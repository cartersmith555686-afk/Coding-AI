"""Helpers shared by every template module.

A template module defines (all optional except TEMPLATES):

  CATEGORY   "Roblox / Lua"      heading used in the help list
  TEMPLATES  [...]               new templates, built with kit() below
  EXTEND     {template_id: {language: (code, precise_or_None, how_to_run)}}
                                 adds more languages to templates defined elsewhere
  RUNNABLE   {"template_id"}     ids whose code is EXECUTED by the tests (must be self-contained:
                                 no network, servers, input(), third-party packages, files outside the cwd)
  PHRASES    [(prompt, template_id, language_or_None)]
                                 sample prompts the matcher must route correctly
  SLOTS      {"NAME": [(regex, value_or_function)]}
                                 extra values pulled out of the prompt (see engine.extract_slots)

Code in a template can contain slots like __NUMBER|10__ (value from the prompt, default 10).
Built-in slots: NUMBER, NUMBER2, PORT, URL, REPLY, COMMAND, NAME, CHANNEL, ROUTE, TABLE, FILE, DATE.
"""
import re


def kit(category):
    """Returns (TEMPLATES list, add function) for a module."""
    templates = []

    def add(id, title, keywords, quiet_lang=False, **langs):
        """keywords: {word: weight}. langs: language=(code, precise_code_or_None, how_to_run)."""
        templates.append({
            "id": id, "title": title, "keywords": keywords, "langs": langs,
            "quiet_lang": quiet_lang, "category": category,
        })

    return templates, add


_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,40}")


def ident(value):
    """A safe identifier, or None. Use this on anything taken from user text that goes into code unquoted."""
    if value and _IDENT.fullmatch(value):
        return value
    return None
