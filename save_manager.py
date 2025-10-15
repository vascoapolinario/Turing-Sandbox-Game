import os, json
import platform


def get_save_dir():
    if platform.system() == "Emscripten":
        base = "/saves"
    else:
        base = os.path.expanduser("~/Documents")
    path = os.path.join(base, "Turing Sandbox Saves")
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
    if platform.system() == "Emscripten":
        base = "/saves"
    else:
        base = os.path.expanduser("~\Documents\Turing Sandbox Saves\progress")

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
