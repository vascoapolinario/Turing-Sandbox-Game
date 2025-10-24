import os
import json
import requests
import TuringMachine
import Level

SESSION_PATH = os.path.expanduser("~/Documents/Turing Sandbox Saves/Auth/session.json")
WORKSHOP_DIR = os.path.expanduser("~/Documents/Turing Sandbox Saves/workshop")

# Render.com links

WORKSHOP_URL = "https://turingmachinesapi.onrender.com/workshop"
AUTH_URL = "https://turingmachinesapi.onrender.com/auth"
AUTH_POP_UP_URL = "https://turingmachinesapi.onrender.com/players"
AUTH_VERIFY_URL = "https://turingmachinesapi.onrender.com/players/verify"
VERIFY_SSL = True

# Localhost testing links:

#WORKSHOP_URL = "https://localhost:7054/workshop"
#AUTH_URL = "https://localhost:7054/auth"
#AUTH_POP_UP_URL = "https://localhost:7054/players"
#AUTH_VERIFY_URL = "https://localhost:7054/players/verify"
#VERIFY_SSL = False





def save_session(token: str, user: dict):
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    with open(SESSION_PATH, "w", encoding="utf-8") as f:
        json.dump({"token": token, "user": user}, f, indent=2)


def load_session():
    if not os.path.exists(SESSION_PATH):
        return None, None
    try:
        with open(SESSION_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            token = data.get("token")
            user = data.get("user", {})
            if token is not None and user is not None:

                return token, user
        headers = {"Authorization": f"Bearer {token}"}
        debug_requests("load_session")
        r = requests.get(AUTH_VERIFY_URL, headers=headers, verify=VERIFY_SSL, timeout=3)

        if r.status_code == 200:
            verified = r.json()
            verified_user = verified.get("user", {})
            if verified.get("valid") and verified_user.get("username"):
                save_session(token, verified_user)
                return token, verified_user
        elif r.status_code == 429:
            print("Rate limited while verifying token; assuming valid.")
            return token, user
        else:
            print(f"Token invalid (status {r.status_code}), clearing session.")
            clear_session()
            return None, None
    except Exception as e:
        print("Session verification failed:", e)
        clear_session()
    return None, None


def clear_session():
    if os.path.exists(SESSION_PATH):
        os.remove(SESSION_PATH)


def get_auth_headers():
    token, _ = load_session()
    return {"Authorization": f"Bearer {token}"} if token else {}

def verify_authentication():
    debug_requests("verify_authentication")
    token, user = load_session()
    if not token:
        return False
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(AUTH_VERIFY_URL, headers=headers, verify=VERIFY_SSL, timeout=3)
        if r.status_code == 200:
            verified = r.json()
            return verified.get("valid", False)
        elif r.status_code == 429:
            print("Rate limited while verifying token; assuming valid.")
            return True
        else:
            print(f"Token invalid (status {r.status_code}), clearing session.")
            clear_session()
            return False
    except Exception as e:
        print("Session verification failed:", e)
        clear_session()


def login_user(username: str, password: str):
    debug_requests("login_user")
    try:
        r = requests.post(f"{AUTH_POP_UP_URL}/login",
                          json={"username": username, "password": password},
                          verify=VERIFY_SSL, timeout=5)
        if r.status_code == 200:
            data = r.json()
            token = data.get("token")
            user = data.get("user", {})
            if token and user:
                save_session(token, user)
                return token, user
    except Exception as e:
        print("Login failed:", e)
    return None, None


def register_user(username: str, password: str):
    debug_requests("register_user")
    try:
        r = requests.post(f"{AUTH_POP_UP_URL}",
                          json={"username": username, "password": password},
                          verify=VERIFY_SSL, timeout=5)
        if r.status_code in (200, 201):
            return r.json()
        else:
            print(f"Registration failed ({r.status_code}): {r.text}")
    except Exception as e:
        print("Register failed:", e)
        print(e)
    return None


def get_workshop_items(name_filter: str = None):
    debug_requests("get_workshop_items")
    workshop_items = {"LevelItems": [], "MachineItems": []}
    headers = get_auth_headers()
    params = {"NameFilter": name_filter} if name_filter else {}
    try:
        r = requests.get(WORKSHOP_URL, headers=headers, params=params, verify=VERIFY_SSL, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(data)
            for item in data:
                if item.get("type") == "Level":
                    workshop_items["LevelItems"].append(item)
                elif item.get("type") == "Machine":
                    workshop_items["MachineItems"].append(item)
            return workshop_items
        else:
            print(f"Failed to fetch workshop items (status {r.status_code})")
    except Exception as e:
        print("Failed to fetch workshop items:", e)
    return workshop_items


def get_workshop_item_by_id(item_id: int):
    debug_requests("get_workshop_item_by_id")
    headers = get_auth_headers()
    try:
        r = requests.get(f"{WORKSHOP_URL}/{item_id}", headers=headers, verify=VERIFY_SSL, timeout=5)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            print(f"Workshop item {item_id} not found.")
        else:
            print(f"Failed to get item {item_id}: {r.status_code}")
    except Exception as e:
        print("Failed to get workshop item:", e)
    return None


def create_workshop_item(item_json):
    debug_requests("create_workshop_item")
    headers = get_auth_headers()
    headers["Content-Type"] = "application/json"
    try:
        r = requests.post(WORKSHOP_URL, headers=headers, json=item_json, verify=VERIFY_SSL, timeout=5)
        if r.status_code in (200, 201):
            return r.json()
        else:
            print(f"Failed to create item (status {r.status_code}): {r.text}")
    except Exception as e:
        print("Error creating workshop item:", e)
    return None


def rate_workshop_item(item_id: int, rating: int):
    debug_requests("rate_workshop_item")
    if rating < 1 or rating > 5:
        print("Rating must be between 1 and 5.")
        return False

    headers = get_auth_headers()
    try:
        r = requests.post(f"{WORKSHOP_URL}/{item_id}/rate/{rating}", headers=headers, verify=VERIFY_SSL, timeout=5)
        if r.status_code == 200:
            print("Rating submitted successfully.")
            return True
        elif r.status_code == 404:
            print("Workshop item not found.")
        elif r.status_code == 400:
            print("Invalid rating request.")
        else:
            print(f"Failed to rate item (status {r.status_code})")
    except Exception as e:
        print("Failed to rate workshop item:", e)
    return False


def toggle_subscription(item_id: int):
    debug_requests("toggle_subscription")
    headers = get_auth_headers()
    try:
        r = requests.post(f"{WORKSHOP_URL}/{item_id}/subscribe", headers=headers, verify=VERIFY_SSL, timeout=5)
        if r.status_code == 200:
            print("Subscription toggled successfully.")
            return True
        elif r.status_code == 404:
            print("Workshop item not found.")
        else:
            print(f"Failed to toggle subscription (status {r.status_code})")
    except Exception as e:
        print("Failed to toggle subscription:", e)
    return False


def is_subscribed(item_id: int):
    debug_requests("is_subscribed")
    headers = get_auth_headers()
    try:
        r = requests.get(f"{WORKSHOP_URL}/{item_id}/subscribed", headers=headers, verify=VERIFY_SSL, timeout=5)
        if r.status_code == 200:
            return r.json() if r.text.strip().lower() in ["true", "false"] else bool(r.json())
        elif r.status_code == 404:
            print("Workshop item not found.")
        else:
            print(f"Failed to check subscription (status {r.status_code})")
    except Exception as e:
        print("Failed to check subscription:", e)
    return False

def upload_level(level):
    debug_requests("upload_level")
    RequestJson = {
        "name" : level.name,
        "description" : level.description,
        "detailedDescription" : level.detailed_description,
        "objective" : level.objective,
        "type" : "Level",
        "mode" : level.mode,
        "alphabetJson" : level.alphabet,
        "transformTestsJson" : level.transform_tests,
        "correctExamplesJson" : level.correct_examples,
        "wrongExamplesJson" : level.wrong_examples
    }
    return create_workshop_item(RequestJson)

def upload_machine(machine):
    debug_requests("upload_machine")

    if isinstance(machine, dict):
        name = machine.get("name")
        description = machine.get("description", "")
        alphabet = machine.get("alphabet", ["_"])
        nodes = machine.get("nodes", [])
        connections = machine.get("connections", [])
    else:
        name = getattr(machine, "name", "Unnamed Machine")
        description = getattr(machine, "description", "")
        alphabet = getattr(machine, "alphabet", ["_"])
        nodes = getattr(machine, "nodes", [])
        connections = getattr(machine, "connections", [])

    RequestJson = {
        "name": name,
        "description": description,
        "type": "Machine",
        "alphabetJson": alphabet,
        "nodesJson": nodes,
        "connectionsJson": connections
    }
    return create_workshop_item(RequestJson)

def workshopitem_to_object(item_json):
    item_type = item_json.get("type")

    def ensure_parsed(value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return []
        return value or []

    if item_type == "Level":
        level_data = {
            "name": item_json.get("name", "Unnamed Level"),
            "level_type": "Workshop",
            "description": item_json.get("description", ""),
            "detailedDescription": item_json.get("detailedDescription", ""),
            "alphabet": ensure_parsed(item_json.get("alphabetJson")),
            "objective": item_json.get("objective", ""),
            "mode": item_json.get("mode", "Normal"),
            "transform_tests": ensure_parsed(item_json.get("transformTestsJson")),
            "correct_examples": ensure_parsed(item_json.get("correctExamplesJson")),
            "wrong_examples": ensure_parsed(item_json.get("wrongExamplesJson")),
            "double_tape": item_json.get("doubleTape", False)
        }
        return Level.Level.from_dict(level_data)

    elif item_type == "Machine":
        machine_data = {
            "name": item_json.get("name", "Unnamed Machine"),
            "description": item_json.get("description", ""),
            "alphabet": ensure_parsed(item_json.get("alphabetJson")),
            "nodes": ensure_parsed(item_json.get("nodesJson")),
            "connections": ensure_parsed(item_json.get("connectionsJson"))
        }
        return TuringMachine.TuringMachine.from_dict(machine_data)

    else:
        print(f"Unknown workshop item type: {item_type}")
        return None

def debug_requests(request_name):
    print("[Request Debug] Called:", request_name)


def is_authenticated():
    try:
        with open(SESSION_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            token = data.get("token")
            user = data.get("user", {})
            if token is not None and user is not None:
                return True
    except Exception:
        return False

def get_user():
    try:
        with open(SESSION_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            user = data.get("user", {})
            return user
    except Exception:
        return None

def delete_workshop_item(id):
    debug_requests("delete_workshop_item")
    headers = get_auth_headers()
    try:
        r = requests.delete(f"{WORKSHOP_URL}/{id}", headers=headers, verify=VERIFY_SSL, timeout=5)
        if r.status_code == 200:
            print("Workshop item deleted successfully.")
            return True
        elif r.status_code == 404:
            print("Workshop item not found.")
        else:
            print(f"Failed to delete workshop item (status {r.status_code})")
    except Exception as e:
        print("Failed to delete workshop item:", e)
    return False