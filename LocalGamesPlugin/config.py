"""library.json: the games the user added. Everything is stored locally."""
import json
import logging
import os
import shlex
import tempfile
import uuid

PLUGIN_DIR = r"%LOCALAPPDATA%\GOG.com\Galaxy\Configuration\plugins\localgames"
LIBRARY_LOC = PLUGIN_DIR + r"\library.json"
GAME_TIMES_LOC = PLUGIN_DIR + r"\game_times.json"

NAME_MAX = 30         # longest game name kept (longer names break the layout and rarely match a cover anyway)
ID_PREFIX = "LOCAL-"
MAX_GAMES = 500


def expand(location):
    return os.path.expandvars(location)


def clean_path(value):
    """Trim spaces and the quotes Windows adds with 'Copy as path'."""
    return (value or "").strip().strip('"').strip()


def new_game_id():
    return ID_PREFIX + uuid.uuid4().hex[:12].upper()


def _text(value):
    return value.strip() if isinstance(value, str) else ""


def _clean_game(raw):
    """One game record from the file, or None when it is unusable. Never raises."""
    if not isinstance(raw, dict):
        return None
    game = {
        "id": _text(raw.get("id")),
        "name": _text(raw.get("name")),
        "exe": clean_path(raw.get("exe") if isinstance(raw.get("exe"), str) else ""),
        "args": _text(raw.get("args")),
        "workdir": clean_path(raw.get("workdir") if isinstance(raw.get("workdir"), str) else ""),
    }
    if not game["exe"]:
        return None
    if not game["name"]:
        game["name"] = os.path.splitext(os.path.basename(game["exe"].replace("\\", "/")))[0] or game["exe"]
    game["name"] = game["name"][:NAME_MAX].strip()
    if not game["id"]:
        game["id"] = new_game_id()
    return game


def load_library():
    """{"games": [..]}. A missing or broken file just yields an empty library."""
    library = {"games": []}
    path = expand(LIBRARY_LOC)
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
        try:
            value = json.loads(raw.decode("utf-8-sig"))
        except UnicodeDecodeError:
            value = json.loads(raw.decode("cp1252", errors="replace"))
    except FileNotFoundError:
        return library
    except (OSError, ValueError):
        logging.exception("DEV: could not read library.json, starting with an empty library")
        return library
    if not isinstance(value, dict):
        return library
    seen = set()
    for raw_game in value.get("games") if isinstance(value.get("games"), list) else []:
        game = _clean_game(raw_game)
        if game is None or game["id"] in seen:
            continue
        seen.add(game["id"])
        library["games"].append(game)
    return library


def save_library(library):
    target = expand(LIBRARY_LOC)
    directory = os.path.dirname(target)
    os.makedirs(directory, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix="library_", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(library, fh, ensure_ascii=False, indent=4)
        os.replace(temp, target)
    finally:
        if os.path.exists(temp):
            try:
                os.unlink(temp)
            except OSError:
                pass


def split_args(text):
    """Launch arguments as a list. Quoted parts stay together; quotes are removed."""
    try:
        return [token.strip('"') for token in shlex.split(text or "", posix=False)]
    except ValueError:
        return (text or "").split()
