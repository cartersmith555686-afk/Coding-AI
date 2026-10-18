# Coding AI

A streaming chat app where you describe the code you want and an AI writes it, like ChatGPT, Gemini or Claude but focused on coding. It runs a small Flask server that forwards your conversation to an LLM API (Anthropic Claude or Google Gemini) with a coding-assistant prompt.

Features: streaming answers, code blocks with a Copy button, follow-up questions and code edits (the conversation is remembered in your browser), a Stop button, and a password gate so strangers can't spend your API credits.

## Style slider

The slider in Settings tunes the temperature and the style instructions sent to the model:

| Slider | Style | Effect |
|---|---|---|
| 0 to 34 | Creative | Higher temperature, suggests alternatives and extras |
| 35 to 70 | Balanced | Default |
| 71 to 100 | Precise | Low temperature, does exactly what you asked, minimal extras |

It does not change the model's built-in safety behavior.

## Configuration (environment variables)

| Variable | Required | Notes |
|---|---|---|
| `ACCESS_PASSWORD` | yes | Password the web UI asks for. Chat is disabled without it. |
| `ANTHROPIC_API_KEY` | one of these | Uses Claude. Model via `CLAUDE_MODEL` (default `claude-sonnet-5-5`). |
| `GEMINI_API_KEY` | one of these | Uses Gemini. Model via `GEMINI_MODEL` (default `gemini-flash-latest`). If both keys are set, Claude is used. |
| `MAX_OUTPUT_TOKENS` | no | Default 4096. |
| `RATE_LIMIT_PER_MIN` | no | Default 30 requests per IP per minute. |

Never commit API keys. Set them in your host's dashboard.

## Run locally

```bash
pip install -r requirements.txt
export ACCESS_PASSWORD=choose-one
export GEMINI_API_KEY=...        # or ANTHROPIC_API_KEY
python app.py                    # http://localhost:5000
python -m unittest -v            # tests (no API key needed)
```

## Deploy on Render

`render.yaml` is included. Create the service (or Blueprint), then open the service's **Environment** tab and add `ACCESS_PASSWORD` (Render can generate it) and one API key. Free-tier services sleep when idle, so the first visit after a while takes about 30 seconds.
