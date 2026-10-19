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
import importlib
import logging
import re

import templates_basic as _basic
import templates_web as _web
import templates_more as _more

log = logging.getLogger("codingai")

# New template modules (see tplkit.py for the contract). A module that does not exist yet is skipped;
# a module that exists but is broken fails loudly at import time.
EXTRA_MODULES = [
    "tpl_roblox", "tpl_discord", "tpl_python", "tpl_frontend", "tpl_backend", "tpl_devops",
    "tpl_compiled", "tpl_scripting",
]

TEMPLATES = []
PHRASES = []          # (prompt, template_id, language or None): sample prompts the matcher must route correctly
RUNNABLE = set()      # template ids whose code the tests execute
EXTRA_SLOTS = {}      # extra slot rules contributed by modules
_EXTENDS = []


def _load():
    legacy = ((_basic, "Everyday code"), (_web, "Web, apps and bots"), (_more, "Tools and scripts"))
    for mod, category in legacy:
        for tpl in mod.TEMPLATES:
            tpl.setdefault("category", category)
            tpl.setdefault("quiet_lang", False)
            TEMPLATES.append(tpl)
    for name in EXTRA_MODULES:
        try:
            mod = importlib.import_module(name)
        except ModuleNotFoundError as e:
            if e.name == name:
                continue
            raise
        category = getattr(mod, "CATEGORY", name)
        for tpl in getattr(mod, "TEMPLATES", []):
            tpl.setdefault("category", category)
            tpl.setdefault("quiet_lang", False)
            TEMPLATES.append(tpl)
        _EXTENDS.append((name, getattr(mod, "EXTEND", {})))
        RUNNABLE.update(getattr(mod, "RUNNABLE", set()))
        PHRASES.extend(getattr(mod, "PHRASES", []))
        for slot, rules in getattr(mod, "SLOTS", {}).items():
            EXTRA_SLOTS.setdefault(slot, []).extend(rules)


_load()
BY_ID = {t["id"]: t for t in TEMPLATES}
if len(BY_ID) != len(TEMPLATES):
    raise RuntimeError("duplicate template ids")
for _name, _ext in _EXTENDS:
    for _tid, _langs in _ext.items():
        if _tid not in BY_ID:
            raise RuntimeError(f"{_name}: EXTEND refers to unknown template {_tid!r}")
        for _lang, _entry in _langs.items():
            BY_ID[_tid]["langs"].setdefault(_lang, _entry)

MAX_PROMPT_CHARS = 2000
SCORE_FOR_FULL_CONFIDENCE = 6.0

LANG_WORDS = {
    "python": "python", "py": "python", "python3": "python", "flask": "python",
    "discord.py": "python", "discordpy": "python", "requests": "python",
    "beautifulsoup": "python", "bs4": "python",
    "javascript": "javascript", "js": "javascript", "node": "javascript",
    "nodejs": "javascript", "node.js": "javascript", "express": "javascript",
    "discord.js": "javascript", "discordjs": "javascript",
    "typescript": "typescript", "ts": "typescript",
    "bash": "bash", "shell": "bash", "sh": "bash", "terminal": "bash",
    "html": "html", "webpage": "html", "website": "html", "css": "html",
    "sql": "sql", "mysql": "sql", "postgres": "sql", "postgresql": "sql", "sqlite": "sql",
    "docker": "dockerfile", "dockerfile": "dockerfile",
    "lua": "lua", "luau": "lua", "roblox": "lua",
    "c": "c", "cpp": "cpp", "c++": "cpp", "java": "java", "go": "go", "golang": "go",
    "rust": "rust", "php": "php", "ruby": "ruby", "perl": "perl",
    "yaml": "yaml", "yml": "yaml", "json": "json",
}
# Words that are also ordinary English: they only count as a language after "in", "using", "with"...
AMBIGUOUS_LANG_WORDS = {"c", "go", "ts", "json"}
_LANG_LEADERS = {"in", "using", "with", "via", "as", "a", "an", "for", "the", "into", "to", "from", "of"}
LANG_FENCE = {"python": "python", "javascript": "javascript", "typescript": "typescript", "bash": "bash",
              "html": "html", "sql": "sql", "dockerfile": "dockerfile", "lua": "lua", "c": "c", "cpp": "cpp",
              "java": "java", "go": "go", "rust": "rust", "php": "php", "ruby": "ruby", "perl": "perl",
              "yaml": "yaml", "json": "json", "css": "css"}
