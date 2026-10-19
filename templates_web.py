"""Hand-written code templates: bots, servers, files, web pages, SQL.

Same format as templates_basic.py. Slots look like __KEY|default__.
"""

TEMPLATES = []


def add(id, title, keywords, **langs):
    TEMPLATES.append({"id": id, "title": title, "keywords": keywords, "langs": langs})


add(
    "discord_slash_command", "Discord bot with a slash command",
    {"discord": 6, "bot": 3, "slash": 4, "command": 2, "commands": 2, "ping": 2},
    javascript=(
        '''// npm install discord.js
const {
  Client, Events, GatewayIntentBits, REST, Routes, SlashCommandBuilder,
} = require("discord.js");

const TOKEN = process.env.DISCORD_TOKEN;
const CLIENT_ID = process.env.CLIENT_ID;

const commands = [
  new SlashCommandBuilder()
    .setName("__COMMAND|ping__")
    .setDescription("Replies with __REPLY|Pong!__")
    .toJSON(),
];

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

client.once(Events.ClientReady, async (c) => {
  const rest = new REST({ version: "10" }).setToken(TOKEN);
  await rest.put(Routes.applicationCommands(CLIENT_ID), { body: commands });
  console.log(`Logged in as ${c.user.tag}`);
});

client.on(Events.InteractionCreate, async (interaction) => {
  if (!interaction.isChatInputCommand()) return;
  if (interaction.commandName === "__COMMAND|ping__") {
    await interaction.reply("__REPLY|Pong!__");
  }
});

client.login(TOKEN);
''',
        None,
        "npm install discord.js, then DISCORD_TOKEN=... CLIENT_ID=... node bot.js",
    ),
    python=(
        '''# pip install discord.py
import os

import discord
from discord import app_commands


class Bot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


bot = Bot()


@bot.tree.command(name="__COMMAND|ping__", description="Replies with __REPLY|Pong!__")
async def command(interaction: discord.Interaction):
    await interaction.response.send_message("__REPLY|Pong!__")


bot.run(os.environ["DISCORD_TOKEN"])
''',
        None,
        "pip install discord.py, then DISCORD_TOKEN=... python bot.py",
    ),
)

add(
    "http_server", "Simple web server / API",
    {"server": 4, "api": 4, "flask": 4, "express": 4, "http": 3, "endpoint": 3, "route": 2,
     "web": 1, "rest": 2, "backend": 2},
    python=(
        '''# pip install flask
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify(message="Hello, world!")


@app.route("/api/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=__PORT|3000__)
''',
        None,
        "pip install flask, then python server.py",
    ),
    javascript=(
        '''// npm install express
const express = require("express");
const app = express();

app.use(express.json());

app.get("/", (req, res) => {
  res.json({ message: "Hello, world!" });
});

app.get("/api/health", (req, res) => {
  res.json({ status: "ok" });
});

app.listen(__PORT|3000__, () => {
  console.log("Server running on port __PORT|3000__");
});
''',
        None,
        "npm install express, then node server.js",
    ),
)

add(
    "fetch_api", "Fetch data from an API",
    {"fetch": 4, "request": 3, "api": 3, "http": 2, "get": 1, "download": 1, "call": 1, "json": 1},
    python=(
        '''# pip install requests
import requests


def fetch_json(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


data = fetch_json("__URL|https://api.github.com/repos/python/cpython__")
print(data)
''',
        None,
        "pip install requests, then python fetch.py",
    ),
    javascript=(
        '''async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

fetchJson("__URL|https://api.github.com/repos/nodejs/node__")
  .then((data) => console.log(data))
  .catch((err) => console.error(err.message));
''',
        None,
        "node fetch.js (Node 18+)",
    ),
)

