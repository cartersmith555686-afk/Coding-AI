import unittest
from unittest import mock

import app as backend


class AppTests(unittest.TestCase):
    def setUp(self):
        backend._hits.clear()
        self.c = backend.app.test_client()

    def chat(self, body):
        return self.c.post("/api/chat", json=body)

    def test_home_health_status(self):
        r = self.c.get("/")
        self.assertEqual(r.status_code, 200)
        r.close()
        self.assertEqual(self.c.get("/health").data, b"ok")
        data = self.c.get("/api/status").get_json()
        self.assertEqual(data["engine"], "custom")
        self.assertGreater(data["templates"], 30)

    def test_chat_returns_code(self):
        r = self.chat({"message": "fizzbuzz up to 30", "strictness": 50})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["template"], "fizzbuzz")
        self.assertIn("```python", data["reply"])
        self.assertEqual(data["language"], "python")
        self.assertEqual(data["languages"][:2], ["python", "javascript"])

    def test_works_without_any_api_key_or_password(self):
        for var in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "ACCESS_PASSWORD"):
            self.assertFalse(hasattr(backend, var), f"app should not depend on {var}")
        self.assertEqual(self.chat({"message": "hello world"}).status_code, 200)

    def test_follow_up_uses_previous_prompts(self):
        r = self.chat({"message": "now in javascript", "previous": ["fizzbuzz up to 30"]}).get_json()
        self.assertEqual(r["language"], "javascript")

    def test_strictness_is_applied_and_sanitised(self):
        weak = {"message": "make a list"}
        self.assertEqual(self.chat({**weak, "strictness": 10}).get_json()["template"], "todo_app")
        self.assertIsNone(self.chat({**weak, "strictness": 90}).get_json()["template"])
        for bad in ("abc", None, float("nan"), 10**9, -5, [], {}):
            self.assertEqual(self.chat({**weak, "strictness": bad}).status_code, 200, bad)

    def test_get_endpoint_for_quick_checks(self):
        r = self.c.get("/api/chat", query_string={"message": "reverse a string in javascript"})
        self.assertEqual(r.get_json()["language"], "javascript")

    def test_bad_requests_get_json_errors(self):
        self.assertEqual(self.c.post("/api/chat", data="nope").status_code, 400)
        self.assertEqual(self.c.post("/api/chat", data="nope").get_json()["status"], "error")
        for body in ({}, {"message": ""}, {"message": "   "}, {"message": 5}, {"message": ["x"]}, [1]):
            r = self.chat(body)
            self.assertEqual(r.status_code, 400, body)
            self.assertEqual(r.get_json()["status"], "error")
        self.assertEqual(self.chat({"message": "x" * 5000}).status_code, 400)
        self.assertEqual(self.chat({"message": "x" * 40000}).status_code, 413)

    def test_previous_is_cleaned(self):
        r = self.chat({"message": "fizzbuzz", "previous": "not a list"})
        self.assertEqual(r.status_code, 200)
        r = self.chat({"message": "fizzbuzz", "previous": [1, None, {"a": 1}, "ok"] + ["x"] * 50})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(backend.clean_previous(["a", "b", "c", "d", "e"]), ["c", "d", "e"])

    def test_rate_limit(self):
        with mock.patch.object(backend, "RATE_LIMIT_PER_MIN", 3):
            codes = [self.chat({"message": "fizzbuzz"}).status_code for _ in range(5)]
        self.assertEqual(codes, [200, 200, 200, 429, 429])

    def test_rate_limit_cannot_be_dodged_with_fake_forwarded_for(self):
        with mock.patch.object(backend, "RATE_LIMIT_PER_MIN", 3):
            codes = []
            for i in range(6):
                # The client invents a new first entry each time; the proxy's own entry stays 9.9.9.9
                headers = {"X-Forwarded-For": f"10.0.0.{i}, 9.9.9.9"}
                codes.append(self.c.post("/api/chat", json={"message": "fizzbuzz"}, headers=headers).status_code)
        self.assertEqual(codes[:3], [200, 200, 200])
        self.assertEqual(set(codes[3:]), {429})

    def test_different_visitors_have_separate_limits(self):
        with mock.patch.object(backend, "RATE_LIMIT_PER_MIN", 1):
            a = self.c.post("/api/chat", json={"message": "fizzbuzz"}, headers={"X-Forwarded-For": "1.1.1.1"})
            b = self.c.post("/api/chat", json={"message": "fizzbuzz"}, headers={"X-Forwarded-For": "2.2.2.2"})
        self.assertEqual((a.status_code, b.status_code), (200, 200))


if __name__ == "__main__":
    unittest.main()
