import os
import json
import requests

SESSION_PATH = os.path.expanduser("~/Documents/Turing Sandbox Saves/Auth/session.json")
API_VERIFY_URL = "https://turingmachinesapi.onrender.com/players/verify"
VERIFY_SSL = False


def _ensure_dir():
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)


def save_session(token: str, user: dict):
    _ensure_dir()
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
            if not token:
                return None, None
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(API_VERIFY_URL, headers=headers, verify=VERIFY_SSL, timeout=3)

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


def is_logged_in():
    token, user = load_session()
    return bool(token and user.get("username"))

def get_username():
    _, user = load_session()
    return user.get("username") if user else None


def get_auth_headers():
    token, _ = load_session()
    return {"Authorization": f"Bearer {token}"} if token else {}
