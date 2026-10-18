# Coding AI

A small Flask app with a chat UI that trains a **character-level n-gram (Markov) model** on text you paste in, then continues whatever you type in the style of that text. A **strictness slider** controls how adventurous or conservative the output is.

It is not a large language model: it can only recombine patterns from your dataset, and it cannot follow instructions. For a real coding assistant, call an LLM API instead.

## How it works

- **Training** (`POST /train`): builds counts of which character follows every 1 to 4 character context. Capped at 200,000 characters.
- **Generation** (`POST /generate`): your prompt seeds the model, which then predicts one character at a time, backing off to shorter contexts when needed.
- **Sessions**: each browser gets its own model (a random session id kept in `localStorage`), so visitors don't overwrite each other. The server keeps the 50 most recent sessions in memory.

### Strictness slider

| Slider | Label | Behavior |
|---|---|---|
| 0 to 34 | Unrestricted | High temperature (up to 1.6). Varied, sometimes rambling output. |
| 35 to 70 | Balanced | Medium temperature. Falls back to a random start if your prompt isn't in the data. |
| 71 to 100 | Max Strict | Low temperature (down to 0.2), only the 3 most likely next characters, and it stops with a note instead of guessing when the output drifts from the training data or the prompt isn't found. |

## Run locally

```bash
pip install -r requirements.txt
python app.py          # http://localhost:5000
python -m unittest -v  # run the tests
```

## Deploy on Render

`render.yaml` is included. In Render choose **New > Blueprint**, pick this repo, and deploy. The start command uses `--workers 1` on purpose, because trained models live in memory. Free-tier services sleep when idle and lose trained models on restart, so recompile after a cold start.
