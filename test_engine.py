import re
import unittest

import engine

# (what a person might type, expected template, expected language or None)
PHRASES = [
    ("write a python function that reverses a string", "reverse_string", "python"),
    ("reverse a string in javascript", "reverse_string", "javascript"),
    ("fizzbuzz up to 30 in javascript", "fizzbuzz", "javascript"),
    ("first 15 fibonacci numbers", "fibonacci", "python"),
    ("check if a number is prime", "is_prime", None),
    ("is this word a palindrome", "palindrome", None),
    ("flask api on port 8080", "http_server", "python"),
    ("express server", "http_server", "javascript"),
    ("make a discord bot with a /hello command", "discord_slash_command", None),
    ("discord.py bot with a slash command", "discord_slash_command", "python"),
    ("sql table called orders", "sql_table", "sql"),
    ("python script to rename files to lowercase", "rename_files_lowercase", "python"),
    ("bash script to rename files to lowercase", "rename_files_lowercase", "bash"),
    ("scrape links from a website", "web_scraper", "python"),
    ("convert data.csv to json", "csv_to_json", None),
    ("todo list web page", "todo_app", "html"),
    ("pricing page", "pricing_table", "html"),
    ("countdown to 2027-05-01", "countdown_timer", "html"),
    ("hello world", "hello_world", None),
    ("sort a list of numbers", "sort_list", None),
    ("binary search in python", "binary_search", "python"),
    ("rest api with crud for todos", "crud_api", None),
    ("generate a secure password of length 20", "password_generator", None),
    ("count the words in a text", "word_count", None),
    ("fetch json from https://api.example.com/data", "fetch_api", None),
    ("welcome new members in discord", "discord_welcome", None),
    ("dockerfile for my node app", "dockerfile_node", "dockerfile"),
    ("dockerfile for a python flask app", "dockerfile_python", "dockerfile"),
    ("back up a folder", "backup_folder", None),
    ("retry a request 5 times with backoff", "retry_backoff", None),
    ("debounce a search input", "debounce_throttle", "javascript"),
    ("write unit tests", "unit_tests", None),
    ("celsius to fahrenheit converter", "temperature_converter", None),
    ("calculator in javascript", "calculator", "javascript"),
    ("validate an email address", "email_validation", None),
    ("counter with increment and decrement buttons", "counter_button", "html"),
    ("responsive navbar", "navbar", "html"),
    ("login form with validation", "login_form", "html"),
    ("read and write a json file", "read_json_file", None),
]


def code_blocks(text):
    return re.findall(r"```[a-z]*\n(.*?)```", text, re.S)


class MatchingTests(unittest.TestCase):
    def test_phrases_pick_the_right_template(self):
        for prompt, expected, lang in PHRASES:
            for strictness in (20, 50, 90):
                r = engine.respond(prompt, strictness)
                self.assertEqual(r["template"], expected, f"{prompt!r} @ {strictness}")
                if lang:
                    self.assertEqual(r["language"], lang, f"{prompt!r} @ {strictness}")

    def test_unknown_requests_are_declined_honestly(self):
        for prompt in ("make me a 3d racing game", "write a compiler for a new language", "asdf qwerty"):
            r = engine.respond(prompt, 50)
            self.assertIsNone(r["template"], prompt)
            self.assertIn("what I can build", r["text"] + "what I can build")  # reply lists the options
            self.assertNotIn("```", r["text"], prompt)

    def test_empty_and_garbage_input(self):
        self.assertIsNone(engine.respond("", 50)["template"])
        self.assertIsNone(engine.respond("   ", 50)["template"])
        self.assertIsNone(engine.respond(None, 50)["template"])
        engine.respond("x" * 50000, 50)
        engine.respond("fizzbuzz", "not a number")
        engine.respond("fizzbuzz", 10**9)
        engine.respond("fizzbuzz", -5)

    def test_help_lists_areas_and_help_topic_lists_titles(self):
        text = engine.respond("help", 50)["text"]
        for category in engine.categories():
            self.assertIn(category, text)
        for category, titles in engine.categories().items():
            topic = engine.respond(f"help {category}", 50)["text"]
            for title in titles:
                self.assertIn(title, topic, category)

    def test_registered_phrases_route_correctly(self):
        for prompt, tid, lang in engine.PHRASES:
            r = engine.respond(prompt, 50)
            self.assertEqual(r["template"], tid, prompt)
            if lang:
                self.assertEqual(r["language"], lang, prompt)


