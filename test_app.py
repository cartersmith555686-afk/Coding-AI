import sys
import types
import unittest
from unittest import mock

import app as backend

PW = "secret-pw"
HDR = {"X-Access-Key": PW}
MSGS = [{"role": "user", "content": "write hello world in python"}]


def fake_streamer(chunks):
    calls = []

    def streamer(system, messages, temperature):
        calls.append({"system": system, "messages": messages, "temperature": temperature})
        for c in chunks:
            yield c

    streamer.calls = calls
    return streamer


class ChatTests(unittest.TestCase):
    def setUp(self):
        backend._hits.clear()
        self.patches = [
            mock.patch.object(backend, "ACCESS_PASSWORD", PW),
            mock.patch.object(backend, "ANTHROPIC_API_KEY", "k"),
            mock.patch.object(backend, "GEMINI_API_KEY", ""),
        ]
        for p in self.patches:
            p.start()
        self.streamer = fake_streamer(["Here ", "you go:\n```python\n", "print('hi')\n```"])
        p = mock.patch.dict(backend.PROVIDERS, {"anthropic": self.streamer})
        p.start()
        self.patches.append(p)
        self.c = backend.app.test_client()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def chat(self, body=None, headers=HDR):
        return self.c.post("/api/chat", json=body if body is not None else {"messages": MSGS}, headers=headers)

    # ---- access control ----
    def test_requires_password_configured(self):
        with mock.patch.object(backend, "ACCESS_PASSWORD", ""):
            self.assertEqual(self.chat().status_code, 503)

    def test_wrong_or_missing_password(self):
        self.assertEqual(self.chat(headers={"X-Access-Key": "nope"}).status_code, 401)
        self.assertEqual(self.chat(headers={}).status_code, 401)

    def test_no_api_key_configured(self):
        with mock.patch.object(backend, "ANTHROPIC_API_KEY", ""):
            r = self.chat()
            self.assertEqual(r.status_code, 503)
            self.assertIn("API key", r.get_json()["message"])

    def test_rate_limit_cannot_be_dodged_with_fake_forwarded_for(self):
        with mock.patch.object(backend, "RATE_LIMIT_PER_MIN", 3):
            codes = []
            for i in range(6):
                # The client invents a new first entry each time; the proxy's own entry stays 9.9.9.9
                headers = dict(HDR, **{"X-Forwarded-For": f"10.0.0.{i}, 9.9.9.9"})
                codes.append(self.chat(headers=headers).status_code)
            self.assertEqual(codes[:3], [200, 200, 200])
            self.assertEqual(set(codes[3:]), {429})

    def test_rate_limit(self):
        with mock.patch.object(backend, "RATE_LIMIT_PER_MIN", 3):
            codes = [self.chat().status_code for _ in range(5)]
        self.assertEqual(codes, [200, 200, 200, 429, 429])

    def test_status_endpoint(self):
        self.assertEqual(self.c.get("/api/status").status_code, 401)
        r = self.c.get("/api/status", headers=HDR).get_json()
        self.assertEqual(r["provider"], "anthropic")

    # ---- validation ----
    def test_rejects_bad_bodies(self):
        bad = [
            {"messages": []},
            {"messages": "hi"},
            {"messages": [{"role": "system", "content": "x"}]},
            {"messages": [{"role": "user", "content": "   "}]},
            {"messages": [{"role": "user", "content": 5}]},
            {"messages": [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]},
            {"messages": [{"role": "user", "content": "x" * (backend.MAX_MESSAGE_CHARS + 1)}]},
            {},
        ]
        for body in bad:
            self.assertEqual(self.chat(body).status_code, 400, body)

    def test_non_json_body(self):
        r = self.c.post("/api/chat", data="nope", headers=HDR)
        self.assertEqual(r.status_code, 400)

    def test_total_size_limit(self):
        big = [{"role": "user" if i % 2 == 0 else "assistant", "content": "x" * 19_000} for i in range(5)]
        self.assertEqual(self.chat({"messages": big}).status_code, 400)

    def test_long_history_is_trimmed_not_rejected(self):
        hist = [{"role": "user" if i % 2 == 0 else "assistant", "content": "hi"} for i in range(60)] + [
            {"role": "user", "content": "last"}
        ]
        self.assertEqual(self.chat({"messages": hist}).status_code, 200)
        sent = self.streamer.calls[-1]["messages"]
        self.assertLessEqual(len(sent), backend.MAX_MESSAGES)
        self.assertEqual(sent[0]["role"], "user")
        self.assertEqual(sent[-1]["content"], "last")

    # ---- behaviour ----
    def test_streams_text(self):
        r = self.chat()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_data(as_text=True), "Here you go:\n```python\nprint('hi')\n```")

    def test_strictness_changes_style_and_temperature(self):
        self.chat({"messages": MSGS, "strictness": 0}).get_data()
        self.chat({"messages": MSGS, "strictness": 100}).get_data()
        low, high = self.streamer.calls[-2], self.streamer.calls[-1]
        self.assertGreater(low["temperature"], high["temperature"])
        self.assertIn("exploratory", low["system"])
        self.assertIn("precise and minimal", high["system"])

    def test_bad_strictness_does_not_crash(self):
        for bad in ("abc", None, float("nan"), 10**9, -5, [], {}):
            self.assertEqual(self.chat({"messages": MSGS, "strictness": bad}).status_code, 200, bad)
        temps = [c["temperature"] for c in self.streamer.calls]
        self.assertTrue(all(0.1 <= t <= 1.0 for t in temps))

    def test_provider_error_is_shown_in_stream(self):
        def boom(system, messages, temperature):
            yield "partial"
            raise RuntimeError("rate limited by provider")

        with mock.patch.dict(backend.PROVIDERS, {"anthropic": boom}):
            text = self.chat().get_data(as_text=True)
        self.assertIn("partial", text)
        self.assertIn("[Error: rate limited by provider]", text)

    def test_home_and_health(self):
        self.assertEqual(self.c.get("/").status_code, 200)
        self.assertEqual(self.c.get("/health").data, b"ok")


