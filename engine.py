"""Coding AI engine: a fully custom, rule-based code generator.

No machine learning and no outside AI service. It works in four steps:
  1. tokenize the prompt and score every template by weighted keyword matches
  2. detect the requested language
  3. pull simple details out of the prompt (numbers, ports, names, URLs...) into slots
  4. fill the template and format the answer

The strictness slider (0-100) controls how sure the engine must be before it
answers, and how much it includes:
  creative (<35)  answers even on weak matches, shows every language, suggests related templates
  balanced        answers on reasonable matches, one language
  precise  (>70)  needs a strong match, uses the validated variant, lists its assumptions
"""
import datetime
import re

from templates_basic import TEMPLATES as _BASIC
from templates_web import TEMPLATES as _WEB
from templates_more import TEMPLATES as _MORE

TEMPLATES = _BASIC + _WEB + _MORE
BY_ID = {t["id"]: t for t in TEMPLATES}

MAX_PROMPT_CHARS = 2000
SCORE_FOR_FULL_CONFIDENCE = 6.0

LANG_WORDS = {
    "python": "python", "py": "python", "python3": "python", "flask": "python",
    "discord.py": "python", "discordpy": "python", "requests": "python",
    "beautifulsoup": "python", "bs4": "python",
    "javascript": "javascript", "js": "javascript", "node": "javascript",
    "nodejs": "javascript", "node.js": "javascript", "express": "javascript",
    "discord.js": "javascript", "discordjs": "javascript",
    "bash": "bash", "shell": "bash", "sh": "bash", "terminal": "bash",
    "html": "html", "webpage": "html", "website": "html", "css": "html",
    "sql": "sql", "mysql": "sql", "postgres": "sql", "postgresql": "sql", "sqlite": "sql",
    "docker": "dockerfile", "dockerfile": "dockerfile",
}
LANG_FENCE = {"python": "python", "javascript": "javascript", "bash": "bash", "html": "html", "sql": "sql",
              "dockerfile": "dockerfile"}
LANG_LABEL = {"python": "Python", "javascript": "JavaScript", "bash": "Bash", "html": "HTML/CSS/JS", "sql": "SQL",
              "dockerfile": "Dockerfile"}

HELP_WORDS = {"help", "hello", "hi", "hey", "commands", "capabilities", "menu"}
IDENT_STOPWORDS = {
    "for", "with", "to", "in", "of", "and", "that", "the", "a", "an", "on", "my", "our", "it",
    "sql", "new", "simple", "basic", "create", "make", "database", "users", "table", "this", "from",
    "write", "build", "me", "is", "as", "using", "by",
}


# --------------------------------------------------------------------------
# Step 1: tokenizing and scoring
# --------------------------------------------------------------------------
def tokenize(text):
    text = re.sub(r"\bback[\s-]+up\b", "backup", text.lower())  # "back up" -> "backup"
    tokens = set(re.findall(r"[a-z0-9']+", text))
    for raw in text.split():  # also keep compounds like "discord.js" and "node.js"
        raw = raw.strip(".,!?;:()[]{}\"'")
        if raw:
            tokens.add(raw)
    return tokens


def stems(token):
    out = {token}
    if token.endswith("es") and len(token) > 4:
        out.add(token[:-2])
    if token.endswith("s") and len(token) > 3:
        out.add(token[:-1])
    return out


_QUALIFIER_RE = re.compile(r"\b(?:in|using|with|as|via)\s+([a-z0-9.+#]+)")


def language_qualifiers(prompt):
    """Language words used as qualifiers, like the 'sql' in 'fizzbuzz in sql'."""
    found = set()
    for word in _QUALIFIER_RE.findall(prompt.lower()):
        word = word.strip(".")
        if word in LANG_WORDS or word in UNSUPPORTED_LANGS:
            found |= stems(word)
    return found


