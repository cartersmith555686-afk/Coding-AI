"""Checks every template in every language: syntax for all, and real execution for the self-contained ones."""
import ast
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser

import engine

# Self-contained programs (no network, servers, bots or third-party packages): these are actually executed.
RUNNABLE = {
    "fizzbuzz", "fibonacci", "is_prime", "palindrome", "reverse_string", "factorial", "password_generator",
    "word_count", "hello_world", "sort_list", "binary_search", "email_validation", "temperature_converter",
    "calculator", "retry_backoff", "debounce_throttle", "unit_tests",
}

# Awkward-but-valid slot values, to prove substitution never breaks the generated code.
TRICKY_SLOTS = {
    "NUMBER": "12", "PORT": "8080", "COMMAND": "my-cmd", "REPLY": "Hi there! It's fine & dandy.",
    "TABLE": "orders", "FILE": "data/in.csv", "URL": "https://example.com/x?y=1&z=2",
    "CHANNEL": "general", "ROUTE": "tasks", "DATE": "2030-02-03T00:00:00",
}

VOID = {"meta", "link", "br", "hr", "img", "input", "area", "base", "col", "embed", "source", "track", "wbr"}


def variants():
    for tpl in engine.TEMPLATES:
        for lang, (base, precise, _run) in tpl["langs"].items():
            yield tpl["id"], lang, "base", base
            if precise:
                yield tpl["id"], lang, "precise", precise


class _Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.scripts, self._in_script = [], [], [], False

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)
        if tag == "script":
            self._in_script = True
            self.scripts.append("")

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_script = False
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}>")
        else:
            self.stack.pop()

    def handle_data(self, data):
        if self._in_script:
            self.scripts[-1] += data


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def run(cmd, cwd, timeout=30):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


class TemplateTests(unittest.TestCase):
    def check_code(self, label, lang, code, execute):
        with tempfile.TemporaryDirectory() as tmp:
            if lang == "python":
                ast.parse(code)
                if execute:
                    path = os.path.join(tmp, "t.py")
                    write(path, code)
                    r = run([sys.executable, path], tmp)
                    self.assertEqual(r.returncode, 0, f"{label}\n{r.stderr}")
            elif lang == "javascript":
                path = os.path.join(tmp, "t.js")
                write(path, code)
                r = run(["node", "--check", path], tmp)
                self.assertEqual(r.returncode, 0, f"{label}\n{r.stderr}")
                if execute:
                    r = run(["node", path], tmp)
                    self.assertEqual(r.returncode, 0, f"{label}\n{r.stderr}")
            elif lang == "bash":
                path = os.path.join(tmp, "t.sh")
                write(path, code)
                r = run(["bash", "-n", path], tmp)
                self.assertEqual(r.returncode, 0, f"{label}\n{r.stderr}")
            elif lang == "sql":
                conn = sqlite3.connect(":memory:")
                try:
                    conn.executescript(code)
                finally:
                    conn.close()
            elif lang == "html":
                parser = _Tags()
                parser.feed(code)
                self.assertEqual(parser.errors, [], label)
                self.assertEqual(parser.stack, [], f"{label}: unclosed {parser.stack}")
                self.assertIn("<!DOCTYPE html>", code)
                for i, script in enumerate(parser.scripts):
                    path = os.path.join(tmp, f"s{i}.js")
                    write(path, script)
                    r = run(["node", "--check", path], tmp)
                    self.assertEqual(r.returncode, 0, f"{label} <script>\n{r.stderr}")
            elif lang == "dockerfile":
                first = next(line for line in code.splitlines() if line.strip() and not line.startswith("#"))
                self.assertTrue(first.startswith("FROM "), label)
            else:
                self.fail(f"no checker for language {lang!r} ({label})")

    def test_every_template_with_defaults(self):
        count = 0
        for tid, lang, kind, code in variants():
            filled, _ = engine.fill(code, {})
            self.assertNotRegex(filled, r"__[A-Z]+(\|.*?)?__", f"{tid}/{lang}: unfilled slot")
            self.check_code(f"{tid}/{lang}/{kind}", lang, filled, tid in RUNNABLE)
            count += 1
        self.assertGreater(count, 60)

    def test_every_template_with_tricky_slot_values(self):
        for tid, lang, kind, code in variants():
            filled, _ = engine.fill(code, TRICKY_SLOTS)
            self.check_code(f"{tid}/{lang}/{kind} (tricky slots)", lang, filled, tid in RUNNABLE)

    def test_templates_are_well_formed(self):
        ids = [t["id"] for t in engine.TEMPLATES]
        self.assertEqual(len(ids), len(set(ids)), "duplicate template ids")
        for tpl in engine.TEMPLATES:
            self.assertTrue(tpl["title"] and tpl["keywords"] and tpl["langs"], tpl["id"])
            for lang, entry in tpl["langs"].items():
                self.assertEqual(len(entry), 3, f"{tpl['id']}/{lang}")
                self.assertIn(lang, engine.LANG_FENCE, f"{tpl['id']}/{lang}")
                self.assertIn(lang, engine.LANG_LABEL, f"{tpl['id']}/{lang}")
                self.assertTrue(entry[0].strip() and entry[2].strip(), f"{tpl['id']}/{lang}")

    def test_primes_include_the_limit(self):
        code = engine.fill(engine.BY_ID["is_prime"]["langs"]["python"][0], {"NUMBER": "13"})[0]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "p.py")
            write(path, code)
            self.assertIn("13]", run([sys.executable, path], tmp).stdout)


if __name__ == "__main__":
    unittest.main()
