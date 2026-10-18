# Coding AI

A small Flask app with a chat UI. Type the start of some code and a **character-level n-gram (Markov) model** continues it. A **strictness slider** controls how adventurous or conservative the output is.

There is nothing to train or upload: the model is built at startup from the bundled `corpus.txt` (a small sample of JavaScript, Python, HTML, CSS and SQL). To change what it can write, edit that file and redeploy.

It is not a large language model: it can only recombine patterns from `corpus.txt`, and it cannot follow instructions or write genuinely new code. For a real coding assistant, call an LLM API instead.

## How it works

`POST /generate` takes `{"prompt": "...", "strictness": 0-100}`. Your prompt seeds the model, which predicts one character at a time from the last 1 to 4 characters, backing off to shorter contexts when needed.

### Strictness slider

| Slider | Label | Behavior |
|---|---|---|
| 0 to 34 | Unrestricted | High temperature (up to 1.6). Varied, sometimes rambling output. |
| 35 to 70 | Balanced | Medium temperature. Uses a random start if your prompt isn't in the sample. |
| 71 to 100 | Max Strict | Low temperature (down to 0.2), only the 3 most likely next characters, and it stops with a note instead of guessing when output drifts from the sample or the prompt isn't found. |

## Run locally

```bash
pip install -r requirements.txt
python app.py          # http://localhost:5000
python -m unittest -v  # run the tests
```

## Deploy on Render

`render.yaml` is included. In Render choose **New > Blueprint**, pick this repo, and deploy. Free-tier services sleep when idle, so the first visit after a while takes about 30 seconds.
