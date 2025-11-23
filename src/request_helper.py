import os
import json
import requests
import TuringMachine
import Level
import urllib.parse

SESSION_PATH = os.path.expanduser("~/Documents/Turing Sandbox Saves/Auth/session.json")
WORKSHOP_DIR = os.path.expanduser("~/Documents/Turing Sandbox Saves/workshop")

# Render.com links

WORKSHOP_URL = "https://turingmachinesapi.onrender.com/workshop"
AUTH_URL = "https://turingmachinesapi.onrender.com/auth"
AUTH_POP_UP_URL = "https://turingmachinesapi.onrender.com/players"
AUTH_VERIFY_URL = "https://turingmachinesapi.onrender.com/players/verify"
LOBBY_URL = "https://turingmachinesapi.onrender.com/lobbies"
LEADERBOARD_URL = "https://turingmachinesapi.onrender.com/leaderboard"
VERIFY_SSL = True

# Localhost testing links:

#WORKSHOP_URL = "https://localhost:7054/workshop"
#AUTH_URL = "https://localhost:7054/auth"
#AUTH_POP_UP_URL = "https://localhost:7054/players"
#AUTH_VERIFY_URL = "https://localhost:7054/players/verify"
#LOBBY_URL = "https://localhost:7054/lobbies"
#LEADERBOARD_URL = "https://localhost:7054/leaderboard"
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
        r = requests.get(AUTH_VERIFY_URL, headers=headers, verify=VERIFY_SSL, timeout=7)

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
        r = requests.get(AUTH_VERIFY_URL, headers=headers, verify=VERIFY_SSL, timeout=7)
        if r.status_code == 200:
            verified = r.json()
            return verified.get("valid", False)
        elif r.status_code == 429:
            return False
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
                          verify=VERIFY_SSL, timeout=7)
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
                          verify=VERIFY_SSL, timeout=7)
        if r.status_code in (200, 201):
            return r.json()
        else:
            print(f"Registration failed ({r.status_code}): {r.text}")
    except Exception as e:
        print("Register failed:", e)
        print(e)
    return None

def delete_account(user_id: int):
    debug_requests("delete_account")
    try:
        token, user = load_session()
        if not token:
            print("No session token, cannot delete account")
            return False, "Not authenticated"

        headers = {"Authorization": f"Bearer {token}"}

        r = requests.delete(
            f"{AUTH_POP_UP_URL}/{user_id}",
            headers=headers,
            verify=VERIFY_SSL,
            timeout=7,
        )

        if r.status_code == 200:
            clear_session()
            return True, r.json().get("message", "Account deleted")

        elif r.status_code == 403:
            return False, "You do not have permission to delete this account."

        elif r.status_code == 404:
            return False, "Account not found."

        else:
            return False, f"Delete failed ({r.status_code}): {r.text}"

    except Exception as e:
        print("Delete failed:", e)
        return False, "Unexpected error"


def get_workshop_items(name_filter: str = None):
    debug_requests("get_workshop_items")
    workshop_items = {"LevelItems": [], "MachineItems": []}
    headers = get_auth_headers()
    params = {"NameFilter": name_filter} if name_filter else {}
    try:
        r = requests.get(WORKSHOP_URL, headers=headers, params=params, verify=VERIFY_SSL, timeout=7)
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
        r = requests.get(f"{WORKSHOP_URL}/{item_id}", headers=headers, verify=VERIFY_SSL, timeout=7)
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
        r = requests.post(WORKSHOP_URL, headers=headers, json=item_json, verify=VERIFY_SSL, timeout=7)
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
        r = requests.post(f"{WORKSHOP_URL}/{item_id}/rate/{rating}", headers=headers, verify=VERIFY_SSL, timeout=7)
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
        r = requests.post(f"{WORKSHOP_URL}/{item_id}/subscribe", headers=headers, verify=VERIFY_SSL, timeout=7)
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
        r = requests.get(f"{WORKSHOP_URL}/{item_id}/subscribed", headers=headers, verify=VERIFY_SSL, timeout=7)
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
        "wrongExamplesJson" : level.wrong_examples,
        "twoTapes" : level.double_tape
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

def submit_leaderboard(level_name: str, time_seconds: float, node_count: int, connection_count: int):
    debug_requests("submit_leaderboard")

    headers = get_auth_headers()
    if "Authorization" not in headers or not headers["Authorization"]:
        print("Not authenticated; cannot submit leaderboard.")
        return False, "Not authenticated"

    payload = {
        "levelName": level_name,
        "PlayerName": get_username(),
        "time": time_seconds,
        "nodeCount": node_count,
        "connectionCount": connection_count,
    }

    try:
        r = requests.post(
            LEADERBOARD_URL,
            headers=headers,
            json=payload,
            verify=VERIFY_SSL,
            timeout=7,
        )

        if r.status_code in (200, 201):
            try:
                return True, r.json()
            except ValueError:
                return True, None
        elif r.status_code == 400:
            msg = f"Invalid submission ({r.status_code}): {r.text}"
            print(msg)
            return False, msg
        elif r.status_code == 401:
            print("Authentication failed; clearing session.")
            clear_session()
            return False, "Authentication failed; please log in again."
        elif r.status_code == 429:
            msg = "Rate limited when submitting to leaderboard; try again later."
            print(msg)
            return False, msg
        else:
            msg = f"Leaderboard submit failed ({r.status_code}): {r.text}"
            print(msg)
            return False, msg

    except Exception as e:
        print("Leaderboard submission failed:", e)
        return False, "Unexpected error while submitting to leaderboard"