def score_templates(prompt):
    """Return [(score, template)] for templates with score > 0, best first."""
    tokens = tokenize(prompt)
    expanded = set()
    for t in tokens:
        expanded |= stems(t)
    qualifiers = language_qualifiers(prompt)
    results = []
    for tpl in TEMPLATES:
        # For most templates the language is just a request ("in sql"); for a few (Dockerfile for
        # Python vs Node) it is part of the topic, so those keep counting it.
        words = expanded if tpl.get("quiet_lang") else expanded - qualifiers
        score = sum(w for kw, w in tpl["keywords"].items() if kw in words)
        if score > 0:
            results.append((float(score), tpl))
    results.sort(key=lambda r: (-r[0], r[1]["id"]))
    return results


def confidence(score):
    return min(1.0, score / SCORE_FOR_FULL_CONFIDENCE)


def threshold(strictness):
    """0 -> 0.10, 50 -> 0.40, 100 -> 0.70"""
    return 0.10 + 0.60 * (strictness / 100.0)


def mode_for(strictness):
    if strictness < 35:
        return "creative"
    if strictness <= 70:
        return "balanced"
    return "precise"


# --------------------------------------------------------------------------
# Step 2: language
# --------------------------------------------------------------------------
UNSUPPORTED_LANGS = {
    "rust": "Rust", "go": "Go", "golang": "Go", "java": "Java", "c": "C", "cpp": "C++", "c++": "C++",
    "c#": "C#", "csharp": "C#", "ruby": "Ruby", "php": "PHP", "swift": "Swift", "kotlin": "Kotlin",
    "typescript": "TypeScript", "ts": "TypeScript", "perl": "Perl", "lua": "Lua", "r": "R",
}


def detect_language(prompt):
    """First supported language mentioned in the prompt, or None."""
    for word in _words(prompt):
        if word in LANG_WORDS:
            return LANG_WORDS[word]
    return None


def detect_unsupported(prompt):
    """Name of a language the user asked for that I have no templates for, or None."""
    words = _words(prompt)
    if detect_language(prompt):
        return None
    for i, word in enumerate(words):
        if word in UNSUPPORTED_LANGS and (len(word) > 2 or (i > 0 and words[i - 1] in ("in", "using", "with"))):
            return UNSUPPORTED_LANGS[word]
    return None


def _words(prompt):
    out = []
    for raw in prompt.lower().split():
        raw = raw.strip(".,!?;:()[]{}\"'")
        if raw:
            out.append(raw)
            squashed = re.sub(r"[^a-z0-9+#]", "", raw)
            if squashed != raw and squashed:
                out.append(squashed)
    return out


# --------------------------------------------------------------------------
# Step 3: slots
# --------------------------------------------------------------------------
def _clean_text(value, limit=80):
    """Keep user text safe to place inside a double-quoted string in generated code."""
    value = re.sub(r'["\\`\r\n\t$<>]', "", value)
    return value.strip()[:limit]


def _identifier(candidate):
    candidate = candidate.lower()
    if candidate in IDENT_STOPWORDS:
        return None
    return candidate if re.fullmatch(r"[a-z_][a-z0-9_]{0,40}", candidate) else None