add(
    "rename_files_lowercase", "Rename all files in a folder to lowercase",
    {"rename": 5, "files": 3, "file": 1, "lowercase": 5, "folder": 2, "directory": 2, "lower": 3},
    python=(
        '''from pathlib import Path


def lowercase_files(folder):
    for path in Path(folder).iterdir():
        if not path.is_file():
            continue
        target = path.with_name(path.name.lower())
        if target == path:
            continue
        if target.exists() and not target.samefile(path):
            print(f"Skipped {path.name}: {target.name} already exists")
            continue
        path.rename(target)
        print(f"{path.name} -> {target.name}")


lowercase_files("__FOLDER|.__")
''',
        None,
        "python rename.py",
    ),
    bash=(
        '''#!/usr/bin/env bash
cd "__FOLDER|.__" || exit 1
for f in *; do
  [ -f "$f" ] || continue
  lower=$(printf '%s' "$f" | tr '[:upper:]' '[:lower:]')
  if [ "$f" != "$lower" ]; then
    mv -n -- "$f" "$lower" && echo "$f -> $lower"
  fi
done
''',
        None,
        "bash rename.sh",
    ),
)

add(
    "read_json_file", "Read and write a JSON file",
    {"json": 5, "read": 2, "write": 2, "save": 2, "load": 2, "file": 1, "config": 2},
    python=(
        '''import json
from pathlib import Path

path = Path("__FILE|data.json__")

data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
data["visits"] = data.get("visits", 0) + 1
path.write_text(json.dumps(data, indent=2), encoding="utf-8")
print(data)
''',
        None,
        "python json_file.py",
    ),
    javascript=(
        '''const fs = require("fs");

const path = "__FILE|data.json__";
const data = fs.existsSync(path) ? JSON.parse(fs.readFileSync(path, "utf8")) : {};
data.visits = (data.visits || 0) + 1;
fs.writeFileSync(path, JSON.stringify(data, null, 2));
console.log(data);
''',
        None,
        "node json_file.js",
    ),
)

add(
    "csv_to_json", "Convert CSV to JSON",
    {"csv": 6, "convert": 2, "json": 2, "spreadsheet": 1, "table": 1},
    python=(
        '''import csv
import json

with open("__FILE|input.csv__", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2)

print(f"Converted {len(rows)} rows")
''',
        None,
        "python csv_to_json.py",
    ),
)

add(
    "web_scraper", "Web scraper (page title and links)",
    {"scrape": 5, "scraper": 5, "scraping": 5, "crawl": 3, "links": 2, "parse": 1, "beautifulsoup": 4},
    python=(
        '''# pip install requests beautifulsoup4
import requests
from bs4 import BeautifulSoup

url = "__URL|https://example.com__"
response = requests.get(url, timeout=10, headers={"User-Agent": "my-scraper/1.0"})
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
print("Title:", soup.title.string if soup.title else "(none)")
for link in soup.find_all("a", href=True):
    print(link["href"], "-", link.get_text(strip=True))
''',
        None,
        "pip install requests beautifulsoup4, then python scrape.py (check the site's terms first)",
    ),
)

add(
    "sql_table", "SQL table with basic queries",
    {"sql": 6, "table": 4, "database": 3, "query": 2, "select": 2, "insert": 2, "create": 1, "schema": 2},
    sql=(
        '''CREATE TABLE __TABLE|users__ (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO __TABLE|users__ (name, email) VALUES ('Alice', 'alice@example.com');

SELECT id, name, email FROM __TABLE|users__ ORDER BY name;

UPDATE __TABLE|users__ SET name = 'Alice Smith' WHERE email = 'alice@example.com';

DELETE FROM __TABLE|users__ WHERE id = 1;
''',
        None,
        "Run in SQLite, PostgreSQL or MySQL (AUTOINCREMENT/SERIAL syntax varies by database)",
    ),
)

