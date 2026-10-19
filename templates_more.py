"""Hand-written code templates: more everyday tasks, Discord, front-end snippets, DevOps.

Same format as templates_basic.py. Slots look like __KEY|default__.
Pass quiet_lang=True for templates whose language words (python, node) are part of
the topic itself, so the engine does not complain about a "missing" language.
"""

TEMPLATES = []


def add(id, title, keywords, quiet_lang=False, **langs):
    TEMPLATES.append({"id": id, "title": title, "keywords": keywords, "langs": langs, "quiet_lang": quiet_lang})


add(
    "hello_world", "Hello, World!",
    {"hello": 4, "world": 4, "helloworld": 8, "greeting": 1},
    python=(
        r'''print("__REPLY|Hello, World!__")
''',
        None,
        "python hello.py",
    ),
    javascript=(
        r'''console.log("__REPLY|Hello, World!__");
''',
        None,
        "node hello.js",
    ),
    bash=(
        r'''#!/usr/bin/env bash
echo "__REPLY|Hello, World!__"
''',
        None,
        "bash hello.sh",
    ),
    html=(
        r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hello</title>
</head>
<body>
<h1>__REPLY|Hello, World!__</h1>
</body>
</html>
''',
        None,
        "Save as index.html and open it in a browser",
    ),
)

add(
    "sort_list", "Sort a list (quicksort)",
    {"sort": 6, "sorting": 6, "sorted": 6, "quicksort": 8, "ascending": 2, "descending": 2, "order": 1},
    python=(
        r'''def quick_sort(items):
    """Return a new sorted list using quicksort."""
    if len(items) <= 1:
        return list(items)
    pivot = items[len(items) // 2]
    smaller = [x for x in items if x < pivot]
    equal = [x for x in items if x == pivot]
    larger = [x for x in items if x > pivot]
    return quick_sort(smaller) + equal + quick_sort(larger)


numbers = [5, 2, 9, 1, 5, 6]
print(quick_sort(numbers))  # [1, 2, 5, 5, 6, 9]
print(sorted(numbers))      # the built-in sort is what you should use in real code
''',
        None,
        "python sort.py",
    ),
    javascript=(
        r'''function quickSort(items) {
  if (items.length <= 1) return [...items];
  const pivot = items[Math.floor(items.length / 2)];
  const smaller = items.filter((x) => x < pivot);
  const equal = items.filter((x) => x === pivot);
  const larger = items.filter((x) => x > pivot);
  return [...quickSort(smaller), ...equal, ...quickSort(larger)];
}

const numbers = [5, 2, 9, 1, 5, 6];
console.log(quickSort(numbers));                  // [1, 2, 5, 5, 6, 9]
console.log([...numbers].sort((a, b) => a - b));  // built-in: always pass a comparator for numbers
''',
        None,
        "node sort.js",
    ),
)

add(
    "binary_search", "Binary search",
    {"binary": 6, "search": 4, "searching": 4, "bisect": 4, "find": 1, "sorted": 1},
    python=(
        r'''def binary_search(items, target):
    """Return the index of target in the sorted list items, or -1 if it is missing."""
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


numbers = [1, 3, 5, 7, 9, 11]
print(binary_search(numbers, 7))  # 3
print(binary_search(numbers, 4))  # -1
''',
        None,
        "python binary_search.py",
    ),
    javascript=(
        r'''function binarySearch(items, target) {
  let low = 0;
  let high = items.length - 1;
  while (low <= high) {
    const mid = Math.floor((low + high) / 2);
    if (items[mid] === target) return mid;
    if (items[mid] < target) low = mid + 1;
    else high = mid - 1;
  }
  return -1;
}

const numbers = [1, 3, 5, 7, 9, 11];
console.log(binarySearch(numbers, 7)); // 3
console.log(binarySearch(numbers, 4)); // -1
''',
        None,
        "node binary_search.js",
    ),
)

add(
    "crud_api", "REST API with create, read, update, delete",
    {"crud": 8, "rest": 3, "api": 3, "resource": 2, "endpoints": 3, "endpoint": 3, "post": 1, "put": 1,
     "delete": 2, "backend": 1},
    python=(
        r'''# pip install flask
from flask import Flask, abort, jsonify, request

app = Flask(__name__)
items = {}
next_id = 1


@app.get("/__ROUTE|todos__")
def list_items():
    return jsonify(list(items.values()))


@app.post("/__ROUTE|todos__")
def create_item():
    global next_id
    item = {"id": next_id, **(request.get_json(silent=True) or {})}
    items[next_id] = item
    next_id += 1
    return jsonify(item), 201


@app.get("/__ROUTE|todos__/<int:item_id>")
def get_item(item_id):
    if item_id not in items:
        abort(404)
    return jsonify(items[item_id])


@app.put("/__ROUTE|todos__/<int:item_id>")
def update_item(item_id):
    if item_id not in items:
        abort(404)
    items[item_id].update(request.get_json(silent=True) or {})
    items[item_id]["id"] = item_id
    return jsonify(items[item_id])


@app.delete("/__ROUTE|todos__/<int:item_id>")
def delete_item(item_id):
    if items.pop(item_id, None) is None:
        abort(404)
    return "", 204


if __name__ == "__main__":
    app.run(port=__PORT|3000__)
''',
        None,
        "pip install flask, then python server.py (data is kept in memory; use a database for real projects)",
    ),
    javascript=(
        r'''// npm install express
const express = require("express");
const app = express();
app.use(express.json());

let items = [];
let nextId = 1;

app.get("/__ROUTE|todos__", (req, res) => res.json(items));

app.post("/__ROUTE|todos__", (req, res) => {
  const item = { ...req.body, id: nextId++ };
  items.push(item);
  res.status(201).json(item);
});

app.get("/__ROUTE|todos__/:id", (req, res) => {
  const item = items.find((i) => i.id === Number(req.params.id));
  if (!item) return res.sendStatus(404);
  res.json(item);
});

app.put("/__ROUTE|todos__/:id", (req, res) => {
  const item = items.find((i) => i.id === Number(req.params.id));
  if (!item) return res.sendStatus(404);
  Object.assign(item, req.body, { id: item.id });
  res.json(item);
});

app.delete("/__ROUTE|todos__/:id", (req, res) => {
  const before = items.length;
  items = items.filter((i) => i.id !== Number(req.params.id));
  if (items.length === before) return res.sendStatus(404);
  res.sendStatus(204);
});

app.listen(__PORT|3000__, () => console.log("Listening on port __PORT|3000__"));
''',
        None,
        "npm install express, then node server.js (data is kept in memory; use a database for real projects)",
    ),
)

add(
    "discord_welcome", "Discord bot that welcomes new members",
    {"welcome": 6, "member": 4, "members": 4, "join": 3, "joins": 3, "joined": 3, "greet": 3,
     "discord": 5, "bot": 1, "new": 1},
    javascript=(
        r'''// npm install discord.js
// Turn on "Server Members Intent" in the Discord Developer Portal (Bot tab).
const { Client, Events, GatewayIntentBits } = require("discord.js");

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMembers],
});

