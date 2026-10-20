"""Coding AI web app.

Serves the chat page and the custom code-generation engine (engine.py).
There is no outside AI service and no API key: everything runs inside this process.
"""
import os
import threading
import time
from collections import defaultdict, deque

from flask import Flask, jsonify, request, send_from_directory

import engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024

RATE_LIMIT_PER_MIN = int(os.environ.get("RATE_LIMIT_PER_MIN", "60"))
MAX_PREVIOUS = 3


# --------------------------------------------------------------------------
# Rate limiting
# --------------------------------------------------------------------------
_hits = defaultdict(deque)
_hits_lock = threading.Lock()


def client_ip():
    # Use the LAST X-Forwarded-For entry: that is the address our own proxy saw.
    # The first entry is supplied by the client and can be faked to dodge the limit.
    forwarded = request.headers.get("X-Forwarded-For", "")
    return forwarded.split(",")[-1].strip() or request.remote_addr or "unknown"


def rate_limited(ip):
    now = time.time()
    with _hits_lock:
        if len(_hits) > 5000:
            for key in [k for k, q in _hits.items() if not q or now - q[-1] > 60]:
                del _hits[key]
        q = _hits[ip]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= RATE_LIMIT_PER_MIN:
            return True
        q.append(now)
        return False


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def error(message, status=400):
    return jsonify({"status": "error", "message": message}), status


def to_int(value, default, lo, hi):
    try:
        number = int(float(value))
    except (TypeError, ValueError, OverflowError):
        return default
    return max(lo, min(hi, number))


def clean_previous(raw):
    """Earlier user prompts (used for follow-ups like "now in javascript")."""
    if not isinstance(raw, list):
        return []
    out = [item.strip()[: engine.MAX_PROMPT_CHARS] for item in raw if isinstance(item, str) and item.strip()]
    return out[-MAX_PREVIOUS:]


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.after_request
def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/health")
def health():
    return "ok"


@app.errorhandler(413)
def too_large(_e):
    return error("Request too large.", 413)


@app.route("/api/status")
def status():
    return jsonify({"status": "success", "engine": "custom", "templates": len(engine.TEMPLATES)})


@app.route("/api/chat", methods=["GET", "POST"])
def chat():
    if rate_limited(client_ip()):
        return error("Too many requests. Slow down a little.", 429)

    if request.method == "POST":
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error("Send a JSON body.")
    else:  # GET /api/chat?message=...&strictness=50 (handy for quick tests and sharing)
        data = {"message": request.args.get("message", ""), "strictness": request.args.get("strictness")}

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return error("Describe the code you want.")
    message = message.strip()
    if len(message) > engine.MAX_PROMPT_CHARS:
        return error(f"That is too long (max {engine.MAX_PROMPT_CHARS:,} characters).")

    result = engine.respond(
        message,
        to_int(data.get("strictness"), 50, 0, 100),
        clean_previous(data.get("previous")),
    )
    return jsonify({
        "status": "success",
        "reply": result["text"],
        "template": result["template"],
        "confidence": round(result["confidence"], 2),
        "language": result.get("language"),
        "languages": result.get("languages", []),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
