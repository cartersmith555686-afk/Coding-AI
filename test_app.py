import time
import unittest

import app as backend


class CodingAITests(unittest.TestCase):
    def setUp(self):
        self.c = backend.app.test_client()

    def gen(self, **kw):
        return self.c.post("/generate", json=kw)

    def test_generates_without_any_setup(self):
        r = self.gen(prompt="function", strictness=50)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["output"])

    def test_empty_prompt_still_works(self):
        self.assertEqual(self.gen(prompt="").status_code, 200)

    def test_bad_content_type_is_json_error_not_415(self):
        r = self.c.post("/generate", data="nope")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["status"], "error")

    def test_bad_strictness_values_do_not_crash(self):
        for bad in ("abc", None, float("nan"), 10**9, -5, [], {}):
            r = self.gen(prompt="fun", strictness=bad)
            self.assertEqual(r.status_code, 200, bad)

    def test_prompt_is_used_as_seed(self):
        valid = set(backend.MODEL["tables"][4]["tion"])
        for _ in range(20):
            out = self.gen(prompt="function", strictness=100, max_chars=3).get_json()["output"]
            self.assertIn(out[0], valid)

    def test_max_strict_does_not_always_halt(self):
        halts = sum(1 for _ in range(30) if self.gen(prompt="f", strictness=100).get_json()["halted"])
        self.assertLess(halts, 30)

    def test_strict_refuses_unknown_prompt(self):
        r = self.gen(prompt="~~~~", strictness=100).get_json()
        self.assertEqual(r["output"], "")
        self.assertTrue(r["halted"])

    def test_loose_mode_falls_back_for_unknown_prompt(self):
        r = self.gen(prompt="~~~~", strictness=10).get_json()
        self.assertTrue(r["output"])

    def test_training_endpoint_removed(self):
        self.assertEqual(self.c.post("/train", json={}).status_code, 404)

    def test_oversized_body_rejected(self):
        r = self.gen(prompt="x" * (70 * 1024))
        self.assertEqual(r.status_code, 413)

    def test_generation_is_fast(self):
        start = time.time()
        for _ in range(20):
            self.gen(prompt="f", strictness=50)
        self.assertLess(time.time() - start, 2.0)

    def test_home_and_health(self):
        self.assertEqual(self.c.get("/").status_code, 200)
        self.assertEqual(self.c.get("/health").data, b"ok")


if __name__ == "__main__":
    unittest.main()