LANG_LABEL = {"python": "Python", "javascript": "JavaScript", "typescript": "TypeScript", "bash": "Bash",
              "html": "HTML/CSS/JS", "sql": "SQL", "dockerfile": "Dockerfile", "lua": "Lua (Roblox)", "c": "C",
              "cpp": "C++", "java": "Java", "go": "Go", "rust": "Rust", "php": "PHP", "ruby": "Ruby",
              "perl": "Perl", "yaml": "YAML", "json": "JSON", "css": "CSS"}

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
    "c#": "C#", "csharp": "C#", "swift": "Swift", "kotlin": "Kotlin", "r": "R", "dart": "Dart",
    "scala": "Scala", "haskell": "Haskell", "elixir": "Elixir", "assembly": "Assembly", "vba": "VBA",
}


def detect_languages(prompt):
    """Every supported language mentioned in the prompt, in order of appearance."""
    words = _words(prompt)
    found = []
    for i, word in enumerate(words):
        lang = LANG_WORDS.get(word)
        if not lang:
            continue
        if word in AMBIGUOUS_LANG_WORDS and not (i > 0 and words[i - 1] in _LANG_LEADERS):
            continue
        if lang not in found:
            found.append(lang)
    return found


def detect_language(prompt):
    """First supported language mentioned in the prompt, or None."""
    found = detect_languages(prompt)
    return found[0] if found else None


def detect_unsupported(prompt):
    """Name of a language the user asked for that I have no templates for, or None."""
    words = _words(prompt)
    if detect_languages(prompt):
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
        if "NUMBER" not in slots:
            slots["NUMBER"] = str(int(m.group(1)))
        else:
            slots["NUMBER2"] = str(int(m.group(1)))
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

    m = re.search(r"\b(?:called|named)\s+[\"']?([A-Za-z][A-Za-z0-9_]{0,30})\b", text)
    if m and m.group(1).lower() not in IDENT_STOPWORDS:
        slots["NAME"] = m.group(1)

    for slot, rules in EXTRA_SLOTS.items():
        for regex, value in rules:
            m = re.search(regex, text, re.I)
            if not m:
                continue
            try:
                got = value(m) if callable(value) else value
            except (ValueError, IndexError):
                got = None
            got = _clean_text(str(got)) if got is not None else ""
            if got:
                slots[slot] = got
                break

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


def categories():
    """{category: [titles]} in the order templates were loaded."""
    out = {}
    for t in TEMPLATES:
        out.setdefault(t["category"], []).append(t["title"])
    return out


def catalog_text(topic=None):
    cats = categories()
    if topic:
        words = {w for t in tokenize(topic) for w in stems(t)} - {"help", "me", "with", "on", "for", "the", "a", "all", "list", "show"}
        picked = {}
        for cat, titles in cats.items():
            cat_words = {w for t in tokenize(cat) for w in stems(t)}
            if words & cat_words:
                picked[cat] = titles
        if not picked:
            for t in TEMPLATES:
                text_words = {w for x in tokenize(t["title"]) for w in stems(x)} | set(t["keywords"])
                if words & text_words:
                    picked.setdefault(t["category"], []).append(t["title"])
        if picked:
            return "\n\n".join(f"**{c}**\n" + "\n".join(f"- {x}" for x in titles) for c, titles in picked.items())
        topic = None
    lines = []
    for cat, titles in cats.items():
        sample = ", ".join(titles[:3])
        lines.append(f"- **{cat}** ({len(titles)}): {sample}...")
    return "\n".join(lines)


