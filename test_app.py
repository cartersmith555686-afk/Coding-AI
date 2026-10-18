import time
import unittest

import app as backend

SID = "test-session-0001"
SID2 = "test-session-0002"


class CodingAITests(unittest.TestCase):
    def setUp(self):
        backend._models.clear()
        self.c = backend.app.test_client()

    def train(self, sid=SID, text="function add(a, b) { return a + b; }\n" * 20):
        return self.c.post("/train", json={"session_id": sid, "dataset_text": text})

    def gen(self, sid=SID, **kw):
        return self.c.post("/generate", json={"session_id": sid, **kw})

    def test_untrained_returns_json_error(self):
        r = self.gen(prompt="x")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["status"], "error")

    def test_bad_content_type_is_json_error_not_415(self):
        r = self.c.post("/train", data="nope")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["status"], "error")

    def test_missing_session_rejected(self):
        r = self.c.post("/train", json={"dataset_text": "hello world"})
        self.assertEqual(r.status_code, 400)

    def test_bad_strictness_values_do_not_crash(self):
        self.train()
        for bad in ("abc", None, float("nan"), 10**9, -5, [], {}):
            r = self.gen(prompt="fun", strictness=bad)
            self.assertEqual(r.status_code, 200, bad)

    def test_sessions_are_isolated(self):
        self.train(SID, "AAAA AAAA AAAA AAAA")
        self.train(SID2, "zzzz zzzz zzzz zzzz")
        out1 = self.gen(SID, prompt="A", strictness=50).get_json()["output"]
        self.assertNotIn("z", out1)

    def test_prompt_is_used_as_seed(self):
        self.train()
        out = self.gen(prompt="function ad", strictness=90, max_chars=6).get_json()["output"]
        self.assertTrue(out.startswith("d("), out)  # "function add(" continues from "ad"

    def test_max_strict_does_not_always_halt(self):
        self.train()
        halts = sum(
            1 for _ in range(30)
            if self.gen(prompt="f", strictness=100).get_json()["halted"]
        )
        self.assertLess(halts, 30)

    def test_strict_refuses_unknown_prompt(self):
        self.train()
        r = self.gen(prompt="~~~~", strictness=100).get_json()
        self.assertEqual(r["output"], "")
        self.assertTrue(r["halted"])

    def test_dataset_size_limit(self):
        r = self.train(text="x" * (backend.MAX_DATASET_CHARS + 1))
        self.assertEqual(r.status_code, 413)

    def test_generation_is_fast_on_large_dataset(self):
        self.train(text="function add(a, b) { return a + b; }\n" * 5000)
        start = time.time()
        self.gen(prompt="f", strictness=50)
        self.assertLess(time.time() - start, 0.5)

    def test_session_cap_evicts_oldest(self):
        for i in range(backend.MAX_SESSIONS + 5):
            self.train(f"session-{i:04d}-abcd")
        self.assertLessEqual(len(backend._models), backend.MAX_SESSIONS)

    def test_home_and_health(self):
        self.assertEqual(self.c.get("/").status_code, 200)
        self.assertEqual(self.c.get("/health").data, b"ok")


if __name__ == "__main__":
    unittest.main()