client.once(Events.ClientReady, (c) => {
  console.log(`Logged in as ${c.user.tag}`);
});

client.on(Events.GuildMemberAdd, async (member) => {
  const channel = member.guild.channels.cache.find((ch) => ch.name === "__CHANNEL|welcome__");
  if (channel && channel.isTextBased()) {
    await channel.send(`Welcome to ${member.guild.name}, ${member}!`);
  }
});

client.login(process.env.DISCORD_TOKEN);
''',
        None,
        "npm install discord.js, then DISCORD_TOKEN=... node bot.js",
    ),
    python=(
        r'''# pip install discord.py
# Turn on "Server Members Intent" in the Discord Developer Portal (Bot tab).
import os

import discord

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="__CHANNEL|welcome__")
    if channel:
        await channel.send(f"Welcome to {member.guild.name}, {member.mention}!")


client.run(os.environ["DISCORD_TOKEN"])
''',
        None,
        "pip install discord.py, then DISCORD_TOKEN=... python bot.py",
    ),
)

add(
    "dockerfile_node", "Dockerfile for a Node.js app",
    {"dockerfile": 8, "docker": 6, "container": 3, "containerize": 4, "image": 1, "node": 3, "nodejs": 3,
     "express": 1, "javascript": 1},
    quiet_lang=True,
    dockerfile=(
        r'''FROM node:20-slim
WORKDIR /app

# Install dependencies first so Docker can cache this layer
COPY package*.json ./
RUN npm ci --omit=dev

COPY . .
EXPOSE __PORT|3000__
CMD ["node", "index.js"]
''',
        None,
        "docker build -t my-app . && docker run -p __PORT|3000__:__PORT|3000__ my-app",
    ),
)

add(
    "dockerfile_python", "Dockerfile for a Python app",
    {"dockerfile": 8, "docker": 6, "container": 3, "containerize": 4, "image": 1, "python": 3, "flask": 2},
    quiet_lang=True,
    dockerfile=(
        r'''FROM python:3.12-slim
