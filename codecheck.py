"""Verify generated code: syntax-check every language we can, and really run the self-contained ones.

check_code(lang, code, execute) raises AssertionError if the code is broken, or ToolMissing if this
machine lacks the toolchain for that language (the caller decides whether that is a skip).
"""
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

LUA_LIB = "/usr/lib/x86_64-linux-gnu/liblua5.4.so.0"
_LUA_RUNNER_C = r"""
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
typedef struct lua_State lua_State;
lua_State *luaL_newstate(void);
void luaL_openlibs(lua_State *L);
int luaL_loadfilex(lua_State *L, const char *filename, const char *mode);
int lua_pcallk(lua_State *L, int nargs, int nresults, int msgh, intptr_t ctx, void *k);
const char *lua_tolstring(lua_State *L, int idx, size_t *len);
int main(int argc, char **argv) {
  if (argc < 3) return 2;
  lua_State *L = luaL_newstate();
  luaL_openlibs(L);
  int st = luaL_loadfilex(L, argv[2], NULL);
  if (st == 0 && argv[1][0] == 'r') st = lua_pcallk(L, 0, 0, 0, 0, NULL);
  if (st != 0) { fprintf(stderr, "%s\n", lua_tolstring(L, -1, NULL)); return 1; }
  return 0;
}
"""
VOID = {"meta", "link", "br", "hr", "img", "input", "area", "base", "col", "embed", "source", "track", "wbr"}


class ToolMissing(Exception):
    pass


def _have(*names):
    for name in names:
        if shutil.which(name):
            return name
    raise ToolMissing(" or ".join(names))


def _run(cmd, cwd, timeout=60, env=None):
    full_env = dict(os.environ)
    full_env.update(env or {})
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=full_env)


def _write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _ok(r, what):
    assert r.returncode == 0, f"{what} failed (exit {r.returncode})\n{r.stdout[-600:]}\n{r.stderr[-1200:]}"


def lua_runner():
    """Build (once) a tiny Lua 5.4 command-line runner from the system's liblua."""
    if not os.path.exists(LUA_LIB):
        raise ToolMissing("liblua5.4")
    gcc = _have("gcc", "cc")
    out = os.path.join(tempfile.gettempdir(), "codingai_lua_runner")
    if not os.path.exists(out):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "r.c")
            _write(src, _LUA_RUNNER_C)
            tmp_out = out + f".{os.getpid()}"
            _ok(_run([gcc, src, LUA_LIB, "-o", tmp_out], tmp), "building the Lua runner")
            os.replace(tmp_out, out)
    return out


class _Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.scripts, self.styles, self._cur = [], [], [], [], None

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)
        if tag in ("script", "style"):
            self._cur = tag
            (self.scripts if tag == "script" else self.styles).append("")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._cur = None
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}> (open: {self.stack[-3:]})")
        else:
            self.stack.pop()

    def handle_data(self, data):
        if self._cur == "script":
            self.scripts[-1] += data
        elif self._cur == "style":
            self.styles[-1] += data


def _css_ok(css, label):
    assert css.count("{") == css.count("}"), f"{label}: unbalanced braces in CSS"
    assert css.count("/*") == css.count("*/"), f"{label}: unclosed CSS comment"


