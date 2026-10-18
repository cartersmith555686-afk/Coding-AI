"""Coding AI: a small pattern-based code generator with a strictness slider.

The model is a character-level n-gram (Markov) model with backoff, trained once
at startup on the bundled corpus.txt. It can only recombine patterns found in
that file; it is not a large language model.
"""
import os
import random
from collections import Counter, defaultdict

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORPUS_PATH = os.path.join(BASE_DIR, "corpus.txt")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # reject oversized request bodies

ORDER = 4                  # longest context (in characters) the model looks at
MAX_PROMPT_CHARS = 2_000
DEFAULT_OUTPUT_CHARS = 180
MAX_OUTPUT_CHARS = 600


# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------
def build_model(text):
    """Count which character follows each context of length 1..ORDER."""
    tables = {k: defaultdict(Counter) for k in range(1, ORDER + 1)}
    for k in range(1, ORDER + 1):
        table = tables[k]
        for i in range(len(text) - k):
            table[text[i:i + k]][text[i + k]] += 1
    return {"tables": tables, "text": text}


def load_corpus():
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


MODEL = build_model(load_corpus())


def lookup(model, buf):
    """Longest matching context (with backoff). Returns (order, counter) or (0, None)."""
    for k in range(min(ORDER, len(buf)), 0, -1):
        counter = model["tables"][k].get(buf[-k:])
        if counter:
            return k, counter
    return 0, None


def random_start(model):
    text = model["text"]
    i = random.randrange(max(1, len(text) - ORDER))
    return text[i:i + ORDER]


def strictness_settings(strictness):
    """Map the 0-100 slider to sampling behaviour.

    Low  = high temperature, any pattern allowed (creative, can ramble).
    High = low temperature, only the few most likely characters, and it stops
           instead of guessing when the output no longer matches the corpus.
    """
    temperature = 1.6 - 1.4 * (strictness / 100)  # 1.6 -> 0.2
    strict = strictness > 70
    return {
        "temperature": temperature,
        "top_k": 3 if strict else None,
        "min_order": 2 if strict else 1,
        "strict": strict,
    }


def generate_text(model, prompt, strictness, limit):
    cfg = strictness_settings(strictness)
    buf = prompt[-ORDER:] if prompt else random_start(model)
    halted = None

    if lookup(model, buf)[1] is None:
        if cfg["strict"]:
            return "", "Prompt not found in the built-in code sample (strict mode refuses to guess)."
        buf = random_start(model)

    out = []
    for _ in range(limit):
        order, counter = lookup(model, buf)
        if counter is None:
            halted = "Reached a pattern with no continuation in the code sample."
            break
        if len(buf) >= 2 and order < cfg["min_order"]:
            halted = "Stopped: output drifted away from patterns in the code sample."
            break

        items = counter.most_common(cfg["top_k"]) if cfg["top_k"] else list(counter.items())
        chars = [c for c, _ in items]
        weights = [n ** (1.0 / cfg["temperature"]) for _, n in items]
        ch = random.choices(chars, weights=weights)[0]
        out.append(ch)
        buf = (buf + ch)[-ORDER:]

    return "".join(out), halted


def to_int(value, default, lo, hi):
    """Parse anything into an int clamped to [lo, hi]; fall back to default."""
    try:
        number = int(float(value))
    except (TypeError, ValueError, OverflowError):
        return default
    return max(lo, min(hi, number))


def error(message, status=400):
    return jsonify({"status": "error", "message": message}), status


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/health")
def health():
    return "ok"


@app.errorhandler(413)
def too_large(_e):
    return error("Request too large.", 413)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Send a JSON body.")

    prompt = str(data.get("prompt") or "")[:MAX_PROMPT_CHARS].strip()
    strictness = to_int(data.get("strictness"), 50, 0, 100)
    limit = to_int(data.get("max_chars"), DEFAULT_OUTPUT_CHARS, 1, MAX_OUTPUT_CHARS)

    output, halted = generate_text(MODEL, prompt, strictness, limit)
    return jsonify({"status": "success", "output": output, "halted": halted})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