def extract_slots(prompt, template_id):
    slots = {}
    text = prompt

    m = re.search(r"\bport\s*(?:number\s*)?:?\s*(\d{2,5})\b", text, re.I)
    if m and 1 <= int(m.group(1)) <= 65535:
        slots["PORT"] = m.group(1)

    # NUMBER: first standalone integer that isn't the port
    for m in re.finditer(r"(?<![\w.])(\d{1,6})(?![\w.])", text):
        if slots.get("PORT") == m.group(1):
            continue
        slots["NUMBER"] = str(int(m.group(1)))
        break

    m = re.search(r"https?://[^\s\"'<>\\`]+", text)
    if m:
        slots["URL"] = m.group(0).rstrip(".,;:!?)")

    m = re.search(r"[\"“]([^\"”]{1,80})[\"”]", text)
    if m:
        cleaned = _clean_text(m.group(1))
        if cleaned:
            slots["REPLY"] = cleaned

    # command name: "/hello", "called hello", "command hello"
    for pattern in (r"(?<![\w/])/([a-z][a-z0-9_-]{0,31})\b",
                    r"\b(?:called|named)\s+[\"'/]?([a-z][a-z0-9_-]{0,31})\b",
                    r"\bcommand\s+[\"'/]?([a-z][a-z0-9_-]{0,31})\b"):
        m = re.search(pattern, text, re.I)
        if m and m.group(1).lower() not in IDENT_STOPWORDS and m.group(1).lower() not in ("command", "slash"):
            slots["COMMAND"] = m.group(1).lower()
            break

    # channel name: "#welcome", "channel called general"
    m = re.search(r"(?<![\w&])#([a-z][a-z0-9_-]{0,31})\b|\bchannel\s+(?:called\s+|named\s+)?[\"'#]?([a-z][a-z0-9_-]{0,31})\b", text, re.I)
    if m:
        name = (m.group(1) or m.group(2)).lower()
        if name not in IDENT_STOPWORDS:
            slots["CHANNEL"] = name

    # API route: "/tasks", "route called tasks", "for tasks"
    for pattern in (r"(?<![\w/])/([a-z][a-z0-9_-]{0,31})\b",
                    r"\b(?:route|endpoint|resource)s?\s+(?:called\s+|named\s+|for\s+)?/?([a-z][a-z0-9_-]{0,31})\b",
                    r"\b(?:api|crud)\s+(?:for|of)\s+(?:my\s+|the\s+|a\s+)?([a-z][a-z0-9_-]{0,31})\b"):
        m = re.search(pattern, text, re.I)
        if m and m.group(1).lower() not in IDENT_STOPWORDS | {"route", "endpoint", "resource", "api"}:
            slots["ROUTE"] = m.group(1).lower()
            break

    # table name: "table called orders", "a customers table"
    m = re.search(r"\btable\s+(?:called\s+|named\s+)?([a-z_][a-z0-9_]*)", text, re.I)
    name = _identifier(m.group(1)) if m else None
    if not name:
        m = re.search(r"\b([a-z_][a-z0-9_]*)\s+table\b", text, re.I)
        name = _identifier(m.group(1)) if m else None
    if name:
        slots["TABLE"] = name

    ext = {"csv_to_json": "csv", "read_json_file": "json"}.get(template_id)
    if ext:
        m = re.search(r"([A-Za-z0-9_./-]+\." + ext + r")\b", text)
        if m and not m.group(1).startswith("/") and ".." not in m.group(1):
            slots["FILE"] = m.group(1)

    m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if m:
        try:
            datetime.date.fromisoformat(m.group(1))
            slots["DATE"] = m.group(1) + "T00:00:00"
        except ValueError:
            pass
    return slots


_SLOT_RE = re.compile(r"__([A-Z]+)(?:\|(.*?))?__")


def fill(code, slots):
    """Replace __KEY|default__ markers. Returns (code, {key: (value, was_default)})."""
    used = {}

    def sub(match):
        key, default = match.group(1), match.group(2) or ""
        if key in slots:
            used[key] = (slots[key], False)
            return slots[key]
        used.setdefault(key, (default, True))
        return default

    return _SLOT_RE.sub(sub, code), used


# --------------------------------------------------------------------------
# Step 4: build the answer
# --------------------------------------------------------------------------
def _block(lang, code):
    return f"```{LANG_FENCE.get(lang, '')}\n{code.rstrip()}\n```"


def catalog_text():
    lines = [f"- {t['title']}" for t in TEMPLATES]
    return "\n".join(lines)


def _help_text():
    return (
        "I'm a fully custom code generator: no outside AI, just templates and rules I was built with. "
        "Describe what you want, for example:\n\n"
        "- \"python script that renames files to lowercase\"\n"
        "- \"discord bot in js with a /hello command\"\n"
        "- \"flask api on port 8080\"\n"
        "- \"sql table called orders\"\n"
        "- \"fizzbuzz up to 30 in javascript\"\n\n"
        "Here is everything I can build right now:\n\n" + catalog_text() + "\n\n"
        "Use the Style slider: Creative shows every language and related ideas, "
        "Precise only answers when it is confident and lists its assumptions."
    )