def check_code(lang, code, execute=False):
    with tempfile.TemporaryDirectory() as tmp:
        p = lambda name: os.path.join(tmp, name)
        env = {"HOME": tmp, "GOCACHE": p("gocache"), "GOPATH": p("gopath"), "GOFLAGS": "-mod=mod",
               "GO111MODULE": "off", "CARGO_HOME": tmp}

        if lang == "python":
            ast.parse(code)
            if execute:
                _write(p("t.py"), code)
                _ok(_run([sys.executable, p("t.py")], tmp, 30), "python run")

        elif lang == "javascript":
            node = _have("node")
            _write(p("t.js"), code)
            _ok(_run([node, "--check", p("t.js")], tmp), "node --check")
            if execute:
                _ok(_run([node, p("t.js")], tmp, 30), "node run")

        elif lang == "typescript":
            tsc = _have("tsc")
            _write(p("t.ts"), code)
            _ok(_run([tsc, "--noEmit", "--strict", "--target", "es2022", "--lib", "es2022,dom",
                      "--module", "esnext", "--moduleResolution", "bundler", "--skipLibCheck", "--types", "",
                      p("t.ts")], tmp, 90), "tsc")
            if execute:
                _write(p("t.mts"), code)
                _ok(_run([tsc, "--target", "es2022", "--lib", "es2022,dom", "--module", "nodenext",
                          "--skipLibCheck", "--types", "", "--outDir", p("out"), p("t.mts")], tmp, 90), "tsc build")
                _ok(_run([_have("node"), p("out/t.mjs")], tmp, 30), "ts run (node)")

        elif lang == "bash":
            bash = _have("bash")
            _write(p("t.sh"), code)
            _ok(_run([bash, "-n", p("t.sh")], tmp), "bash -n")
            if execute:
                _ok(_run([bash, p("t.sh")], tmp, 30), "bash run")

        elif lang == "sql":
            import sqlite3
            conn = sqlite3.connect(":memory:")
            try:
                conn.executescript(code)
            finally:
                conn.close()

        elif lang == "html":
            node = _have("node")
            parser = _Tags()
            parser.feed(code)
            assert not parser.errors, f"html: {parser.errors}"
            assert not parser.stack, f"html: unclosed {parser.stack}"
            assert "<!DOCTYPE html>" in code, "html: missing doctype"
            for css in parser.styles:
                _css_ok(css, "html <style>")
            for i, script in enumerate(parser.scripts):
                _write(p(f"s{i}.js"), script)
                _ok(_run([node, "--check", p(f"s{i}.js")], tmp), "<script> syntax")

        elif lang == "css":
            _css_ok(code, "css")

        elif lang == "dockerfile":
            lines = [x for x in code.splitlines() if x.strip() and not x.lstrip().startswith("#")]
            assert lines and lines[0].split()[0].upper() in ("FROM", "ARG"), "Dockerfile must start with FROM"

        elif lang == "json":
            json.loads(code)

        elif lang == "yaml":
            try:
                import yaml
            except ImportError:
                raise ToolMissing("pyyaml")
            list(yaml.safe_load_all(code))

        elif lang == "lua":
            runner = lua_runner()
            _write(p("t.lua"), code)
            _ok(_run([runner, "c", p("t.lua")], tmp), "lua compile")
            if execute:
                _ok(_run([runner, "r", p("t.lua")], tmp, 30), "lua run")

        elif lang in ("c", "cpp"):
            cc = _have("gcc", "cc") if lang == "c" else _have("g++")
            src = p("t.c" if lang == "c" else "t.cpp")
            std = ["-std=c11"] if lang == "c" else ["-std=c++17"]
            _write(src, code)
            _ok(_run([cc, *std, "-Wall", "-fsyntax-only", src], tmp, 60), f"{lang} syntax")
            if execute:
                _ok(_run([cc, *std, src, "-o", p("t.out"), "-lm"], tmp, 90), f"{lang} build")
                _ok(_run([p("t.out")], tmp, 30), f"{lang} run")

        elif lang == "java":
            javac, java = _have("javac"), _have("java")
            _write(p("Main.java"), code)
            _ok(_run([javac, "-d", tmp, p("Main.java")], tmp, 90), "javac (the public class must be named Main)")
            if execute:
                _ok(_run([java, "-cp", tmp, "Main"], tmp, 30), "java run")

        elif lang == "go":
            go = shutil.which("go") or "/usr/local/go/bin/go"
            if not os.path.exists(go):
                raise ToolMissing("go")
            _write(p("t.go"), code)
            _ok(_run([go, "build", "-o", p("t.out"), p("t.go")], tmp, 120, env), "go build")
            if execute:
                _ok(_run([p("t.out")], tmp, 30), "go run")

        elif lang == "rust":
            rustc = shutil.which("rustc") or "/root/.cargo/bin/rustc"
            if not os.path.exists(rustc):
                raise ToolMissing("rustc")
            _write(p("t.rs"), code)
            _ok(_run([rustc, "--edition", "2021", "-o", p("t.out"), p("t.rs")], tmp, 180, env), "rustc")
            if execute:
                _ok(_run([p("t.out")], tmp, 30), "rust run")

        elif lang == "php":
            php = _have("php")
            _write(p("t.php"), code)
            _ok(_run([php, "-l", p("t.php")], tmp), "php -l")
            if execute:
                _ok(_run([php, p("t.php")], tmp, 30), "php run")

        elif lang == "ruby":
            ruby = _have("ruby")
            _write(p("t.rb"), code)
            _ok(_run([ruby, "-c", p("t.rb")], tmp), "ruby -c")
            if execute:
                _ok(_run([ruby, p("t.rb")], tmp, 30), "ruby run")

        elif lang == "perl":
            perl = _have("perl")
            _write(p("t.pl"), code)
            _ok(_run([perl, "-c", p("t.pl")], tmp), "perl -c")
            if execute:
                _ok(_run([perl, p("t.pl")], tmp, 30), "perl run")

        else:
            raise AssertionError(f"no checker for language {lang!r}")
