import os, json, requests

from Level import Level


def get_save_dir(custom_levels=False):
    base = os.path.expanduser("~/Documents")
    path = os.path.join(base, "Turing Sandbox Saves")
    if custom_levels:
        path = os.path.join(path, "custom_levels")
    os.makedirs(path, exist_ok=True)
    return path

def list_saves():
    path = get_save_dir()
    saves = []
    for f in os.listdir(path):
        if f.endswith(".json"):
            full_path = os.path.join(path, f)
            try:
                with open(full_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    saves.append({"name": data.get("name", f[:-5]), "path": full_path})
            except Exception as e:
                print("Error reading save:", f, e)
    return sorted(saves, key=lambda s: s["name"])

def list_custom_levels():
    path = get_save_dir(custom_levels=True)
    levels = []
    for f in os.listdir(path):
        if f.endswith(".json"):
            full_path = os.path.join(path, f)
            try:
                with open(full_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    levels.append({
                        "name": data.get("name", f[:-5]),
                        "description": data.get("description", ""),
                        "path": full_path,
                        "data": data
                    })
            except Exception as e:
                print("Error reading custom level:", f, e)
    return sorted(levels, key=lambda s: s["name"])

def save_machine(name, data):
    path = os.path.join(get_save_dir(), f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return path

def load_machine(name):
    path = os.path.join(get_save_dir(), f"{name}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def delete_machine(name):
    path = os.path.join(get_save_dir(), f"{name}.json")
    if os.path.exists(path):
        os.remove(path)

def delete_progress():
    path = get_progress_path()
    if os.path.exists(path):
        os.remove(path)

def get_progress_path():
    base = os.path.expanduser(r"~/Documents/Turing Sandbox Saves/progress")
    os.makedirs(base, exist_ok=True)
    path = os.path.join(base, "turing_sandbox_progress.json")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)
    return path

def load_progress():
    path = get_progress_path()
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_progress(progress):
    path = get_progress_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=4)

def mark_level_complete(level_name, solution=None):
    progress = load_progress()
    progress[level_name] = {"completed": True}
    if solution:
        progress[level_name]["solution"] = solution
    save_progress(progress)

def is_level_complete(level_name):
    return load_progress().get(level_name, {}).get("completed", False)

def get_level_solution(level_name):
    return load_progress().get(level_name, {}).get("solution", None)

def serialize_level_to_string(level_data: dict) -> str:
    wrapper = {
        "version": 1,
        "game": "Turing Sandbox",
        "source": "Python",
        "data": level_data
    }

    try:
        return json.dumps(wrapper, ensure_ascii=False, separators=(",", ":"))
    except Exception as e:
        print(f"[serialize_level_to_string] Failed to encode JSON: {e}")
        return "{}"


def deserialize_level_from_string(level_source) -> Level:
    try:
        if isinstance(level_source, requests.Response):
            try:
                wrapper = level_source.json()
            except ValueError:
                wrapper = json.loads(level_source.text)

        elif isinstance(level_source, str):
            wrapper = json.loads(level_source)

        elif isinstance(level_source, dict):
            wrapper = level_source
        else:
            raise TypeError(f"Unsupported type for level_source: {type(level_source)}")

        if "levelData" in wrapper:
            inner_data = wrapper["levelData"]

            if isinstance(inner_data, str):
                try:
                    inner_data = json.loads(inner_data)
                except Exception:
                    pass
            if isinstance(inner_data, str) and inner_data.startswith("{"):
                try:
                    inner_data = json.loads(inner_data)
                except Exception:
                    pass

            if "data" in inner_data:
                inner_data = inner_data["data"]

            inner_data["level_type"] = inner_data.get("type", "Workshop")
            return Level.from_dict(inner_data)

    except Exception as e:
        print(f"[deserialize_level_from_string] Failed to decode JSON: {e}")
        return Level(name="Invalid Level", description="Failed to load", objective="N/A")