WORKDIR /app

# Install dependencies first so Docker can cache this layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE __PORT|8000__
CMD ["python", "app.py"]
''',
        None,
        "docker build -t my-app . && docker run -p __PORT|8000__:__PORT|8000__ my-app",
    ),
)

add(
    "backup_folder", "Back up a folder to a timestamped archive",
    {"backup": 8, "back": 1, "archive": 4, "compress": 3, "zip": 3, "tar": 3, "folder": 1, "directory": 1},
    bash=(
        r'''#!/usr/bin/env bash
set -euo pipefail

source_dir="${1:?Usage: $0 <folder> [destination]}"
dest_dir="${2:-$HOME/backups}"
stamp="$(date +%Y-%m-%d_%H-%M-%S)"
archive="$dest_dir/$(basename "$source_dir")_$stamp.tar.gz"

mkdir -p "$dest_dir"
tar -czf "$archive" -C "$(dirname "$source_dir")" "$(basename "$source_dir")"
echo "Backup created: $archive"
''',
        None,
        "bash backup.sh ~/projects ~/backups",
    ),
    python=(
        r'''import shutil
import sys
from datetime import datetime
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit("Usage: python backup.py <folder> [destination]")

source = Path(sys.argv[1]).resolve()
dest = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.home() / "backups"
dest.mkdir(parents=True, exist_ok=True)

stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
archive = shutil.make_archive(
    str(dest / f"{source.name}_{stamp}"), "gztar", root_dir=source.parent, base_dir=source.name
)
print(f"Backup created: {archive}")
''',
        None,
        "python backup.py ~/projects ~/backups",
    ),
)

add(
    "email_validation", "Validate an email address",
    {"email": 6, "emails": 6, "validate": 3, "validation": 3, "regex": 3, "valid": 2, "check": 1},
    python=(
        r'''import re

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")


def is_valid_email(address):
    return bool(EMAIL_RE.match(address.strip()))


print(is_valid_email("alice@example.com"))  # True
print(is_valid_email("not-an-email"))       # False
''',
        None,
        "python email_check.py (a regex only checks the shape; confirm real addresses by sending a message)",
    ),
    javascript=(
        r'''const EMAIL_RE = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$/;

function isValidEmail(address) {
  return EMAIL_RE.test(address.trim());
}

console.log(isValidEmail("alice@example.com")); // true
console.log(isValidEmail("not-an-email"));      // false
''',
        None,
        "node email_check.js (a regex only checks the shape; confirm real addresses by sending a message)",
    ),
)

add(
    "temperature_converter", "Temperature converter",
    {"temperature": 6, "celsius": 5, "fahrenheit": 5, "kelvin": 4, "convert": 2, "converter": 3},
    python=(
        r'''def convert_temperature(value, source, target):
    """Convert between "C", "F" and "K"."""
    source, target = source.upper(), target.upper()
    if source not in ("C", "F", "K") or target not in ("C", "F", "K"):
        raise ValueError("units must be C, F or K")
    celsius = {"C": value, "F": (value - 32) * 5 / 9, "K": value - 273.15}[source]
    return {"C": celsius, "F": celsius * 9 / 5 + 32, "K": celsius + 273.15}[target]


print(convert_temperature(100, "C", "F"))  # 212.0
print(convert_temperature(32, "F", "C"))   # 0.0
''',
        None,
        "python temperature.py",
    ),
    javascript=(
        r'''function convertTemperature(value, source, target) {
  const units = ["C", "F", "K"];
  source = source.toUpperCase();
  target = target.toUpperCase();
  if (!units.includes(source) || !units.includes(target)) {
    throw new Error("units must be C, F or K");
  }
  const celsius = { C: value, F: ((value - 32) * 5) / 9, K: value - 273.15 }[source];
  return { C: celsius, F: (celsius * 9) / 5 + 32, K: celsius + 273.15 }[target];
}

console.log(convertTemperature(100, "C", "F")); // 212
console.log(convertTemperature(32, "F", "C"));  // 0
''',
        None,
        "node temperature.js",
    ),
)

add(
    "calculator", "Calculator",
    {"calculator": 8, "calculate": 4, "arithmetic": 3, "add": 1, "subtract": 1, "multiply": 1, "divide": 1,
     "math": 1},
    python=(
        r'''import operator

OPERATORS = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}


