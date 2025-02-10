import json
import os

current_path = os.path.dirname(__file__)
chat_history_path = os.path.join(current_path, 'chat_history.json')

def load_history():
    with open(chat_history_path, "r", encoding="utf-8") as f:
        history = json.load(f)
    return history

def save_history(history):
    with open(chat_history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
