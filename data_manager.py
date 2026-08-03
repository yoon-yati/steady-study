# data_manager.py - Persistent Storage
import json
import os
import streamlit as st
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

def load_users_db():
    """Load users database from JSON file"""
    users_file = PROJECT_ROOT / "users_db.json"
    if users_file.exists():
        try:
            with open(users_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error loading users_db.json: {e}")
            return {}
    return {}

def save_users_db(users_data):
    """Save users database to JSON file"""
    users_file = PROJECT_ROOT / "users_db.json"
    try:
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"Error saving users_db.json: {e}")
        return False

def load_plans_db():
    """Load plans database from JSON file"""
    plans_file = PROJECT_ROOT / "plans_db.json"
    if plans_file.exists():
        try:
            with open(plans_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error loading plans_db.json: {e}")
            return {}
    return {}

def save_plans_db(plans_data):
    """Save plans database to JSON file"""
    plans_file = PROJECT_ROOT / "plans_db.json"
    try:
        with open(plans_file, "w", encoding="utf-8") as f:
            json.dump(plans_data, f, indent=2, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"Error saving plans_db.json: {e}")
        return False

def save_plan_for_user(username: str, plan: dict):
    if username not in st.session_state["plans_db"]:
        st.session_state["plans_db"][username] = []
    st.session_state["plans_db"][username].append(plan)
    save_plans_db(st.session_state["plans_db"])

def get_plans_for_user(username):
    """Get plans for specific user"""
    plans_db = load_plans_db()
    return plans_db.get(username, [])

def save_session(username: str):
    try:
        with open("session.json", "w") as f:
            json.dump({"username": username}, f)
    except Exception:
        pass

def clear_session():
    try:
        if os.path.exists("session.json"):
            os.remove("session.json")
    except Exception:
        pass