class StrictnessTests(unittest.TestCase):
    def test_weak_match_is_a_guess_when_creative_and_declined_when_precise(self):
        creative = engine.respond("make a list", 10)
        self.assertEqual(creative["template"], "todo_app")
        self.assertIn("low-confidence", creative["text"])
        self.assertIsNone(engine.respond("make a list", 50)["template"])
        self.assertIsNone(engine.respond("make a list", 95)["template"])

    def test_creative_shows_every_language_balanced_shows_one(self):
        creative = engine.respond("fizzbuzz", 10)["text"]
        self.assertEqual(len(code_blocks(creative)), 2)
        self.assertIn("Related", engine.respond("sort a list", 10)["text"])
        balanced = engine.respond("fizzbuzz", 50)["text"]
        self.assertEqual(len(code_blocks(balanced)), 1)

    def test_precise_uses_validated_code_and_lists_assumptions(self):
        precise = engine.respond("factorial", 95)["text"]
        self.assertIn("non-negative integer", precise)
        self.assertIn("Assumptions", precise)
        self.assertNotIn("non-negative integer", engine.respond("factorial", 50)["text"])

    def test_slider_changes_how_much_confidence_is_needed(self):
        self.assertLess(engine.threshold(0), engine.threshold(50))
        self.assertLess(engine.threshold(50), engine.threshold(100))
        self.assertEqual([engine.mode_for(s) for s in (0, 34, 35, 70, 71, 100)],
                         ["creative", "creative", "balanced", "balanced", "precise", "precise"])


class SlotTests(unittest.TestCase):
    def test_details_from_the_prompt_end_up_in_the_code(self):
        self.assertIn("8080", engine.respond("flask api on port 8080", 50)["text"])
        self.assertIn("fizzbuzz(30)", engine.respond("fizzbuzz up to 30", 50)["text"])
        self.assertIn('"hello"', engine.respond("discord bot with a /hello command", 50)["text"])
        self.assertIn("orders", engine.respond("sql table called orders", 50)["text"])
        self.assertIn('"greetings"', engine.respond("welcome new members in discord #greetings", 50)["text"])
        self.assertIn("/tasks", engine.respond("rest api for tasks on port 9000", 50)["text"])
        self.assertIn("9000", engine.respond("rest api for tasks on port 9000", 50)["text"])
        self.assertIn("https://example.org/a", engine.respond("fetch json from https://example.org/a", 50)["text"])
        self.assertIn("2028-12-25", engine.respond("countdown to 2028-12-25", 50)["text"])
        self.assertIn("data/in.csv", engine.respond("convert data/in.csv to json", 50)["text"])

    def test_primes_up_to_n_includes_n(self):
        self.assertIn("101 + 1", engine.respond("primes up to 101", 50)["text"])

    def test_back_up_is_understood_as_backup(self):
        self.assertEqual(engine.respond("back up my files", 50)["template"], "backup_folder")

    def test_hostile_text_cannot_inject_code(self):
        attacks = [
            'discord bot "x"); import os; os.system("id") #"',
            'discord bot saying "$(rm -rf ~) `id` ${process.env.TOKEN}"',
            'hello world "</h1><script>alert(1)</script>"',
            "discord bot called x\"); process.exit(); //",
            "sql table called users; DROP TABLE users;--",
            "fetch json from https://evil.example/\"+require('child_process')+\"",
            "convert ../../etc/passwd.csv to json",
            "flask api on port 99999999",
        ]
        for prompt in attacks:
            for strictness in (10, 50, 90):
                text = engine.respond(prompt, strictness)["text"]
                for banned in ("os.system", "$(rm", "`id`", "${process", "<script>", "child_process",
                               "DROP TABLE", "../", "99999999"):
                    self.assertNotIn(banned, text, f"{prompt!r} leaked {banned!r}")


class FollowUpTests(unittest.TestCase):
    def test_now_in_another_language(self):
        r = engine.respond("now in javascript", 50, ["fizzbuzz up to 30"])
        self.assertEqual(r["template"], "fizzbuzz")
        self.assertEqual(r["language"], "javascript")
        self.assertIn("fizzbuzz(30)", r["text"])

    def test_follow_up_without_history_is_not_a_crash(self):
        self.assertIsNone(engine.respond("now in javascript", 50, [])["template"])

    def test_missing_language_is_explained(self):
        r = engine.respond("fizzbuzz in sql", 50)
        self.assertEqual(r["template"], "fizzbuzz")
        self.assertIn("don't have", r["text"])
        r = engine.respond("fizzbuzz in rust", 50)
        self.assertIn("Rust", r["text"])


if __name__ == "__main__":
    unittest.main()
