# app.py - Full fixed version

import streamlit as st
import sys
import os
import json
from datetime import datetime

sys.path.append(os.getcwd())

from home import show_home_page, auth_screen
from dashboard import show_dashboard
from timetable import show_timetable_page
from learning import show_learning_page
from quiz import show_quiz_page
from planner import show_planner_page
from settings import show_settings_page
from data_manager import load_users_db, load_plans_db, save_session

# ---------- Page Config ----------
st.set_page_config(
    page_title="Smart Study Planner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- GLOBAL CSS FOR SOFT GRADIENT BACKGROUND ----------
GLOBAL_CSS = """
<style>
    /* 🌈 Soft Gradient Background */
    .stApp {
        background: linear-gradient(160deg, #e8f0fe 0%, #d4e4ff 30%, #b8d4ff 60%, #a8c8ff 100%) !important;
        background-attachment: fixed !important;
        min-height: 100vh !important;
    }
    
    /* ✅ Main content - transparent so gradient shows through */
    .main > div {
        background: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
    }
    
    /* ✅ Block container - transparent */
    .block-container {
        background: transparent !important;
        padding: 1rem 1rem 4rem 1rem !important;
        max-width: 100% !important;
    }
    
    /* ✅ All cards, containers - glass effect */
    .st-emotion-cache-1r6slb0, .st-emotion-cache-1v3fvcr,
    [data-testid="stForm"], [data-testid="stMetric"],
    .css-1r6slb0, .css-1v3fvcr,
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 16px rgba(79, 141, 255, 0.08) !important;
    }
    
    /* Hide Streamlit default elements */
    header { display: none !important; }
    .stDeployButton { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stHeader"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    footer { display: none !important; }
    .st-emotion-cache-1cypcdb { display: none !important; }
    button[data-testid="baseButton-header"] { display: none !important; }
    .st-emotion-cache-1r6slb0 { display: none !important; }
    .st-emotion-cache-1v3fvcr { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .st-emotion-cache-12w0qpk { padding-top: 0 !important; }
    
    /* ✅ Ensure sidebar glass effect stays */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
</style>
"""

# Apply global CSS
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ---------- Session State Init ----------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "subjects" not in st.session_state:
    st.session_state["subjects"] = []
if "signup_success" not in st.session_state:
    st.session_state["signup_success"] = False
if "study_hours" not in st.session_state:
    st.session_state["study_hours"] = "4:00"
if "start_time" not in st.session_state:
    st.session_state["start_time"] = "09:00"
if "profile_pic" not in st.session_state:
    st.session_state["profile_pic"] = None
if "remember_me" not in st.session_state:
    st.session_state["remember_me"] = False
if "dashboard_action" not in st.session_state:
    st.session_state["dashboard_action"] = "home"
if "auth_tab" not in st.session_state:
    st.session_state["auth_tab"] = "login"
if "selected_learning_subject" not in st.session_state:
    st.session_state["selected_learning_subject"] = None
if "validation_cache" not in st.session_state:
    st.session_state["validation_cache"] = {}
if "study_streak" not in st.session_state:
    st.session_state["study_streak"] = 12
if "exams" not in st.session_state:
    st.session_state["exams"] = [
        {"name": "Machine Learning", "days_left": 12, "date": "26 Jul 2026"},
        {"name": "Database Systems", "days_left": 25, "date": "8 Aug 2026"},
        {"name": "English", "days_left": 30, "date": "15 Aug 2026"},
    ]
if "show_create_plan" not in st.session_state:
    st.session_state["show_create_plan"] = False
if "show_add_task" not in st.session_state:
    st.session_state["show_add_task"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"
if "learning_view_mode" not in st.session_state:
    st.session_state["learning_view_mode"] = "Grid"

# ---------- Load Persistent Data ----------
if "users_db" not in st.session_state:
    st.session_state["users_db"] = load_users_db()
if "plans_db" not in st.session_state:
    st.session_state["plans_db"] = load_plans_db()

# ============================================================
# 🔥 FIX 1: Auto-login from session.json
# ============================================================
def auto_login_from_session():
    """Auto login from saved session if remember_me is True"""
    if not st.session_state.get("logged_in", False):
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    session_data = json.load(f)
                    username = session_data.get("username")
                    if username and username in st.session_state.get("users_db", {}):
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username
                        st.session_state["remember_me"] = True
                        return True
        except Exception as e:
            print(f"Auto-login error: {e}")
    return False

# Run auto-login
auto_login_from_session()

# ============================================================
# 🔥 FIX 2: Load profile picture from database on EVERY page load
# ============================================================
def load_profile_from_database():
    """Load profile picture from database into session_state"""
    if st.session_state.get("logged_in", False):
        username = st.session_state.get("username")
        if username:
            users_db = st.session_state.get("users_db", {})
            user_data = users_db.get(username, {})
            profile = user_data.get("profile", {})
            
            # Load profile picture from database
            db_profile_pic = profile.get("profile_pic")
            
            # Update session_state
            if db_profile_pic and isinstance(db_profile_pic, str) and len(db_profile_pic) > 100:
                st.session_state["profile_pic"] = db_profile_pic
            else:
                st.session_state["profile_pic"] = None
            
            # Debug
            print(f"✅ Loaded profile for {username}: {'Yes' if st.session_state['profile_pic'] else 'No'}")
    else:
        st.session_state["profile_pic"] = None

# 🔥 Call this function on EVERY page load
load_profile_from_database()
# ============================================================

# ---------- SIDEBAR CSS ----------
SIDEBAR_CSS = """
<style>
    /* Font Awesome CDN */
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');
    
    /* Sidebar Container - Soft Glass Effect */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    .sidebar-container {
        padding: 0;
    }
    
    /* Sidebar Profile Section */
    .sidebar-profile {
        text-align: center;
        padding: 16px 0 14px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.3);
        margin-bottom: 8px;
    }
    .sidebar-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4f8dff, #6c5ce7);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 8px auto;
        font-size: 26px;
        color: white;
        overflow: hidden;
        border: 2px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 4px 16px rgba(79, 141, 255, 0.2);
    }
    .sidebar-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 50%;
    }
    .sidebar-avatar i {
        font-size: 26px;
    }
    .sidebar-name {
        font-size: 15px;
        font-weight: 700;
        color: #183153;
    }
    .sidebar-role {
        font-size: 12px;
        color: #4a5a7a;
    }
    .sidebar-plan {
        display: inline-block;
        background: linear-gradient(135deg, #4f8dff, #6c5ce7);
        color: white;
        padding: 2px 14px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 600;
        margin-top: 4px;
    }
    .sidebar-plan i {
        font-size: 10px;
        margin-right: 4px;
    }
    
    /* Sidebar Nav Items */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        border-radius: 10px;
        color: #4a5a7a !important;
        font-weight: 500;
        font-size: 14px;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-bottom: 2px;
        border: none;
        background: transparent;
        width: 100%;
    }
    .nav-item:hover {
        background: rgba(79, 141, 255, 0.12);
        color: #4f8dff !important;
    }
    .nav-item.active {
        background: rgba(79, 141, 255, 0.18) !important;
        color: #4f8dff !important;
        box-shadow: 0 4px 16px rgba(79, 141, 255, 0.10);
        border-left: 4px solid #4f8dff;
    }
    .nav-item .icon {
        width: 24px;
        text-align: center;
        font-size: 16px;
        color: inherit;
    }
    .nav-item .icon i {
        font-size: 16px;
    }
    
    /* Sidebar Bottom */
    .sidebar-bottom {
        margin-top: auto;
        border-top: 1px solid rgba(79, 141, 255, 0.15);
        padding-top: 10px;
    }
    
    /* Sidebar buttons */
    .stButton > button {
        background: rgba(79, 141, 255, 0.08) !important;
        color: #4a5a7a !important;
        border: 1px solid rgba(79, 141, 255, 0.15) !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px) !important;
    }
    .stButton > button:hover {
        background: rgba(79, 141, 255, 0.18) !important;
        border-color: rgba(79, 141, 255, 0.3) !important;
        color: #4f8dff !important;
    }
    
    /* Remove extra padding from main content */
    .main > div {
        padding-top: 0 !important;
    }
    .block-container {
        padding-top: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    .nav-item.active .icon i {
        color: #4f8dff !important;
    }
</style>
"""

# ---------- RENDER SIDEBAR ----------
def render_sidebar():
    """Render sidebar with Streamlit components"""
    username = st.session_state.get("username", "User")
    user_data = st.session_state.get("users_db", {}).get(username, {})
    profile = user_data.get("profile", {})
    current_page = st.session_state.get("current_page", "home")
    
    # 🔥 Get profile picture from session_state
    profile_pic = st.session_state.get("profile_pic")
    
    st.markdown('<div class="sidebar-container">', unsafe_allow_html=True)
    
    # Profile Section with profile picture
    if profile_pic and isinstance(profile_pic, str) and len(profile_pic) > 100:
        avatar_html = f'''
        <div class="sidebar-profile">
            <div class="sidebar-avatar">
                <img src="{profile_pic}" alt="Profile picture"/>
            </div>
            <div class="sidebar-name">{username}</div>
            <div class="sidebar-role">{profile.get("bio", "Student")}</div>
            <div class="sidebar-plan"><i class="fas fa-star"></i> Pro Plan</div>
        </div>
        '''
    else:
        avatar_html = f'''
        <div class="sidebar-profile">
            <div class="sidebar-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="sidebar-name">{username}</div>
            <div class="sidebar-role">{profile.get("bio", "Student")}</div>
            <div class="sidebar-plan"><i class="fas fa-star"></i> Pro Plan</div>
        </div>
        '''
    
    st.markdown(avatar_html, unsafe_allow_html=True)
    
    # Navigation items
    nav_items = [
        {"label": "Home", "page": "home", "icon": "fa-house"},
        {"label": "Planner", "page": "planner", "icon": "fa-book"},
        {"label": "Timetable", "page": "timetable", "icon": "fa-clock"},
        {"label": "Learning", "page": "learning", "icon": "fa-graduation-cap"},
        {"label": "Quiz", "page": "quiz", "icon": "fa-puzzle-piece"},
    ]
    
    for item in nav_items:
        is_active = (item["page"] == current_page)
        
        if is_active:
            st.markdown(f"""
            <div class="nav-item active">
                <span class="icon"><i class="fas {item['icon']}"></i></span>
                <span>{item['label']}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button(f"{item['label']}", use_container_width=True, key=f"nav_{item['page']}"):
                st.session_state["current_page"] = item["page"]
                st.query_params["page"] = item["page"]
                st.rerun()
    
    st.markdown("---")
    
    if st.button(" ⚙️ Settings", use_container_width=True, key="nav_settings"):
        st.session_state["current_page"] = "settings"
        st.query_params["page"] = "settings"
        st.rerun()
    
    if st.button(" 🚪 Logout", use_container_width=True, key="nav_logout"):
        # Clear session
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.profile_pic = None
        st.session_state.remember_me = False
        st.session_state.current_page = "home"
        
        # Delete session.json
        try:
            if os.path.exists("session.json"):
                os.remove("session.json")
        except:
            pass
        
        st.query_params.clear()
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- APP ROUTER ----------
def main():
    # Get page from query params
    query_params = st.query_params
    page = query_params.get("page", "home")
    
    # Update current page
    st.session_state["current_page"] = page
    
    # 🔥 Check if logged in
    if not st.session_state.get("logged_in", False):
        auth_screen()
        return
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
        render_sidebar()
    
    # ===== PAGE ROUTER =====
    if page == "home":
        show_dashboard()
    elif page == "planner":
        show_planner_page()
    elif page == "timetable":
        show_timetable_page()
    elif page == "learning":
        show_learning_page()
    elif page == "quiz":
        show_quiz_page()
    elif page == "settings":
        show_settings_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()