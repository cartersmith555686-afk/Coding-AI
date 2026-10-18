"""Coding AI: a streaming chat app that writes code from your descriptions.

It forwards your conversation to an LLM API (Anthropic Claude or Google Gemini,
whichever API key you configure) with a coding-assistant system prompt, and
streams the answer back. The "strictness" slider tunes temperature and style
(creative <-> precise); it does not change the model's built-in safety behavior.

Environment variables
  ACCESS_PASSWORD     required. Password the web UI asks for (protects your API bill)
  ANTHROPIC_API_KEY   use Claude          (model: CLAUDE_MODEL, default claude-sonnet-5-5)
  GEMINI_API_KEY      use Gemini instead  (model: GEMINI_MODEL, default gemini-flash-latest)
  MAX_OUTPUT_TOKENS   default 4096
  RATE_LIMIT_PER_MIN  default 30 requests per IP per minute
"""
import hmac
import json
import logging
import os
import threading
import time
from collections import defaultdict, deque

import requests
from flask import Flask, Response, jsonify, request, send_from_directory, stream_with_context

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log = logging.getLogger("coding-ai")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024

ACCESS_PASSWORD = os.environ.get("ACCESS_PASSWORD", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
MAX_OUTPUT_TOKENS = int(os.environ.get("MAX_OUTPUT_TOKENS", "4096"))
RATE_LIMIT_PER_MIN = int(os.environ.get("RATE_LIMIT_PER_MIN", "30"))

MAX_MESSAGES = 40
MAX_MESSAGE_CHARS = 20_000
MAX_TOTAL_CHARS = 60_000


# --------------------------------------------------------------------------
# Prompting
# --------------------------------------------------------------------------
BASE_PROMPT = """You are Coding AI, an expert software engineer and pair programmer.

The user describes what they want; you write the code. Guidelines:
- Produce complete, working, idiomatic code, not fragments or pseudo-code, unless asked.
- Put all code in fenced markdown blocks tagged with the language (```python, ```js, ...).
- Give a one or two sentence summary first, then the code, then brief notes on how to run it or anything important.
- If the request is ambiguous in a way that would change the code a lot, ask one short clarifying question; otherwise make sensible assumptions and state them.
- When fixing or changing code the user pasted, show the full updated code or a clear diff, and explain what was wrong.
- Never invent library APIs. Prefer well-known, maintained libraries and the standard library.
- Be honest about uncertainty and about anything you could not verify."""

STYLE = {
    "creative": "Style: be exploratory. Where it helps, mention an alternative approach or a nice extra, and favor expressive, modern solutions.",
    "balanced": "Style: balanced. Solve what was asked clearly, with brief notes only where they help.",
    "precise": "Style: be precise and minimal. Do exactly what was asked, with no extra features. Keep prose short and prefer the most conventional approach.",
}


def style_for(strictness):
    if strictness < 35:
        return "creative"
    if strictness <= 70:
        return "balanced"
    return "precise"


def system_prompt(strictness):
    return f"{BASE_PROMPT}\n\n{STYLE[style_for(strictness)]}"


def temperature_for(strictness):
    """0 (creative) -> 1.0, 100 (precise) -> 0.1."""
    return round(1.0 - 0.9 * (strictness / 100), 2)


# --------------------------------------------------------------------------
# Providers (each yields text chunks)
# --------------------------------------------------------------------------
class ProviderError(Exception):
    pass


def stream_anthropic(system, messages, temperature):
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    base = dict(model=CLAUDE_MODEL, max_tokens=MAX_OUTPUT_TOKENS, system=system, messages=messages)
    # Some models reject a temperature value; if so, retry once without it.
    for temp in (temperature, None):
        kwargs = dict(base)
        if temp is not None:
            kwargs["temperature"] = temp
        started = False
        try:
            with client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    started = True
                    yield text
            return
        except anthropic.BadRequestError as e:
            if started or temp is None or "temperature" not in str(e).lower():
                raise


def stream_gemini(system, messages, temperature):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:streamGenerateContent?alt=sse"
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [
            {"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]}
            for m in messages
        ],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": MAX_OUTPUT_TOKENS},
    }
    headers = {"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"}
    with requests.post(url, json=body, headers=headers, stream=True, timeout=(10, 120)) as r:
        if r.status_code != 200:
            try:
                detail = r.json().get("error", {}).get("message", "")
            except Exception:
                detail = ""
            raise ProviderError(f"Gemini API error {r.status_code}: {detail or 'request failed'}")
        r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            try:
                chunk = json.loads(line[5:].strip())
            except ValueError:
                continue
            for cand in chunk.get("candidates", []):
                for part in cand.get("content", {}).get("parts", []):
                    if part.get("text"):
                        yield part["text"]


PROVIDERS = {"anthropic": stream_anthropic, "gemini": stream_gemini}


def active_provider():
    if ANTHROPIC_API_KEY:
        return "anthropic"
    if GEMINI_API_KEY:
        return "gemini"
    return None


def model_label(provider):
    return {"anthropic": CLAUDE_MODEL, "gemini": GEMINI_MODEL}.get(provider)


# --------------------------------------------------------------------------
# Security: rate limit + password
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


def error(message, status=400):
    return jsonify({"status": "error", "message": message}), status


def check_access():
    """Returns an error response, or None if the request may proceed."""
    if rate_limited(client_ip()):
        return error("Too many requests. Slow down a little.", 429)
    if not ACCESS_PASSWORD:
        return error("Server not configured: set the ACCESS_PASSWORD environment variable.", 503)
    given = request.headers.get("X-Access-Key", "")
    if not hmac.compare_digest(given.encode(), ACCESS_PASSWORD.encode()):
        return error("Wrong password.", 401)
    return None


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


@app.route("/api/status")
def status():
    denied = check_access()
    if denied:
        return denied
    provider = active_provider()
    return jsonify({"status": "success", "provider": provider, "model": model_label(provider)})


def clean_messages(raw):
    if not isinstance(raw, list) or not raw:
        return None, "Send a non-empty messages list."
    if len(raw) > MAX_MESSAGES:
        raw = raw[-MAX_MESSAGES:]
    out, total = [], 0
    for m in raw:
        if not isinstance(m, dict) or m.get("role") not in ("user", "assistant"):
            return None, "Each message needs a role of 'user' or 'assistant'."
        content = m.get("content")
        if not isinstance(content, str) or not content.strip():
            return None, "Messages must have non-empty text."
        if len(content) > MAX_MESSAGE_CHARS:
            return None, f"A message is too long (max {MAX_MESSAGE_CHARS:,} characters)."
        total += len(content)
        out.append({"role": m["role"], "content": content})
    if total > MAX_TOTAL_CHARS:
        return None, "Conversation too long. Start a new chat."
    while out and out[0]["role"] != "user":
        out.pop(0)
    if not out or out[-1]["role"] != "user":
        return None, "The last message must be from the user."
    return out, None


def to_int(value, default, lo, hi):
    try:
        number = int(float(value))
    except (TypeError, ValueError, OverflowError):
        return default
    return max(lo, min(hi, number))


@app.route("/api/chat", methods=["POST"])
def chat():
    denied = check_access()
    if denied:
        return denied

    provider = active_provider()
    if not provider:
        return error("No API key configured. Add ANTHROPIC_API_KEY or GEMINI_API_KEY in the server settings.", 503)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Send a JSON body.")
    messages, problem = clean_messages(data.get("messages"))
    if problem:
        return error(problem)

    strictness = to_int(data.get("strictness"), 50, 0, 100)
    system = system_prompt(strictness)
    temperature = temperature_for(strictness)
    streamer = PROVIDERS[provider]

    def generate():
        try:
            yield from streamer(system, messages, temperature)
        except Exception as e:  # surface a readable error inside the chat
            log.exception("provider error")
            detail = str(e).strip().splitlines()[0][:300] if str(e).strip() else e.__class__.__name__
            yield f"\n\n[Error: {detail}]"

    return Response(
        stream_with_context(generate()),
        mimetype="text/plain",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
