import os, json

def get_save_dir():
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
