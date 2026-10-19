"""Check one template module quickly:  python check_module.py tpl_roblox

Verifies every template/language variant (default slots and awkward slot values), executes the RUNNABLE ones,
and confirms every PHRASES prompt routes to the expected template and language through the real engine.
"""
import importlib
import sys

import codecheck
import engine
from test_templates import TRICKY_SLOTS


def main(name):
    mod = importlib.import_module(name)
    if name not in engine.EXTRA_MODULES:
        print(f"note: {name} is not in engine.EXTRA_MODULES, phrases are checked against the loaded engine only")
    runnable = set(getattr(mod, "RUNNABLE", set()))
    entries = [(t["id"], lang, entry) for t in getattr(mod, "TEMPLATES", []) for lang, entry in t["langs"].items()]
    entries += [(tid, lang, entry) for tid, langs in getattr(mod, "EXTEND", {}).items() for lang, entry in langs.items()]
    bad = missing = 0
    for tid, lang, (base, precise, how) in entries:
        assert lang in engine.LANG_FENCE and how.strip(), (tid, lang)
        for kind, code in (("base", base), ("precise", precise)):
            if not code:
                continue
            for slots_name, slots in (("defaults", {}), ("tricky", TRICKY_SLOTS)):
                filled, _ = engine.fill(code, slots)
                label = f"{tid}/{lang}/{kind}/{slots_name}"
                try:
                    codecheck.check_code(lang, filled, tid in runnable)
                except codecheck.ToolMissing as e:
                    missing += 1
                    print("SKIP (tool missing:", e, ")", label)
                except AssertionError as e:
                    bad += 1
                    print("FAIL", label, "\n", str(e)[:1500])
    for prompt, tid, lang in getattr(mod, "PHRASES", []):
        for strictness in (50,):
            r = engine.respond(prompt, strictness)
            if r["template"] != tid or (lang and r.get("language") != lang):
                bad += 1
                print(f"PHRASE FAIL {prompt!r}: wanted {tid}/{lang}, got {r['template']}/{r.get('language')}")
    print(f"{len(entries)} variants, {len(getattr(mod, 'PHRASES', []))} phrases, {bad} failures, {missing} skipped")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
