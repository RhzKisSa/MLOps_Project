import json
import uuid
import os

CHAT_SESSION_DIR = "./data/chat_sessions"
os.makedirs(CHAT_SESSION_DIR, exist_ok=True)

def load_history(session_id):
    path = os.path.join(CHAT_SESSION_DIR, f"{session_id}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("history", [])
    return []

def save_history(session_id, history):
    path = os.path.join(CHAT_SESSION_DIR, f"{session_id}.json")
    data = {
        "session_id": session_id,
        "history": history
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