def _no_match(prompt, ranked, strictness, below_threshold):
    # Only suggest templates matched by something more than a generic word like "write".
    strong = [(s, t) for s, t in ranked if s >= 3]
    if below_threshold and strong:
        names = ", ".join(f"**{t['title']}**" for _, t in strong[:3])
        return (
            f"I'm not confident enough to answer that at this strictness level. Closest things I know: {names}.\n\n"
            "Add more detail, or lower the Style slider toward Creative to let me take a guess."
        )
    return (
        "I don't know how to build that yet. I only know the templates I was given, "
        "and nothing in your description matched them.\n\n"
        "Here is what I can build:\n\n" + catalog_text()
    )


def respond(prompt, strictness=50, previous=None):
    """Return {"text": markdown, "template": id or None, "confidence": float}."""
    prompt = (prompt or "").strip()[:MAX_PROMPT_CHARS]
    try:
        strictness = max(0, min(100, int(strictness)))
    except (TypeError, ValueError):
        strictness = 50
    if not prompt:
        return {"text": "Describe the code you want and I'll build it.", "template": None, "confidence": 0.0}

    ranked = score_templates(prompt)
    lang = detect_language(prompt)

    # Follow-up like "now in javascript": reuse the previous request's topic.
    if previous and (not ranked or ranked[0][0] < 3):
        for earlier in reversed(previous[-3:]):
            combined = earlier + " " + prompt
            combined_ranked = score_templates(combined)
            if combined_ranked and score_templates(earlier):
                ranked = combined_ranked
                lang = lang or detect_language(earlier)
                prompt = combined
                break

    tokens = tokenize(prompt)
    if not ranked:
        if tokens & HELP_WORDS or len(tokens) <= 2 and not lang:
            return {"text": _help_text(), "template": None, "confidence": 0.0}
        return {"text": _no_match(prompt, ranked, strictness, False), "template": None, "confidence": 0.0}

    score, tpl = ranked[0]
    conf = confidence(score)
    # A match made only of generic words (score < 3) is only worth a guess in Creative mode.
    if conf < threshold(strictness) or (score < 3 and strictness >= 35):
        return {"text": _no_match(prompt, ranked, strictness, True), "template": None, "confidence": conf}
    unsupported = detect_unsupported(prompt)

    mode = mode_for(strictness)
    slots = extract_slots(prompt, tpl["id"])
    langs = tpl["langs"]
    default_lang = next(iter(langs))
    chosen = lang if lang in langs else default_lang

    parts = [f"**{tpl['title']}**"]
    if unsupported:
        parts[0] += (f"\n\nI don't have {unsupported} templates yet, so here it is in "
                     f"{LANG_LABEL[chosen]}.")
    elif lang and lang not in langs and not tpl.get("quiet_lang"):
        parts[0] += (f"\n\nI don't have a {LANG_LABEL.get(lang, lang)} version of this yet, "
                     f"so here it is in {LANG_LABEL[default_lang]}.")
    if conf < 0.5:
        parts.append("_This is a low-confidence guess. Check that it matches what you meant._")

    shown = list(langs) if mode == "creative" else [chosen]
    all_used = {}
    for language in shown:
        base, precise, run = langs[language]
        code = precise if (mode == "precise" and precise) else base
        code, used = fill(code, slots)
        if language == chosen:
            all_used = used
        header = f"{LANG_LABEL[language]}:\n\n" if len(shown) > 1 else ""
        parts.append(f"{header}{_block(language, code)}\n\n**Run it:** {run}")

    if mode in ("precise", "creative"):
        notes = []
        for key, (value, was_default) in sorted(all_used.items()):
            notes.append(f"{key.lower()} = `{value}`" + (" (default)" if was_default else ""))
        if notes:
            parts.append("**Assumptions:** " + ", ".join(notes) + ". Put different values in your prompt to change them.")
    if mode == "creative":
        extras = [t["title"] for s, t in ranked[1:4] if t["id"] != tpl["id"]]
        if extras:
            parts.append("**Related things I can build:** " + ", ".join(extras))

    return {"text": "\n\n".join(parts), "template": tpl["id"], "confidence": conf,
            "language": chosen, "languages": list(langs)}
