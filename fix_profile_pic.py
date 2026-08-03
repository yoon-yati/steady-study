# fix_profile_pic.py - Run this once to fix broken profile pictures

import json
import re

def is_valid_base64_image(data):
    """Check if profile picture data is valid"""
    if not data or not isinstance(data, str):
        return False
    if not data.startswith("data:image/"):
        return False
    try:
        header, encoded = data.split(",", 1)
        if len(encoded) < 100:
            return False
        # Check if it has valid base64 characters
        if not re.match(r'^[A-Za-z0-9+/]+=*$', encoded):
            return False
        return True
    except:
        return False

# Load users_db.json
try:
    with open("users_db.json", "r", encoding="utf-8") as f:
        users_db = json.load(f)
except FileNotFoundError:
    print("users_db.json not found!")
    exit()

# Fix broken profile pictures
fixed_count = 0
for username, user_data in users_db.items():
    profile = user_data.get("profile", {})
    profile_pic = profile.get("profile_pic")
    
    if profile_pic and not is_valid_base64_image(profile_pic):
        print(f"Fixing broken profile picture for: {username}")
        profile["profile_pic"] = None
        fixed_count += 1

# Save fixed data
if fixed_count > 0:
    with open("users_db.json", "w", encoding="utf-8") as f:
        json.dump(users_db, f, indent=2, ensure_ascii=False)
    print(f"✅ Fixed {fixed_count} broken profile pictures!")
else:
    print("✅ No broken profile pictures found!")