add(
    "todo_app", "To-do list web page",
    {"todo": 6, "todos": 6, "task": 3, "tasks": 3, "list": 2, "checklist": 3, "app": 1},
    html=(
        '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>To-Do List</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 480px; margin: 40px auto; padding: 0 16px; }
  form { display: flex; gap: 8px; }
  input[type=text] { flex: 1; padding: 8px; }
  li { display: flex; gap: 8px; align-items: center; padding: 6px 0; }
  li.done span { text-decoration: line-through; color: #888; }
  li button { margin-left: auto; }
</style>
</head>
<body>
<h1>To-Do List</h1>
<form id="form"><input type="text" id="text" placeholder="Add a task" required><button>Add</button></form>
<ul id="list"></ul>
<script>
  const list = document.getElementById("list");
  let tasks = JSON.parse(localStorage.getItem("tasks") || "[]");

  function render() {
    list.textContent = "";
    tasks.forEach((task, i) => {
      const li = document.createElement("li");
      if (task.done) li.className = "done";
      const box = document.createElement("input");
      box.type = "checkbox"; box.checked = task.done;
      box.onchange = () => { task.done = box.checked; save(); };
      const label = document.createElement("span");
      label.textContent = task.text;
      const del = document.createElement("button");
      del.textContent = "Delete";
      del.onclick = () => { tasks.splice(i, 1); save(); };
      li.append(box, label, del);
      list.appendChild(li);
    });
  }
  function save() { localStorage.setItem("tasks", JSON.stringify(tasks)); render(); }

  document.getElementById("form").onsubmit = (e) => {
    e.preventDefault();
    const input = document.getElementById("text");
    tasks.push({ text: input.value.trim(), done: false });
    input.value = "";
    save();
  };
  render();
</script>
</body>
</html>
''',
        None,
        "Save as index.html and open it in a browser",
    ),
)

add(
    "pricing_table", "Responsive pricing table",
    {"pricing": 6, "price": 4, "prices": 4, "plans": 4, "plan": 3, "table": 1, "tiers": 3, "responsive": 1},
    html=(
        '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pricing</title>
<style>
  body { font-family: system-ui, sans-serif; margin: 0; padding: 40px 16px; background: #f5f5f7; }
  h1 { text-align: center; }
  .plans { display: grid; gap: 16px; max-width: 900px; margin: 24px auto;
           grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
  .plan { background: #fff; border-radius: 12px; padding: 24px; text-align: center;
          box-shadow: 0 2px 8px rgba(0,0,0,.08); }
  .plan.featured { border: 2px solid #4f46e5; }
  .price { font-size: 2rem; font-weight: 700; margin: 8px 0; }
  ul { list-style: none; padding: 0; line-height: 2; }
  a.btn { display: inline-block; padding: 10px 20px; border-radius: 8px; background: #4f46e5;
          color: #fff; text-decoration: none; }
</style>
</head>
<body>
<h1>Choose your plan</h1>
<div class="plans">
  <div class="plan"><h2>Free</h2><div class="price">$0</div>
    <ul><li>1 project</li><li>Community support</li></ul><a class="btn" href="#">Get started</a></div>
  <div class="plan featured"><h2>Pro</h2><div class="price">$12<small>/mo</small></div>
    <ul><li>Unlimited projects</li><li>Email support</li></ul><a class="btn" href="#">Go Pro</a></div>
  <div class="plan"><h2>Team</h2><div class="price">$39<small>/mo</small></div>
    <ul><li>Everything in Pro</li><li>Team seats</li></ul><a class="btn" href="#">Contact us</a></div>
</div>
</body>
</html>
''',
        None,
        "Save as index.html and open it in a browser",
    ),
)

add(
    "countdown_timer", "Countdown timer web page",
    {"countdown": 6, "timer": 4, "count": 1, "until": 2, "days": 1},
    html=(
        '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Countdown</title>
<style>
  body { font-family: system-ui, sans-serif; display: grid; place-items: center; height: 100vh; margin: 0; background: #111; color: #fff; }
  #time { font-size: 2.5rem; font-variant-numeric: tabular-nums; }
</style>
</head>
<body>
<div id="time"></div>
<script>
  const target = new Date("__DATE|2027-01-01T00:00:00__");
  const out = document.getElementById("time");
  function tick() {
    const ms = target - new Date();
    if (ms <= 0) { out.textContent = "Time's up!"; return; }
    const s = Math.floor(ms / 1000);
    out.textContent = `${Math.floor(s / 86400)}d ${Math.floor(s % 86400 / 3600)}h ` +
                      `${Math.floor(s % 3600 / 60)}m ${s % 60}s`;
  }
  tick();
  setInterval(tick, 1000);
</script>
</body>
</html>
''',
        None,
        "Save as index.html and open it in a browser",
    ),
)