def calculate(a, op, b):
    if op not in OPERATORS:
        raise ValueError(f"unsupported operator: {op}")
    if op == "/" and b == 0:
        raise ZeroDivisionError("cannot divide by zero")
    return OPERATORS[op](a, b)


print(calculate(6, "*", 7))  # 42
print(calculate(1, "/", 4))  # 0.25
''',
        None,
        "python calculator.py",
    ),
    javascript=(
        r'''const OPERATORS = {
  "+": (a, b) => a + b,
  "-": (a, b) => a - b,
  "*": (a, b) => a * b,
  "/": (a, b) => a / b,
};

function calculate(a, op, b) {
  if (!(op in OPERATORS)) throw new Error(`unsupported operator: ${op}`);
  if (op === "/" && b === 0) throw new Error("cannot divide by zero");
  return OPERATORS[op](a, b);
}

console.log(calculate(6, "*", 7)); // 42
console.log(calculate(1, "/", 4)); // 0.25
''',
        None,
        "node calculator.js",
    ),
)

add(
    "retry_backoff", "Retry a failing call with backoff",
    {"retry": 8, "retries": 8, "backoff": 6, "attempts": 3, "flaky": 3, "resilient": 2},
    python=(
        r'''import functools
import time


def retry(times=__NUMBER|3__, delay=0.5, backoff=2.0, exceptions=(Exception,)):
    """Retry the wrapped function, waiting longer after each failure."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as error:
                    if attempt == times:
                        raise
                    print(f"Attempt {attempt} failed ({error}); retrying in {wait}s")
                    time.sleep(wait)
                    wait *= backoff
        return wrapper
    return decorator


calls = {"count": 0}


@retry(delay=0.05)
def flaky():
    calls["count"] += 1
    if calls["count"] < 2:
        raise ConnectionError("temporary failure")
    return "ok"


print(flaky())  # fails once, then succeeds
''',
        None,
        "python retry.py",
    ),
    javascript=(
        r'''async function retry(fn, { times = __NUMBER|3__, delay = 500, backoff = 2 } = {}) {
  let wait = delay;
  for (let attempt = 1; attempt <= times; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === times) throw error;
      console.log(`Attempt ${attempt} failed (${error.message}); retrying in ${wait}ms`);
      await new Promise((resolve) => setTimeout(resolve, wait));
      wait *= backoff;
    }
  }
}

let calls = 0;
retry(async () => {
  calls += 1;
  if (calls < 2) throw new Error("temporary failure");
  return "ok";
}, { delay: 50 }).then(console.log); // fails once, then succeeds
''',
        None,
        "node retry.js",
    ),
)

add(
    "debounce_throttle", "Debounce and throttle",
    {"debounce": 8, "throttle": 8, "debouncing": 8, "throttling": 8, "rate": 1, "limit": 1},
    javascript=(
        r'''// debounce: run fn only after `wait` ms pass without another call
function debounce(fn, wait = __NUMBER|300__) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
}

// throttle: run fn at most once every `wait` ms
function throttle(fn, wait = __NUMBER|300__) {
  let last = 0;
  return (...args) => {
    const now = Date.now();
    if (now - last >= wait) {
      last = now;
      fn(...args);
    }
  };
}

const onType = debounce((text) => console.log("search for", text), 100);
onType("a");
onType("ab");
onType("abc"); // logs once, after 100 ms: search for abc
''',
        None,
        "node debounce.js (in a browser, attach the wrapped function to an input or scroll event)",
    ),
)

add(
    "unit_tests", "Unit test example",
    {"unit": 4, "test": 4, "tests": 4, "testing": 4, "unittest": 8, "pytest": 6, "assert": 3, "jest": 4},
    python=(
        r'''import unittest


def add(a, b):
    return a + b


class AddTests(unittest.TestCase):
    def test_adds_numbers(self):
        self.assertEqual(add(2, 3), 5)

    def test_handles_negatives(self):
        self.assertEqual(add(-1, 1), 0)

    def test_rejects_text_mixed_with_numbers(self):
        with self.assertRaises(TypeError):
            add(1, "2")


if __name__ == "__main__":
    unittest.main()
''',
        None,
        "python test_add.py",
    ),
    javascript=(
        r'''const test = require("node:test");
const assert = require("node:assert");

function add(a, b) {
  return a + b;
}

test("adds numbers", () => {
  assert.strictEqual(add(2, 3), 5);
});

test("handles negatives", () => {
  assert.strictEqual(add(-1, 1), 0);
});
''',
        None,
        "node --test (Node 18+)",
    ),
)

add(
    "counter_button", "Counter with buttons",
    {"counter": 6, "button": 3, "buttons": 3, "click": 2, "increment": 4, "decrement": 3},
    html=(
        r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Counter</title>
<style>
  body { font-family: system-ui, sans-serif; display: grid; place-items: center; height: 100vh; margin: 0; }
  #count { font-size: 3rem; text-align: center; margin-bottom: 12px; }
  button { font-size: 1.2rem; padding: 10px 18px; margin: 0 4px; border-radius: 8px; cursor: pointer; }
</style>
</head>
<body>
<div>
  <div id="count">0</div>
  <button id="dec">-</button>
  <button id="reset">Reset</button>
  <button id="inc">+</button>
</div>
<script>
  let count = 0;
  const label = document.getElementById("count");
  const show = () => { label.textContent = count; };
  document.getElementById("inc").onclick = () => { count++; show(); };
  document.getElementById("dec").onclick = () => { count--; show(); };
  document.getElementById("reset").onclick = () => { count = 0; show(); };
</script>
</body>
</html>
''',
        None,
        "Save as index.html and open it in a browser",
    ),
)

add(
    "navbar", "Responsive navigation bar",
    {"navbar": 8, "nav": 6, "navigation": 6, "menu": 3, "hamburger": 4, "header": 1, "links": 1},
    html=(
        r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Navbar</title>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; font-family: system-ui, sans-serif; }
  nav { position: relative; display: flex; align-items: center; justify-content: space-between;
        padding: 12px 20px; background: #111; color: #fff; }
  nav a { color: #fff; text-decoration: none; }
  .brand { font-weight: 700; }
  .links { display: flex; gap: 20px; }
  .toggle { display: none; background: none; border: 0; color: #fff; font-size: 1.5rem; cursor: pointer; }
  @media (max-width: 640px) {
    .toggle { display: block; }
    .links { display: none; flex-direction: column; gap: 14px; position: absolute; top: 100%;
             left: 0; right: 0; padding: 16px 20px; background: #111; }
    .links.open { display: flex; }
  }
</style>
</head>
<body>
<nav>
  <a class="brand" href="#">MySite</a>
  <button class="toggle" aria-label="Menu" aria-expanded="false">&#9776;</button>
  <div class="links" id="links">
    <a href="#">Home</a>
    <a href="#">About</a>
    <a href="#">Contact</a>
  </div>
</nav>
<script>
  const toggle = document.querySelector(".toggle");
  const links = document.getElementById("links");
  toggle.addEventListener("click", () => {
    const open = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
</script>
</body>
</html>
''',
        None,
        "Save as index.html and open it in a browser",
    ),
)

add(
    "login_form", "Login form with validation",
    {"login": 8, "signin": 6, "form": 4, "forms": 4, "validation": 2, "signup": 3, "register": 2},
    html=(
        r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Log in</title>
<style>
  body { font-family: system-ui, sans-serif; display: grid; place-items: center; min-height: 100vh; margin: 0; background: #f5f5f7; }
  form { background: #fff; padding: 24px; border-radius: 12px; width: min(340px, 90vw); box-shadow: 0 2px 8px rgba(0,0,0,.1); }
  label { display: block; margin-top: 12px; font-size: .9rem; }
  input { width: 100%; padding: 10px; margin-top: 4px; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; }
  .error { color: #c0392b; font-size: .8rem; min-height: 1.1em; }
  button { width: 100%; margin-top: 16px; padding: 10px; border: 0; border-radius: 8px; background: #4f46e5; color: #fff; cursor: pointer; }
</style>
</head>
<body>
<form id="login" novalidate>
  <h2>Log in</h2>
  <label for="email">Email</label>
  <input id="email" type="email" autocomplete="username">
  <div class="error" id="email-error"></div>
  <label for="password">Password</label>
  <input id="password" type="password" autocomplete="current-password">
  <div class="error" id="password-error"></div>
  <button type="submit">Log in</button>
</form>
<script>
  const form = document.getElementById("login");
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const emailError = emailRe.test(email) ? "" : "Enter a valid email address.";
    const passwordError = password.length >= 8 ? "" : "Password must be at least 8 characters.";
    document.getElementById("email-error").textContent = emailError;
    document.getElementById("password-error").textContent = passwordError;
    if (emailError || passwordError) return;
    // Send the values to your server over HTTPS, for example:
    // fetch("/api/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) })
    console.log("Valid form for", email);
  });
</script>
</body>
</html>
''',
        None,
        "Save as index.html and open it in a browser (real login checks must also happen on the server)",
    ),
)
