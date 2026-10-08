"""Local configuration page shown by Galaxy when the integration is connected."""
import html
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import config

CSS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "website", "css", "main.css")

_REDIRECT = b'<script>window.location="/end";</script>'
_HEAD = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
)

_DONE_PAGE = _HEAD + """<style>{css}</style><title>Configuration saved</title></head><body><div class="backdrop"></div><main class="shell"><section class="success-card"><div class="success-icon">&#10003;</div><div class="eyebrow">LOCAL GAMES</div><h1>Configuration saved</h1><p>You can close this window and return to GOG Galaxy.</p></section></main></body></html>"""

_ROW = """<div class="game-row"><input type="hidden" name="gid" value="{gid}"><div class="game-row-head"><strong class="row-title">{title}</strong><span class="game-state {state_class}">{state}</span><button type="button" class="row-remove">Remove</button></div><div class="field-grid"><label class="field"><span>Name <em>Shown in Galaxy</em><em class="name-count">{name_len}/{name_max}</em></span><input class="name-input" name="name" value="{name}" maxlength="{name_max}" placeholder="Game name"></label><label class="field"><span>Executable <em>Required</em></span><input class="exe-input" name="exe" value="{exe}" placeholder="C:\\Games\\MyGame\\game.exe"><small class="field-error">Executable path is required.</small></label><label class="field"><span>Arguments <em>Optional</em></span><input name="args" value="{args}" placeholder="-windowed -nosplash"></label><label class="field"><span>Start in folder <em>Optional</em></span><input name="workdir" value="{workdir}" placeholder="Defaults to the executable's folder"></label></div></div>"""

_BLANK_ROW = _ROW.format(gid="", title="New game", state_class="fresh", state="Add the .exe", name="", name_len=0,
                         name_max=config.NAME_MAX, exe="", args="", workdir="")

_INDEX_PAGE = _HEAD + """<title>Local Games Integration · GOG Galaxy</title><style>{css}</style></head><body><div class="backdrop"></div><main class="shell">
<header class="topbar"><div class="brand"><div class="brand-mark local-mark">LG</div><div><div class="brand-title">Local Games Integration</div><div class="brand-subtitle">GOG Galaxy · your own games</div></div></div><div class="pill"><span class="status-dot"></span>Local library</div></header>
<section class="hero-card"><div class="hero-copy"><div class="eyebrow">GALAXY PLUGIN</div><h1>Any game, one click away.</h1><p>Add the games that are not in GOG's database. You choose the name and the executable; the plugin shows them in Galaxy, launches them and counts your playtime. Nothing is looked up online.</p></div><div class="hero-art" aria-hidden="true"><span class="spark a"></span><span class="spark b"></span><span class="spark c"></span><span class="spark d"></span><div class="folder"><span class="folder-back"></span><span class="folder-front"></span></div><div class="exe-win"><span class="exe-bar"><i></i><i></i><i></i></span><span class="exe-play"></span><span class="exe-label">.EXE</span></div></div></section>
<form class="config-form" method="POST" action="/setconfig" novalidate>
<section class="card"><div class="section-heading"><div><div class="eyebrow">YOUR LIBRARY</div><h2>Games</h2></div><span class="section-badge" id="game-count">{count}</span></div><div class="game-list" id="game-list">{rows}</div><div class="empty-note" id="empty-note">No games yet. Add the first one below.</div><button type="button" class="add-game" id="add-game">+ Add a game</button><div class="hint"><span class="hint-icon">i</span><span>Tip: in Windows Explorer, hold Shift, right-click the .exe and choose "Copy as path", then paste it here. Quotes are removed for you.</span></div></section>
<div class="actions"><div class="footer-note"><span class="status-dot"></span>Configuration is stored locally for this plugin.</div><button type="submit"><span>Save configuration</span><span class="button-arrow">→</span></button></div>
</form>
<template id="row-template">""" + _BLANK_ROW + """</template>
<script>
(() => {
  const NAME_MAX = {name_max};
  const form = document.querySelector(".config-form");
  const list = document.getElementById("game-list");
  const note = document.getElementById("empty-note");
  const countBadge = document.getElementById("game-count");
  const template = document.getElementById("row-template");
  const timers = new WeakMap();

  function setState(row, text, cls) {
    const badge = row.querySelector(".game-state");
    badge.textContent = text;
    badge.className = "game-state " + cls;
  }
  function refresh() {
    const rows = [...list.querySelectorAll(".game-row")];
    note.hidden = rows.length > 0;
    const games = rows.filter(row => row.querySelector(".exe-input").value.trim()).length;
    countBadge.textContent = games + (games === 1 ? " game" : " games");
    rows.forEach(row => {
      const name = row.querySelector(".name-input").value.trim();
      row.querySelector(".row-title").textContent = name || "New game";
      const counter = row.querySelector(".name-count");
      const length = row.querySelector(".name-input").value.length;
      counter.textContent = length + "/" + NAME_MAX;
      counter.classList.toggle("full", length >= NAME_MAX);
    });
  }
  function check(row) {
    const path = row.querySelector(".exe-input").value.trim().replace(/^"+|"+$/g, "").trim();
    if (!path) { setState(row, "Add the .exe", "fresh"); return; }
    fetch("/check?path=" + encodeURIComponent(path), {cache: "no-store"})
      .then(r => r.text())
      .then(text => {
        // ignore the answer when the user kept typing meanwhile
        const now = row.querySelector(".exe-input").value.trim().replace(/^"+|"+$/g, "").trim();
        if (now !== path) return;
        text === "1" ? setState(row, "Found", "") : setState(row, "File not found", "missing");
      })
      .catch(() => {});
  }
  function scheduleCheck(row) {
    clearTimeout(timers.get(row));
    timers.set(row, setTimeout(() => check(row), 250));
  }
  function validateRow(row) {
    const inputs = [...row.querySelectorAll("input[name]")].filter(i => i.type !== "hidden");
    const exe = row.querySelector(".exe-input");
    const error = row.querySelector(".field-error");
    const used = inputs.some(i => i.value.trim());
    const missing = used && !exe.value.trim();
    exe.classList.toggle("invalid", missing);
    error.classList.toggle("visible", missing);
    exe.setAttribute("aria-invalid", missing ? "true" : "false");
    return !missing;
  }
  function addRow() {
    list.appendChild(template.content.firstElementChild.cloneNode(true));
    refresh();
    list.lastElementChild.querySelector(".name-input").focus();
  }
  document.getElementById("add-game").addEventListener("click", addRow);
  list.addEventListener("click", event => {
    if (event.target.closest(".row-remove")) {
      event.target.closest(".game-row").remove();
      refresh();
    }
  });
  list.addEventListener("input", event => {
    const row = event.target.closest(".game-row");
    refresh();
    if (!row) return;
    if (event.target.classList.contains("exe-input")) {
      scheduleCheck(row);
      if (event.target.classList.contains("invalid")) validateRow(row);
    }
  });
  form.addEventListener("submit", event => {
    const ok = [...list.querySelectorAll(".game-row")].map(validateRow).every(Boolean);
    if (!ok) {
      event.preventDefault();
      form.querySelector(".invalid")?.focus();
    }
  });
  refresh();
})();
</script></main></body></html>"""