class ProviderTests(unittest.TestCase):
    def test_gemini_parses_sse_and_maps_roles(self):
        lines = [
            "",
            'data: {"candidates":[{"content":{"parts":[{"text":"Hel"}]}}]}',
            "data: not-json",
            'data: {"candidates":[{"content":{"parts":[{"text":"lo"}]}}]}',
            'data: {"candidates":[{"finishReason":"STOP"}]}',
        ]

        class FakeResp:
            status_code = 200
            encoding = None

            def iter_lines(self, decode_unicode=False):
                return iter(lines)

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        captured = {}

        def fake_post(url, json=None, headers=None, **kw):
            captured.update(url=url, body=json, headers=headers)
            return FakeResp()

        msgs = [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}, {"role": "user", "content": "c"}]
        with mock.patch.object(backend.requests, "post", fake_post), mock.patch.object(backend, "GEMINI_API_KEY", "g"):
            out = "".join(backend.stream_gemini("SYS", msgs, 0.5))
        self.assertEqual(out, "Hello")
        self.assertEqual([c["role"] for c in captured["body"]["contents"]], ["user", "model", "user"])
        self.assertEqual(captured["body"]["systemInstruction"]["parts"][0]["text"], "SYS")
        self.assertEqual(captured["headers"]["x-goog-api-key"], "g")
        self.assertIn("streamGenerateContent", captured["url"])

    def test_gemini_http_error_raises(self):
        class FakeResp:
            status_code = 429

            def json(self):
                return {"error": {"message": "quota exceeded"}}

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        with mock.patch.object(backend.requests, "post", lambda *a, **k: FakeResp()):
            with self.assertRaises(backend.ProviderError) as cm:
                list(backend.stream_gemini("S", [{"role": "user", "content": "x"}], 0.5))
        self.assertIn("quota exceeded", str(cm.exception))

    def test_anthropic_retries_without_temperature(self):
        class BadRequestError(Exception):
            pass

        seen = []

        class FakeStream:
            def __init__(self, fail):
                self.fail = fail

            def __enter__(self):
                if self.fail:
                    raise BadRequestError("temperature is not supported for this model")
                return self

            def __exit__(self, *a):
                return False

            @property
            def text_stream(self):
                return iter(["ok", "!"])

        class FakeClient:
            def __init__(self, api_key=None):
                self.messages = self

            def stream(self, **kw):
                seen.append(kw)
                return FakeStream(fail="temperature" in kw)

        fake_mod = types.SimpleNamespace(Anthropic=FakeClient, BadRequestError=BadRequestError)
        with mock.patch.dict(sys.modules, {"anthropic": fake_mod}):
            out = "".join(backend.stream_anthropic("S", [{"role": "user", "content": "x"}], 0.3))
        self.assertEqual(out, "ok!")
        self.assertIn("temperature", seen[0])
        self.assertNotIn("temperature", seen[1])


if __name__ == "__main__":
    unittest.main()
