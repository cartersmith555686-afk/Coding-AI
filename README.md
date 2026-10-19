# Coding AI

A chat where you describe the code you want and get it back. It is **completely custom**: no LLM, no outside AI service, no API keys. Everything runs inside one small Flask app.

## How it works

`engine.py` is a hand-built, rule-based code generator:

1. **Match**: your description is tokenized and every template is scored by weighted keywords.
2. **Language**: it looks for a language word (Python, JavaScript, Bash, SQL, HTML, Dockerfile...).
3. **Details**: it pulls slots out of your prompt (port numbers, names, `/commands`, URLs, file names, dates, `#channels`).
4. **Fill**: it fills the matching hand-written template and returns it.

It only knows the tasks in its library (see `templates_*.py` and `tpl_*.py`; type `help` in the chat for the areas, `help roblox` for one area). C# code is only bracket-checked (no C# compiler here) and Roblox/Lua code is only compile-checked, never run in Roblox Studio. Prompts it could not match are logged (first 200 chars) so you can see what to add next. It cannot invent code for tasks it has no template for, and it says so instead of guessing. To teach it something new, add a template.

## Style slider

The slider controls how sure the engine must be before it answers and how much it shows:

| Slider | Mode | Behavior |
|---|---|---|
| 0 to 34 | Creative | Answers even on weak matches (flagged as low confidence), shows every language, suggests related templates |
| 35 to 70 | Balanced | Needs a reasonable match, shows one language |
| 71 to 100 | Precise | Needs a strong match, uses the validated version (input checks) where one exists, lists the assumptions it made |

## Adding a template

Add an entry to a module (see `tplkit.py` for the module format; new modules go in `EXTRA_MODULES` in `engine.py`; check one with `python check_module.py tpl_roblox`):

```python
add(
    "my_task", "Title shown to the user",
    {"keyword": 5, "another": 3},          # words that should trigger it, with weights
    python=(code, precise_code_or_None, "how to run it"),
    javascript=(code, None, "node thing.js"),
)
```

Slots in the code look like `__NUMBER|10__` (value from the prompt, default 10). Available slots: `NUMBER`, `NUMBER2`, `NAME`, `PORT`, `URL`, `REPLY`, `COMMAND`, `CHANNEL`, `ROUTE`, `TABLE`, `FILE`, `DATE`. Then run the tests: they syntax-check every template and actually execute the self-contained Python and Node ones.

## Safety

Text from the prompt that ends up inside generated code is restricted (identifiers only, quotes, `$`, backticks and `<>` stripped from messages, no path traversal), and tests try to inject code through the prompt. The page renders replies as plain text, never as HTML.

## Run locally

```bash
pip install -r requirements.txt
python app.py                    # http://localhost:5000
python -m unittest -v            # needs Node.js to check the JavaScript templates
```

Quick check without the page: `curl "localhost:5000/api/chat?message=fizzbuzz+in+javascript"`

## Deploy on Render

`render.yaml` is included: create a Blueprint from this repo, or a Python web service with build `pip install -r requirements.txt` and start `gunicorn app:app --workers 2 --threads 4 --bind 0.0.0.0:$PORT`. No environment variables are needed. Free-tier services sleep when idle, so the first visit after a while takes about 30 seconds.
