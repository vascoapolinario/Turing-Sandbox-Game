import json

from Level import Level

# Browser localStorage key prefixes
_PREFIX_SAVE = "turing_save_"
_PREFIX_CUSTOM = "turing_custom_level_"
_KEY_PROGRESS = "turing_progress"


def _ls_get(key):
    try:
        import js
        val = js.localStorage.getItem(key)
        return str(val) if val is not None else None
    except Exception:
        return None


def _ls_set(key, value):
    try:
        import js
        js.localStorage.setItem(key, value)
    except Exception:
        pass


def _ls_remove(key):
    try:
        import js
        js.localStorage.removeItem(key)
    except Exception:
        pass


def _ls_keys():
    try:
        import js
        return [js.localStorage.key(i) for i in range(js.localStorage.length)]
    except Exception:
        return []


# ── Machine saves ──────────────────────────────────────────────────────────────

def list_saves(workshop_levels=False, workshop_machine=False):
    if workshop_levels or workshop_machine:
        return []
    saves = []
    for key in _ls_keys():
        if key and key.startswith(_PREFIX_SAVE):
            raw = _ls_get(key)
            if raw:
                try:
                    data = json.loads(raw)
                    name = data.get("name", key[len(_PREFIX_SAVE):])
                    saves.append({"name": name, "path": key})
                except Exception:
                    pass
    return sorted(saves, key=lambda s: s["name"])


def save_machine(name, data):
    _ls_set(_PREFIX_SAVE + name, json.dumps(data))
    return _PREFIX_SAVE + name


def load_machine(name, workshop=False):
    if workshop:
        return {}
    raw = _ls_get(_PREFIX_SAVE + name)
    if raw is None:
        raise FileNotFoundError(f"Save not found: {name}")
    return json.loads(raw)


def delete_machine(name):
    _ls_remove(_PREFIX_SAVE + name)


# ── Custom levels ──────────────────────────────────────────────────────────────

def list_custom_levels():
    levels = []
    for key in _ls_keys():
        if key and key.startswith(_PREFIX_CUSTOM):
            raw = _ls_get(key)
            if raw:
                try:
                    data = json.loads(raw)
                    levels.append({
                        "name": data.get("name", key[len(_PREFIX_CUSTOM):]),
                        "description": data.get("description", ""),
                        "path": key,
                        "data": data,
                    })
                except Exception:
                    pass
    return sorted(levels, key=lambda s: s["name"])


def save_custom_level_data(name, data):
    _ls_set(_PREFIX_CUSTOM + name, json.dumps(data))


def delete_custom_level(name):
    _ls_remove(_PREFIX_CUSTOM + name)


# ── Progress ───────────────────────────────────────────────────────────────────

def load_progress():
    raw = _ls_get(_KEY_PROGRESS)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def save_progress(progress):
    _ls_set(_KEY_PROGRESS, json.dumps(progress))


def delete_progress():
    _ls_remove(_KEY_PROGRESS)


def mark_level_complete(level_name, solution=None, time=None):
    progress = load_progress()
    progress[level_name] = {"completed": True}
    if solution:
        progress[level_name]["solution"] = solution
    if time is not None:
        time = round(time, 1)
        progress[level_name]["time"] = time
    save_progress(progress)


def is_level_complete(level_name):
    return load_progress().get(level_name, {}).get("completed", False)


def get_level_solution(level_name):
    return load_progress().get(level_name, {}).get("solution", None)


def get_level_completion_time(level_name):
    return load_progress().get(level_name, {}).get("time", None)


def get_level_stats(level_name):
    progress = load_progress().get(level_name, {})
    solution = progress.get("solution", {})
    num_nodes = len(solution.get("nodes", []))
    num_connections = len(solution.get("connections", []))
    return {
        "completed": progress.get("completed", False),
        "time": progress.get("time", None),
        "num_nodes": num_nodes,
        "num_connections": num_connections,
    }


# ── Workshop stubs (no workshop on web) ───────────────────────────────────────

def save_workshop_level(level: Level):
    pass


def save_workshop_machine(item):
    return None


def delete_workshop_item(name, is_level=False):
    pass
