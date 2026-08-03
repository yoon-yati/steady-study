# settings.py - Settings Page (Fixed - CSS removed, uses app.py gradient)
"""Settings page for Smart Study Planner."""

import base64
import datetime
import io
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent


def save_users() -> None:
    """Save users through the project's data layer when possible."""
    users = st.session_state.get("users_db", {})

    try:
        from data_manager import save_users_db
        save_users_db(users)
        return
    except (ImportError, TypeError, AttributeError):
        pass
    except Exception as error:
        print("save_users_db error:", error)

    candidate_files = [
        PROJECT_ROOT / "users_db.json",
        PROJECT_ROOT / "users.json",
    ]
    target = next((path for path in candidate_files if path.exists()), candidate_files[0])

    try:
        target.write_text(
            json.dumps(users, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as error:
        st.error(f"Could not save account information: {error}")


def ensure_user(username: str) -> dict:
    users = st.session_state.setdefault("users_db", {})
    user = users.setdefault(username, {})
    profile = user.setdefault("profile", {})
    profile.setdefault("name", username)
    profile.setdefault("bio", "Study Planner learner")
    profile.setdefault("email", user.get("email", ""))
    profile.setdefault("social", {})
    profile.setdefault("theme", "Light")
    profile.setdefault("notifications", True)
    profile.setdefault("study_hours", "4:00")
    profile.setdefault("start_time", "09:00")
    profile.setdefault("profile_pic", None)
    return user


def get_profile_picture(username: str) -> str:
    """Get profile picture from session state or users_db."""
    if st.session_state.get("profile_pic"):
        return st.session_state["profile_pic"]
    
    users = st.session_state.get("users_db", {})
    if username in users:
        profile = users[username].get("profile", {})
        pic = profile.get("profile_pic")
        if pic:
            st.session_state["profile_pic"] = pic
            return pic
    return None


def initials(name: str) -> str:
    words = [word for word in str(name).split() if word]
    return "".join(word[0].upper() for word in words[:2]) or "U"


def valid_email(value: str) -> bool:
    return not value or re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value) is not None


def valid_url(value: str) -> bool:
    if not value.strip():
        return True
    result = urlparse(value.strip())
    return result.scheme in {"http", "https"} and bool(result.netloc)


def section_title(number: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:11px;margin:7px 0 14px;">'
        f'<div style="display:grid;width:29px;height:29px;place-items:center;border-radius:8px;background:linear-gradient(135deg,#4f8dff,#6c5ce7);color:white;font-size:12px;font-weight:800;">{number}</div>'
        f'<div><strong style="display:block;color:#183153;font-size:18px;">{title}</strong><small style="display:block;margin-top:2px;color:#7b8797;font-size:12px;">{subtitle}</small></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def dashboard_back() -> None:
    st.session_state["current_page"] = "home"
    st.session_state["dashboard_action"] = "home"
    try:
        st.query_params["page"] = "home"
    except Exception:
        pass
    st.rerun()


def profile_card(username: str, profile: dict) -> None:
    name = profile.get("name") or username
    picture = get_profile_picture(username)

    if picture:
        avatar = f'<div style="width:82px;height:82px;min-width:82px;border-radius:50%;background:linear-gradient(135deg,#4f8dff,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:700;color:white;overflow:hidden;border:4px solid rgba(255,255,255,0.5);box-shadow:0 10px 24px rgba(79,141,255,0.22);"><img src="{picture}" alt="Profile picture" style="width:100%;height:100%;object-fit:cover;"></div>'
    else:
        avatar = f'<div style="width:82px;height:82px;min-width:82px;border-radius:50%;background:linear-gradient(135deg,#4f8dff,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:700;color:white;overflow:hidden;border:4px solid rgba(255,255,255,0.5);box-shadow:0 10px 24px rgba(79,141,255,0.22);">{initials(name)}</div>'

    notifications = "Reminders on" if profile.get("notifications", True) else "Reminders off"

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:18px;padding:21px;margin-bottom:16px;border:1px solid rgba(255,255,255,0.3);border-radius:16px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">'
        f'{avatar}'
        f'<div>'
        f'<h3 style="margin:0;color:#183153;font-size:21px;">{name}</h3>'
        f'<p style="margin:4px 0 0;color:#7b8797;font-size:13px;">{profile.get("bio") or "Study Planner learner"}</p>'
        f'<div style="display:flex;gap:7px;flex-wrap:wrap;margin-top:9px;">'
        f'<span style="display:inline-flex;padding:5px 9px;border-radius:999px;background:#f0f4fe;color:#4f8dff;font-size:11px;font-weight:750;">Learner account</span>'
        f'<span style="display:inline-flex;padding:5px 9px;border-radius:999px;background:#d5f5e3;color:#27ae60;font-size:11px;font-weight:750;">{notifications}</span>'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def save_profile_image(username: str, uploaded_file) -> None:
    """Save profile image with proper base64 encoding"""
    try:
        image = Image.open(uploaded_file).convert("RGB")
        image.thumbnail((300, 300))
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85, optimize=True)
        image_bytes = buffer.getvalue()
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        image_data = f"data:image/jpeg;base64,{encoded_image}"
        
        user = ensure_user(username)
        user["profile"]["profile_pic"] = image_data
        st.session_state["profile_pic"] = image_data
        save_users()
        set_settings_alert("Profile", "success", "Profile picture updated successfully.")
        st.rerun()
        
    except Exception as error:
        st.error(f"The image could not be processed: {error}")
        print(f"Profile image save error: {error}")


def set_settings_alert(section: str, kind: str, message: str) -> None:
    st.session_state["settings_inline_alert"] = {
        "section": section,
        "kind": kind,
        "message": message,
    }


def render_settings_alert(section: str) -> None:
    alert = st.session_state.get("settings_inline_alert", {})
    if alert.get("section") != section:
        return

    kind = alert.get("kind", "info")
    message = alert.get("message", "")
    icons = {"success": "✓", "error": "✗", "warning": "⚠", "info": "ℹ"}
    icon = icons.get(kind, "ℹ")
    
    colors = {
        "success": "border-color:#d5f5e3;background:#f0faf5;color:#27ae60;",
        "error": "border-color:#fde8e8;background:#fdf0f0;color:#e74c3c;",
        "warning": "border-color:#fdebd0;background:#fef9e7;color:#e67e22;",
        "info": "border-color:#d6e4ff;background:#f0f4fe;color:#4f8dff;"
    }
    bg_colors = {
        "success": "background:#27ae60;",
        "error": "background:#e74c3c;",
        "warning": "background:#e67e22;",
        "info": "background:#4f8dff;"
    }
    
    st.markdown(
        f'<div style="display:flex;align-items:flex-start;gap:11px;margin:0 0 15px;padding:13px 15px;border:1px solid;border-radius:11px;font-size:13px;line-height:1.45;{colors.get(kind, colors["info"])}">'
        f'<span style="display:grid;width:23px;height:23px;min-width:23px;place-items:center;border-radius:50%;color:white;font-weight:800;{bg_colors.get(kind, bg_colors["info"])}">{icon}</span>'
        f'<div><strong>{message}</strong></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.session_state.pop("settings_inline_alert", None)


def profile_completion(profile: dict, user: dict) -> int:
    checks = [
        bool(profile.get("name")),
        bool(profile.get("bio")),
        bool(profile.get("email") or user.get("email")),
        bool(profile.get("profile_pic")),
        any(bool(value) for value in profile.get("social", {}).values()),
        bool(profile.get("study_hours")),
        bool(profile.get("start_time")),
    ]
    return round(sum(checks) / len(checks) * 100)


def show_settings_page() -> None:
    """Render the Settings workspace."""

    if not st.session_state.get("logged_in", False):
        st.warning("Please sign in to manage account settings.")
        return

    username = str(st.session_state.get("username") or "User")
    user = ensure_user(username)
    profile = user["profile"]
    completion = profile_completion(profile, user)

    # ===== FONT AWESOME CDN =====
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    """, unsafe_allow_html=True)

    # ===== HEADER WITH WELCOME BOX =====
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    picture = get_profile_picture(username)
    if picture:
        avatar_html = f'<img src="{picture}" alt="Profile" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">'
    else:
        avatar_html = username[0].upper()

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:12px;">
        <div style="display:flex;align-items:center;gap:16px;flex:1;">
            <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:12px 20px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.10);display:flex;align-items:center;gap:12px;flex:1;backdrop-filter:blur(12px);">
                <div style="width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#4f8dff,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700;color:white;flex-shrink:0;overflow:hidden;border:2px solid rgba(255,255,255,0.5);">
                    {avatar_html}
                </div>
                <div style="flex:1;">
                    <div style="font-size:18px;font-weight:700;color:#183153;margin:0;">⚙️ Settings</div>
                    <div style="font-size:13px;color:#5a6a7e;margin:2px 0 0 0;">{greeting}, <span style="color:#4f8dff;font-weight:600;">{username}</span>! Manage your account and preferences.</div>
                </div>
                <div style="background:rgba(248,250,255,0.7);padding:6px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.3);font-size:12px;color:#5a6a7e;white-space:nowrap;">
                    📅 {datetime.datetime.now().strftime('%B %d, %Y')}
                </div>
            </div>
        </div>
    </div>
    <hr style="border:none;border-top:2px solid rgba(255,255,255,0.3);margin:16px 0;">
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:21px;padding:14px 16px;border:1px solid rgba(255,255,255,0.3);border-radius:14px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">'
        f'<div><strong style="display:block;color:#183153;font-size:13px;">✅ Complete your profile</strong>'
        f'<span style="color:#7b8797;font-size:12px;">Add the remaining details to keep your learner account accurate.</span></div>'
        f'<div style="min-width:120px;">'
        f'<div style="display:flex;justify-content:space-between;margin-bottom:6px;color:#7b8797;font-size:10px;font-weight:700;"><span>Profile</span><span>{completion}%</span></div>'
        f'<div style="height:7px;overflow:hidden;border-radius:999px;background:rgba(255,255,255,0.3);"><div style="height:100%;border-radius:inherit;background:linear-gradient(90deg,#4f8dff,#6c5ce7);width:{completion}%;"></div></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    active_section = st.segmented_control(
        "Settings sections",
        options=["All settings", "Profile", "Connected profiles", "Preferences", "Privacy"],
        default="All settings",
        key="settings_section_nav",
        label_visibility="collapsed",
    ) or "All settings"

    st.markdown(
        f'<div style="margin:4px 0 18px;color:#7b8797;font-size:14px;">📂 Settings / {active_section}</div>',
        unsafe_allow_html=True,
    )

    main_column, side_column = st.columns([2.05, 0.95], gap="large")

    with main_column:
        if active_section in {"All settings", "Profile"}:
            section_title("1", "Profile information", "Update the details shown throughout the planner.")
            render_settings_alert("Profile")
            profile_card(username, profile)

            picture_column, remove_column = st.columns([3, 1])
            with picture_column:
                uploaded_file = st.file_uploader(
                    "Profile picture",
                    type=["png", "jpg", "jpeg", "webp"],
                    key="settings_profile_picture",
                    help="Square images work best.",
                )
                if uploaded_file is not None:
                    save_profile_image(username, uploaded_file)
            with remove_column:
                st.write("")
                st.write("")
                if st.button("🗑️ Remove", use_container_width=True, key="settings_remove_photo"):
                    profile["profile_pic"] = None
                    st.session_state["profile_pic"] = None
                    save_users()
                    set_settings_alert("Profile", "success", "Profile picture removed.")
                    st.rerun()

            with st.form("settings_profile_form"):
                name_column, email_column = st.columns(2)
                with name_column:
                    display_name = st.text_input(
                        "👤 Display name", value=profile.get("name") or username
                    )
                with email_column:
                    email = st.text_input(
                        "📧 Email address",
                        value=profile.get("email") or user.get("email", ""),
                        placeholder="student@example.com",
                    )
                bio = st.text_area(
                    "📝 About",
                    value=profile.get("bio", "Study Planner learner"),
                    height=100,
                    max_chars=240,
                )
                if st.form_submit_button("💾 Save changes", use_container_width=True):
                    if not display_name.strip():
                        set_settings_alert("Profile", "error", "Display name cannot be empty.")
                        st.rerun()
                    elif not valid_email(email.strip()):
                        set_settings_alert("Profile", "error", "Enter a valid email address.")
                        st.rerun()
                    else:
                        profile["name"] = display_name.strip()
                        profile["email"] = email.strip()
                        profile["bio"] = bio.strip()
                        user["email"] = email.strip()
                        save_users()
                        set_settings_alert("Profile", "success", "Profile information saved.")
                        st.rerun()

        if active_section in {"All settings", "Connected profiles"}:
            section_title("2", "Connected profiles", "Add optional links for your learner profile.")
            render_settings_alert("Connected profiles")
            social = profile.setdefault("social", {})
            with st.form("settings_social_form"):
                social_left, social_right = st.columns(2)
                with social_left:
                    github = st.text_input(
                        "🐙 GitHub", value=social.get("github", ""),
                        placeholder="https://github.com/username"
                    )
                    twitter = st.text_input(
                        "🐦 X / Twitter", value=social.get("twitter", ""),
                        placeholder="https://x.com/username"
                    )
                with social_right:
                    linkedin = st.text_input(
                        "🔗 LinkedIn", value=social.get("linkedin", ""),
                        placeholder="https://linkedin.com/in/username"
                    )
                    website = st.text_input(
                        "🌐 Website", value=social.get("website", ""),
                        placeholder="https://example.com"
                    )
                if st.form_submit_button("💾 Save links", use_container_width=True):
                    values = {
                        "github": github.strip(), "twitter": twitter.strip(),
                        "linkedin": linkedin.strip(), "website": website.strip(),
                    }
                    invalid = [name for name, value in values.items() if not valid_url(value)]
                    if invalid:
                        set_settings_alert("Connected profiles", "error", "Use a complete http:// or https:// URL for: " + ", ".join(invalid))
                        st.rerun()
                    else:
                        profile["social"] = values
                        save_users()
                        set_settings_alert("Connected profiles", "success", "Connected profiles saved.")
                        st.rerun()

        if active_section in {"All settings", "Preferences"}:
            section_title("3", "Study preferences", "Choose targets, reminders, and appearance settings.")
            render_settings_alert("Preferences")
            hours_options = ["1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00"]
            current_hours = str(st.session_state.get("study_hours") or profile.get("study_hours") or "4:00")
            current_time = str(st.session_state.get("start_time") or profile.get("start_time") or "09:00")
            current_theme = str(st.session_state.get("theme") or profile.get("theme") or "System")
            current_notifications = bool(st.session_state.get("notifications", profile.get("notifications", True)))

            with st.form("settings_preferences_form"):
                left, right = st.columns(2)
                with left:
                    study_hours = st.selectbox(
                        "⏰ Daily study goal", hours_options,
                        index=hours_options.index(current_hours) if current_hours in hours_options else 3,
                    )
                    start_time = st.text_input(
                        "▶️ Preferred start time", value=current_time,
                        placeholder="09:00", help="Use 24-hour HH:MM format."
                    )
                with right:
                    theme = st.selectbox(
                        "🎨 Appearance", ["Light", "Dark", "System"],
                        index=["Light", "Dark", "System"].index(current_theme)
                        if current_theme in ["Light", "Dark", "System"] else 0,
                    )
                    notifications = st.checkbox(
                        "🔔 Enable study reminders", value=current_notifications
                    )
                if st.form_submit_button("💾 Save preferences", use_container_width=True):
                    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", start_time.strip()):
                        set_settings_alert("Preferences", "error", "Start time must use HH:MM format, for example 09:00.")
                        st.rerun()
                    else:
                        st.session_state["study_hours"] = study_hours
                        st.session_state["start_time"] = start_time.strip()
                        st.session_state["theme"] = theme
                        st.session_state["notifications"] = notifications
                        profile["study_hours"] = study_hours
                        profile["start_time"] = start_time.strip()
                        profile["theme"] = theme
                        profile["notifications"] = notifications
                        save_users()
                        set_settings_alert("Preferences", "success", "Study preferences saved.")
                        st.rerun()

        if active_section in {"All settings", "Privacy"}:
            section_title("4", "Account and privacy", "Review account security, privacy controls, and permanent actions.")
            render_settings_alert("Privacy")
            st.markdown(
                f'<div style="overflow:hidden;margin-bottom:18px;border:1px solid rgba(255,255,255,0.3);border-radius:15px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">'
                f'<div style="display:grid;grid-template-columns:38px minmax(0,1fr) auto;align-items:center;gap:13px;padding:17px 18px;border-bottom:1px solid rgba(255,255,255,0.3);">'
                f'<span style="display:grid;width:36px;height:36px;place-items:center;border-radius:10px;background:#d5f5e3;color:#27ae60;font-size:18px;font-weight:850;">✓</span>'
                f'<div><strong style="display:block;color:#183153;font-size:14px;">Private learner profile</strong><p style="margin:3px 0 0;color:#7b8797;font-size:12px;line-height:1.45;">Profile information remains available only inside this planner.</p></div>'
                f'<span style="padding:5px 9px;border:1px solid #d5f5e3;border-radius:999px;background:#d5f5e3;color:#27ae60;font-size:11px;font-weight:750;">Private</span>'
                f'</div>'
                f'<div style="display:grid;grid-template-columns:38px minmax(0,1fr) auto;align-items:center;gap:13px;padding:17px 18px;border-bottom:1px solid rgba(255,255,255,0.3);">'
                f'<span style="display:grid;width:36px;height:36px;place-items:center;border-radius:10px;background:#f0f4fe;color:#4f8dff;font-size:18px;font-weight:850;">⌁</span>'
                f'<div><strong style="display:block;color:#183153;font-size:14px;">Local data storage</strong><p style="margin:3px 0 0;color:#7b8797;font-size:12px;line-height:1.45;">Account preferences and planner data are stored by the application.</p></div>'
                f'<span style="padding:5px 9px;border:1px solid #d5f5e3;border-radius:999px;background:#d5f5e3;color:#27ae60;font-size:11px;font-weight:750;">Enabled</span>'
                f'</div>'
                f'<div style="display:grid;grid-template-columns:38px minmax(0,1fr) auto;align-items:center;gap:13px;padding:17px 18px;">'
                f'<span style="display:grid;width:36px;height:36px;place-items:center;border-radius:10px;background:#f0f4fe;color:#6c5ce7;font-size:18px;font-weight:850;">●</span>'
                f'<div><strong style="display:block;color:#183153;font-size:14px;">Current session</strong><p style="margin:3px 0 0;color:#7b8797;font-size:12px;line-height:1.45;">The learner account is currently signed in on this browser.</p></div>'
                f'<span style="padding:5px 9px;border:1px solid #d5f5e3;border-radius:999px;background:#d5f5e3;color:#27ae60;font-size:11px;font-weight:750;">Active</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="margin-bottom:15px;padding:21px;border:1px solid #fde8e8;border-radius:15px;background:#fff5f5;">'
                f'<div style="display:flex;align-items:flex-start;gap:12px;">'
                f'<span style="display:grid;width:34px;height:34px;min-width:34px;place-items:center;border-radius:10px;background:#fde8e8;color:#e74c3c;font-weight:900;font-size:18px;">⚠</span>'
                f'<div><strong style="display:block;color:#e74c3c;font-size:16px;">Delete learner account</strong>'
                f'<p style="margin:4px 0 0;color:#7b8797;font-size:12px;line-height:1.5;">This action deletes profile details and associated study plans permanently.</p></div>'
                f'</div>'
                f'<div style="display:flex;flex-wrap:wrap;gap:7px;margin:16px 0 12px 46px;">'
                f'<span style="padding:5px 8px;border:1px solid #fde8e8;border-radius:7px;background:#fff;color:#7b8797;font-size:11px;font-weight:650;">Profile information</span>'
                f'<span style="padding:5px 8px;border:1px solid #fde8e8;border-radius:7px;background:#fff;color:#7b8797;font-size:11px;font-weight:650;">Study plans</span>'
                f'<span style="padding:5px 8px;border:1px solid #fde8e8;border-radius:7px;background:#fff;color:#7b8797;font-size:11px;font-weight:650;">Saved preferences</span>'
                f'</div>'
                f'<div style="margin-left:46px;padding:10px 12px;border-radius:9px;background:#fde8e8;color:#e74c3c;font-size:11px;line-height:1.5;">⚠️ This action cannot be undone. Export anything important before continuing.</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            acknowledgement = st.checkbox(
                "☑️ I understand that this action permanently removes the account data.",
                key="settings_delete_acknowledgement",
            )
            confirmation = st.text_input(
                "🔑 Type DELETE to confirm", key="settings_delete_confirmation",
                placeholder="DELETE"
            )
            delete_column, cancel_column = st.columns(2)
            with delete_column:
                if st.button("🗑️ Delete account", use_container_width=True, key="settings_delete_account"):
                    if not acknowledgement:
                        set_settings_alert("Privacy", "error", "Confirm that the permanent deletion warning has been read.")
                        st.rerun()
                    elif confirmation != "DELETE":
                        set_settings_alert("Privacy", "error", "Type DELETE exactly to confirm account deletion.")
                        st.rerun()
                    else:
                        st.session_state.get("users_db", {}).pop(username, None)
                        save_users()
                        plans = st.session_state.get("plans_db", {})
                        plans.pop(username, None)
                        try:
                            from data_manager import save_plans_db
                            save_plans_db(plans)
                        except Exception:
                            pass
                        st.session_state["logged_in"] = False
                        st.session_state["username"] = ""
                        st.session_state["profile_pic"] = None
                        st.session_state["current_page"] = "home"
                        st.session_state["dashboard_action"] = "home"
                        try:
                            st.query_params.clear()
                        except Exception:
                            pass
                        st.rerun()
            with cancel_column:
                if st.button("✖ Cancel", use_container_width=True, key="settings_cancel_delete"):
                    st.session_state["settings_delete_confirmation"] = ""
                    st.rerun()

    with side_column:
        profile_name = profile.get("name") or username
        email_value = profile.get("email") or user.get("email") or "Not provided"
        notification_label = "Enabled" if profile.get("notifications", True) else "Disabled"
        social_count = sum(bool(value) for value in profile.get("social", {}).values())
        picture = get_profile_picture(username)
        avatar_display = f'<img src="{picture}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;">' if picture else initials(profile_name)

        st.markdown(
            f'<div style="padding:20px;margin-bottom:16px;border:1px solid rgba(255,255,255,0.3);border-radius:16px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">'
            f'<div style="margin-bottom:13px;color:#183153;font-size:15px;font-weight:800;">📋 Account overview</div>'
            f'<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;padding:11px 0;border-bottom:1px solid rgba(255,255,255,0.3);color:#7b8797;font-size:12px;"><span>👤 Profile name</span><strong style="color:#183153;text-align:right;">{profile_name}</strong></div>'
            f'<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;padding:11px 0;border-bottom:1px solid rgba(255,255,255,0.3);color:#7b8797;font-size:12px;"><span>📧 Email</span><strong style="color:#183153;text-align:right;">{email_value}</strong></div>'
            f'<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;padding:11px 0;border-bottom:1px solid rgba(255,255,255,0.3);color:#7b8797;font-size:12px;"><span>👑 Plan</span><strong style="color:#183153;text-align:right;">Pro Plan</strong></div>'
            f'<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;padding:11px 0;color:#7b8797;font-size:12px;"><span>🔔 Reminders</span><strong style="color:#183153;text-align:right;">{notification_label}</strong></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="padding:20px;margin-bottom:16px;border:1px solid rgba(255,255,255,0.3);border-radius:16px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">'
            f'<div style="margin-bottom:13px;color:#183153;font-size:15px;font-weight:800;">📊 Workspace summary</div>'
            f'<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;">'
            f'<div style="padding:14px;border-radius:12px;background:#f0f4fe;"><strong style="display:block;color:#183153;font-size:18px;">⏰ {profile.get("study_hours", "4:00")}</strong><span style="color:#7b8797;font-size:11px;">Daily goal</span></div>'
            f'<div style="padding:14px;border-radius:12px;background:#d5f5e3;"><strong style="display:block;color:#183153;font-size:18px;">🔗 {social_count}/4</strong><span style="color:#7b8797;font-size:11px;">Links added</span></div>'
            f'<div style="padding:14px;border-radius:12px;background:#fdebd0;"><strong style="display:block;color:#183153;font-size:18px;">🎨 {profile.get("theme", "Light")}</strong><span style="color:#7b8797;font-size:11px;">Appearance</span></div>'
            f'<div style="padding:14px;border-radius:12px;background:#fef9e7;"><strong style="display:block;color:#183153;font-size:18px;">▶️ {profile.get("start_time", "09:00")}</strong><span style="color:#7b8797;font-size:11px;">Start time</span></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="display:flex;align-items:flex-start;gap:11px;padding:16px;margin-bottom:18px;border:1px solid rgba(255,255,255,0.3);border-radius:16px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">'
            f'<div style="width:10px;height:10px;min-width:10px;margin-top:4px;border-radius:50%;background:#27ae60;box-shadow:0 0 0 5px #d5f5e3;"></div>'
            f'<div><strong style="display:block;color:#183153;font-size:13px;">✅ Changes are saved to this account</strong>'
            f'<p style="margin:3px 0 0;color:#7b8797;font-size:12px;">Use the links above to move between settings without scrolling through the full page.</p></div>'
            f'</div>',
            unsafe_allow_html=True,
        )