def get_leaderboard(level_name: str):
    debug_requests("get_leaderboard")
    headers = get_auth_headers()

    params = {
        "Player": "false",
        "levelName": level_name
    }

    try:
        r = requests.get(
            LEADERBOARD_URL,
            headers=headers,
            params=params,
            verify=VERIFY_SSL,
            timeout=7
        )

        if r.status_code == 200:
            return r.json()

        elif r.status_code == 429:
            print("Rate limit hit on leaderboard request")
            return None

        elif r.status_code == 401:
            print("Unauthorized while requesting leaderboard")
            return None

        else:
            print("Leaderboard bad status:", r.status_code, r.text)
            return None

    except Exception as e:
        print("Error requesting leaderboard:", e)
        return None

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
            "double_tape": item_json.get("twoTapes", False)
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

def get_username():
    user = get_user()
    if user:
        return user.get("username", "Unknown")
    return "Unknown"

def get_user_id():
    user = get_user()
    if user:
        return user.get("id", None)
    return None

def get_user_role():
    user = get_user()
    if user:
        return user.get("role", "User")
    return "User"

def delete_workshop_item(id):
    debug_requests("delete_workshop_item")
    headers = get_auth_headers()
    try:
        r = requests.delete(f"{WORKSHOP_URL}/{id}", headers=headers, verify=VERIFY_SSL, timeout=7)
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

def get_lobbies(include_started: bool = False):
    debug_requests("get_lobbies")
    headers = get_auth_headers()
    params = {"includeStarted": include_started}
    try:
        r = requests.get(LOBBY_URL, headers=headers, params=params, verify=VERIFY_SSL, timeout=7)
        if r.status_code == 200:
            return r.json()
        else:
            print(f"Failed to fetch lobbies (status {r.status_code})")
    except Exception as e:
        print("Failed to fetch lobbies:", e)
    return []

def create_lobby(selected_level_id: int, name: str, max_players: int  ,password: str = None):
    debug_requests("create_lobby")
    headers = get_auth_headers()
    params = {"selectedLevelId": selected_level_id, "name": name, "max_players": max_players}
    if password:
        params["password"] = password
    try:
        r = requests.post(LOBBY_URL, headers=headers, params=params, verify=VERIFY_SSL, timeout=7)
        if r.status_code in (200, 201):
            print("Lobby created successfully.")
            return r.json()
        else:
            print(f"Failed to create lobby (status {r.status_code}): {r.text}")
    except Exception as e:
        print("Create lobby failed:", e)
    return None

def join_lobby(code, password=None):
    debug_requests("join_lobby")
    headers = get_auth_headers()
    params = {"password": password} if password else {}
    try:
        r = requests.post(f"{LOBBY_URL}/{code}/join", headers=headers, params=params, verify=VERIFY_SSL, timeout=7)
        if r.status_code == 200:
            print(f"Joined lobby {code} successfully.")
            return True
        else:
            print(f"Failed to join lobby {code}: {r.status_code} {r.text}")
    except Exception as e:
        print("Join lobby failed:", e)
    return False

from signalrcore.hub_connection_builder import HubConnectionBuilder

hub_connection = None