def _css():
    try:
        with open(CSS_FILE, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def _render(template, **values):
    # One pass over the template: text that was inserted (a game called "{tag}", say) is never substituted again,
    # and the CSS and scripts with their literal braces are left alone.
    return re.sub(r"\{(\w+)\}", lambda m: values.get(m.group(1), m.group(0)), template)


def _rows(games):
    rows = []
    for game in games:
        found = os.path.isfile(game["exe"])
        rows.append(_render(
            _ROW,
            gid=html.escape(game["id"], quote=True),
            title=html.escape(game["name"]),
            state_class="" if found else "missing",
            state="Found" if found else "File not found",
            name=html.escape(game["name"], quote=True),
            name_len=str(len(game["name"])),
            name_max=str(config.NAME_MAX),
            exe=html.escape(game["exe"], quote=True),
            args=html.escape(game["args"], quote=True),
            workdir=html.escape(game["workdir"], quote=True),
        ))
    return "".join(rows)


def _field(params, key, index):
    values = params.get(key, [])
    return values[index] if index < len(values) else ""


def save_form(params):
    """Store the submitted form. Rows without an executable are dropped; known IDs are kept (so playtime stays)."""
    library = config.load_library()
    known = {game["id"] for game in library["games"]}
    games, used = [], set()
    for index in range(min(len(params.get("exe", [])), config.MAX_GAMES)):
        gid = _field(params, "gid", index).strip()
        game = config._clean_game({
            "id": gid if gid in known and gid not in used else "",
            "name": _field(params, "name", index),
            "exe": _field(params, "exe", index),
            "args": _field(params, "args", index),
            "workdir": _field(params, "workdir", index),
        })
        if game is None:
            continue
        while game["id"] in used:
            game["id"] = config.new_game_id()
        used.add(game["id"])
        games.append(game)
    library["games"] = games
    config.save_library(library)


class AuthenticationHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send(self, body, content_type="text/html; charset=utf-8", status=200):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/css/main.css":
            self._send(_css(), "text/css; charset=utf-8")
        elif url.path == "/check":
            path = config.clean_path((parse_qs(url.query).get("path") or [""])[0])
            self._send("1" if path and os.path.isfile(path) else "0", "text/plain; charset=utf-8")
        elif url.path == "/setconfig":
            save_form(parse_qs(url.query, keep_blank_values=True))
            self._send(_REDIRECT)
        elif url.path == "/end":
            self._send(_render(_DONE_PAGE, css=_css()))
        elif url.path in ("", "/", "/index.html"):
            library = config.load_library()
            count = len(library["games"])
            self._send(_render(
                _INDEX_PAGE,
                css=_css(),
                rows=_rows(library["games"]),
                count="%d game%s" % (count, "" if count == 1 else "s"),
                name_max=str(config.NAME_MAX),
            ))
        else:
            self.send_error(404)

    def do_POST(self):
        if urlparse(self.path).path != "/setconfig":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0") or 0)
        except ValueError:
            length = 0
        raw = self.rfile.read(max(0, min(length, 1024 * 1024)))
        save_form(parse_qs(raw.decode("utf-8", "replace"), keep_blank_values=True))
        self._send(_REDIRECT)


class AuthenticationServer(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.httpd = HTTPServer(("localhost", 0), AuthenticationHandler)
        self.port = self.httpd.server_port

    def run(self):
        self.httpd.serve_forever()

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()
