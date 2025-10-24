import os, json, requests

from Level import Level


def get_save_dir(custom_levels=False, workshop_levels=False, workshop_machine=False):
    base = os.path.expanduser("~/Documents")
    path = os.path.join(base, "Turing Sandbox Saves")
    if custom_levels:
        path = os.path.join(path, "custom_levels")
    if workshop_levels:
        path = os.path.join(path, "workshop_levels")
    if workshop_machine:
        path = os.path.join(path, "workshop_machines")
    os.makedirs(path, exist_ok=True)
    return path

def list_saves(workshop_levels=False, workshop_machine=False):
    if workshop_levels:
        path = get_save_dir(workshop_levels=True)
    elif workshop_machine:
        path = get_save_dir(workshop_machine=True)
    else:
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

def load_machine(name, workshop=False):
    if workshop:
        path = os.path.join(get_save_dir(workshop_machine=True), f"{name}.json")
    else:
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

def save_workshop_level(level: Level):
    path = os.path.join(get_save_dir(workshop_levels=True), f"{level.name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(level.to_dict(), f, indent=4)


def save_workshop_machine(item):
    base_dir = get_save_dir(workshop_machine=True)
    name = getattr(item, "name", None)
    if not name and isinstance(item, dict):
        name = item.get("name", "Unnamed_Machine")
    if not name:
        name = "Unnamed_Machine"

    if hasattr(item, "serialize"):
        data = item.serialize(name)
    elif hasattr(item, "to_dict"):
        data = item.to_dict()
    elif isinstance(item, dict):
        data = item
    else:
        print("save_workshop_machine: unsupported item type", type(item))
        return None
    os.makedirs(base_dir, exist_ok=True)
    full_path = os.path.join(base_dir, f"{name}.json")
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return full_path

def delete_workshop_item(name, is_level=False):
    if is_level:
        path = os.path.join(get_save_dir(workshop_levels=True), f"{name}.json")
    else:
        path = os.path.join(get_save_dir(workshop_machine=True), f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