def connect_signalr(on_lobby_created=None, on_player_joined=None, on_player_left=None, on_lobby_deleted=None,
                    on_player_kicked=None, on_lobby_started=None, on_environment_synced=None, on_node_proposed=None, on_connection_proposed=None,on_delete_proposed=None, on_chat_message_received=None):
    global hub_connection

    HUB_URL = LOBBY_URL.replace("/lobbies", "/hubs/lobby")

    try:
        headers = get_auth_headers()
        access_token = headers.get("Authorization", "").replace("Bearer ", "")
        query_str = f"?access_token={access_token}" if access_token else ""

        hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{HUB_URL}{query_str}", options={"verify_ssl": VERIFY_SSL})
            .build()
        )

        if on_lobby_created:
            hub_connection.on("LobbyCreated", lambda args: on_lobby_created(args[0]))
        if on_player_joined:
            hub_connection.on("PlayerJoined", lambda args: on_player_joined(args[0]))
        if on_player_left:
            hub_connection.on("PlayerLeft", lambda args: on_player_left(args[0]))
        if on_lobby_deleted:
            hub_connection.on("LobbyDeleted", lambda args: on_lobby_deleted(args[0]))
        if on_player_kicked:
            hub_connection.on("PlayerKicked", lambda args: on_player_kicked(args[0]))
        if on_lobby_started:
            hub_connection.on("LobbyStarted", lambda args: on_lobby_started(args[0]))
        if on_environment_synced:
            hub_connection.on("EnvironmentSynced", lambda args: on_environment_synced(args[0]))
        if on_node_proposed:
            hub_connection.on("NodeProposed", lambda args: on_node_proposed(args[0]))
        if on_connection_proposed:
            hub_connection.on("ConnectionProposed", lambda args: on_connection_proposed(args[0]))
        if on_delete_proposed:
            hub_connection.on("DeleteProposed", lambda args: on_delete_proposed(args[0]))
        if on_chat_message_received:
            hub_connection.on("ChatMessageReceived", lambda args: on_chat_message_received(args[0]))

        hub_connection.start()
        print("Connected to LobbyHub SignalR")

    except Exception as e:
        print("Failed to connect to SignalR hub:", e)


def leave_lobby(code):
    debug_requests("leave_lobby")
    headers = get_auth_headers()
    try:
        r = requests.post(f"{LOBBY_URL}/{code}/leave", headers=headers, verify=VERIFY_SSL, timeout=7)
        if r.status_code == 200:
            print(f"Left lobby {code}")
            return True
        else:
            print(f"Failed to leave lobby {code}: {r.status_code} {r.text}")
    except Exception as e:
        print("Leave lobby failed:", e)
    return False

def kick_player(code, player_name):
    try:
        headers = get_auth_headers()
        safe_name = urllib.parse.quote(player_name)
        resp = requests.post(f"{LOBBY_URL}/{code}/kick/{safe_name}", headers=headers)
        print("Kick response:", resp.status_code, resp.text)
        if resp.status_code != 200:
            return False
        data = resp.json() if resp.text else {}
        msg = data.get("message", "").lower()
        return "kicked" in msg or "success" in msg
    except Exception as e:
        print(f"Error kicking player: {e}")
        return False


def join_signalr_group(code: str):
    global hub_connection
    if hub_connection:
        try:
            hub_connection.send("JoinLobbyGroup", [code])
            print(f"[SignalR] Joined group {code}")
        except Exception as e:
            print(f"[SignalR] Failed to join group {code}: {e}")


def leave_signalr_group(code: str):
    global hub_connection
    if hub_connection:
        try:
            hub_connection.send("LeaveLobbyGroup", [code])
            print(f"[SignalR] Left group {code}")
        except Exception as e:
            print(f"[SignalR] Failed to leave group {code}: {e}")

def disconnect_signalr():
    global hub_connection
    if hub_connection:
        try:
            hub_connection.stop()
            print("Disconnected from LobbyHub")
        except Exception as e:
            print("Error disconnecting SignalR:", e)
        finally:
            hub_connection = None

def start_lobby(code):
    try:
        headers = get_auth_headers()
        resp = requests.post(f"{LOBBY_URL}/{code}/start", headers=headers, verify=VERIFY_SSL)
        print("Start lobby response:", resp.status_code, resp.text)
        if resp.status_code != 200:
            return False
        return True
    except Exception as e:
        print(f"Error starting lobby: {e}")
        return False


def send_environment_state(lobby_code, state):
    if hub_connection:
        payload = {"lobbyCode": lobby_code, "state": state}
        print(f"[SignalR] Sending environment state → {payload.keys()}")
        hub_connection.send("SyncEnvironment", [payload])
        print("[SignalR] Sent environment state")

def propose_node(lobby_code, pos, is_end):
    if hub_connection:
        payload = {
            "lobbyCode": lobby_code,
            "pos": {"x": pos.x, "y": pos.y},
            "isEnd": is_end
        }
        hub_connection.send("ProposeNode", [payload])
        print(f"[SignalR] Sent node proposal: {payload}")

def propose_connection(data):
    if hub_connection:
        hub_connection.send("ProposeConnection", [data])
        print(f"[SignalR] Sent connection proposal → {data}")

def propose_delete(lobby_code, target_data):
    if hub_connection:
        payload = {"lobbyCode": lobby_code, "target": target_data}
        hub_connection.send("ProposeDelete", [payload])
        print(f"[SignalR] Sent delete proposal → {payload.keys()}")

def send_chat_message(lobby_code, sender, message):
    if not hub_connection:
        return
    payload = {"lobbyCode": lobby_code, "sender": sender, "message": message}
    hub_connection.send("SendChatMessage", [payload])

import pygame
UPDATE_EVENT = pygame.USEREVENT + 1

def trigger_event():
    pygame.event.post(pygame.event.Event(UPDATE_EVENT))