def _help_text(topic=None):
    if topic:
        found = catalog_text(topic)
        if found and not found.startswith("- **"):
            return f"Here is what I can build for \"{topic}\":\n\n{found}\n\nDescribe one of these and I'll write it."
    return (
        "I'm a fully custom code generator: no outside AI, just templates and rules I was built with. "
        "Describe what you want, for example:\n\n"
        "- \"roblox script that sets my walkspeed to 50\"\n"
        "- \"discord bot in js with a /hello command\"\n"
        "- \"flask api on port 8080\"\n"
        "- \"binary search in c\"\n"
        "- \"sql table called orders\"\n\n"
        f"I know {len(TEMPLATES)} things, in these areas:\n\n" + catalog_text() + "\n\n"
        "Type `help roblox` (or any area or word) to list what is in it. "
        "Use the Style slider: Creative shows every language and related ideas, "
        "Precise only answers when it is confident and lists its assumptions."
    )


def _log_unmatched(prompt):
    log.warning("unmatched prompt: %s", re.sub(r"\s+", " ", prompt)[:200])


def _no_match(prompt, ranked, strictness, below_threshold):
    # Only suggest templates matched by something more than a generic word like "write".
    strong = [(s, t) for s, t in ranked if s >= 3]
    if below_threshold and strong:
        names = ", ".join(f"**{t['title']}**" for _, t in strong[:3])
        return (
            f"I'm not confident enough to answer that at this strictness level. Closest things I know: {names}.\n\n"
            "Add more detail, or lower the Style slider toward Creative to let me take a guess."
        )
    _log_unmatched(prompt)
    return (
        "I don't know how to build that yet. I only know the templates I was given, "
        "and nothing in your description matched them.\n\n"
        "Here are the areas I cover:\n\n" + catalog_text() + "\n\n"
        "Type `help <area>` (for example `help roblox`) to see what is inside one, "
        "or try rephrasing with the key words (what it does, plus the language)."
    )


_HELP_RE = re.compile(r"^\s*(?:help|commands|menu|what can you (?:do|build|make)|what do you (?:know|support)|list)\b[\s:,-]*(.*)$", re.I)


def respond(prompt, strictness=50, previous=None):
    """Return {"text": markdown, "template": id or None, "confidence": float}."""
    prompt = (prompt or "").strip()[:MAX_PROMPT_CHARS]
    try:
        strictness = max(0, min(100, int(strictness)))
    except (TypeError, ValueError):
        strictness = 50
    if not prompt:
        return {"text": "Describe the code you want and I'll build it.", "template": None, "confidence": 0.0}

    m = _HELP_RE.match(prompt)
    if m and len(prompt) < 60:
        return {"text": _help_text(m.group(1).strip() or None), "template": None, "confidence": 0.0}

    ranked = score_templates(prompt)
    wanted = detect_languages(prompt)

    # Follow-up like "now in javascript": reuse the previous request's topic.
    if previous and (not ranked or ranked[0][0] < 3):
        for earlier in reversed(previous[-3:]):
            combined = earlier + " " + prompt
            combined_ranked = score_templates(combined)
            if combined_ranked and score_templates(earlier):
                ranked = combined_ranked
                wanted = wanted or detect_languages(earlier)
                prompt = combined
                break

    tokens = tokenize(prompt)
    if not ranked:
        if tokens & HELP_WORDS or len(tokens) <= 2 and not wanted:
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
    lang = wanted[0] if wanted else None
    chosen = next((w for w in wanted if w in langs), default_lang)

    parts = [f"**{tpl['title']}**"]
    if unsupported:
        parts[0] += (f"\n\nI don't have {unsupported} templates yet, so here it is in "
                     f"{LANG_LABEL[chosen]}.")
    elif lang and chosen not in wanted and not tpl.get("quiet_lang"):
        parts[0] += (f"\n\nI don't have a {LANG_LABEL.get(lang, lang)} version of this yet, "
                     f"so here it is in {LANG_LABEL[default_lang]}.")
    if conf < 0.5:
        parts.append("_This is a low-confidence guess. Check that it matches what you meant._")

    shown = ([chosen] + [l for l in langs if l != chosen])[:3] if mode == "creative" else [chosen]
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
