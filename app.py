# app.py - Full Code with Guaranteed Floating Sidebar Toggle Button

import streamlit as st
import sys
import os
import json
import streamlit.components.v1 as components
from datetime import datetime
import streamlit.components.v1 as components

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

# ---------- 🌈 GLOBAL CSS FOR DASHBOARD GRADIENT & CUSTOM SIDEBAR TOGGLE ----------
GLOBAL_CSS = """
<style>
    /* 1. Dashboard Background Gradient */
    .stApp {
        background: linear-gradient(160deg, #e8f0fe 0%, #d4e4ff 30%, #b8d4ff 60%, #a8c8ff 100%) !important;
        background-attachment: fixed !important;
        min-height: 100vh !important;
    }
    
    .main > div {
        background: transparent !important;
    }
    
    .block-container {
        background: transparent !important;
        padding: 2rem 1rem 4rem 1rem !important;
        max-width: 100% !important;
    }

    /* Streamlit Deploy Button နှင့် မလိုအပ်သော Toolbar များကိုသာ ဖျောက်မည် */
    .stDeployButton, [data-testid="stToolbar"] { 
        display: none !important; 
    }
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ---------- 🛠️ GUARANTEED JS-BASED FLOATING TOGGLE BUTTON ----------
# ဒီ JavaScript လေးက Screen ရဲ့ ဘယ်ဘက်အပေါ်ထောင့်မှာ Sidebar ဖွင့်/ပိတ်လုပ်ပေးမယ့် Floating Button လေးကို ဖန်တီးပေးပါတယ်
components.html("""
<script>
    const parentDoc = window.parent.document;

    function toggleSidebar() {
        // Streamlit ရဲ့ Internal Toggle Button များကို ရှာဖွေပြီး နှိပ်ပေးခြင်း
        const button = parentDoc.querySelector('button[data-testid="stSidebarCollapsedControl"]') || 
                       parentDoc.querySelector('button[data-testid="baseButton-header"]') ||
                       parentDoc.querySelector('[data-testid="stSidebar"] button');
        if (button) {
            button.click();
        }
    }

    // Floating Button မရှိသေးပါက Parent DOM ထဲသို့ ထည့်သွင်းမည်
    if (!parentDoc.getElementById('custom-sidebar-toggle-btn')) {
        const btn = parentDoc.createElement('button');
        btn.id = 'custom-sidebar-toggle-btn';
        btn.innerHTML = '☰';
        btn.style.position = 'fixed';
        btn.style.top = '12px';
        btn.style.left = '12px';
        btn.style.zIndex = '9999999';
        btn.style.padding = '6px 14px';
        btn.style.fontSize = '18px';
        btn.style.fontWeight = 'bold';
        btn.style.color = '#1e293b';
        btn.style.backgroundColor = 'rgba(255, 255, 255, 0.85)';
        btn.style.border = '1px solid rgba(0, 0, 0, 0.15)';
        btn.style.borderRadius = '8px';
        btn.style.cursor = 'pointer';
        btn.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
        btn.style.backdropFilter = 'blur(8px)';
        btn.style.transition = 'all 0.2s ease';

        btn.onmouseover = function() {
            btn.style.backgroundColor = '#ffffff';
            btn.style.color = '#2563eb';
            btn.style.transform = 'scale(1.05)';
        };
        btn.onmouseout = function() {
            btn.style.backgroundColor = 'rgba(255, 255, 255, 0.85)';
            btn.style.color = '#1e293b';
            btn.style.transform = 'scale(1)';
        };

        btn.onclick = toggleSidebar;
        parentDoc.body.appendChild(btn);
    }
</script>
""", height=0, width=0)
# ---------- iOS TOGGLE FIX ----------
components.html("""
<script>
    // iOS Fix - Force toggle button to work
    setTimeout(function() {
        // Find all possible toggle buttons
        var btn = document.querySelector('[data-testid="stSidebarCollapsedControl"]') || 
                  document.querySelector('button[aria-label="Collapse sidebar"]') ||
                  document.querySelector('[data-testid="stSidebar"] button');
        
        if (btn) {
            // Make it visible and touchable
            btn.style.display = 'flex';
            btn.style.visibility = 'visible';
            btn.style.opacity = '1';
            btn.style.zIndex = '999999';
            btn.style.padding = '14px 18px';
            btn.style.margin = '10px';
            btn.style.minWidth = '50px';
            btn.style.minHeight = '50px';
            btn.style.background = 'rgba(255,255,255,0.95)';
            btn.style.borderRadius = '12px';
            btn.style.border = '2px solid rgba(79,141,255,0.3)';
            btn.style.boxShadow = '0 4px 16px rgba(79,141,255,0.2)';
            btn.style.touchAction = 'manipulation';
            btn.style.cursor = 'pointer';
            
            // iOS touch fix
            btn.addEventListener('touchstart', function(e) {
                e.preventDefault();
                this.click();
            }, {passive: false});
            
            // Visual feedback
            btn.addEventListener('click', function(e) {
                this.style.transform = 'scale(0.9)';
                setTimeout(function() {
                    btn.style.transform = 'scale(1)';
                }, 200);
            });
        }
    }, 500);
</script>
""", height=0, width=0)

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

# ---------- Auto Login ----------
def auto_login_from_session():
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
        except Exception:
            pass
    return False

auto_login_from_session()

# ---------- Profile Loader ----------
def load_profile_from_database():
    if st.session_state.get("logged_in", False):
        username = st.session_state.get("username")
        if username:
            users_db = st.session_state.get("users_db", {})
            user_data = users_db.get(username, {})
            profile = user_data.get("profile", {})
            db_profile_pic = profile.get("profile_pic")
            if db_profile_pic and isinstance(db_profile_pic, str) and len(db_profile_pic) > 100:
                st.session_state["profile_pic"] = db_profile_pic
            else:
                st.session_state["profile_pic"] = None
    else:
        st.session_state["profile_pic"] = None

load_profile_from_database()

# ---------- SIDEBAR STYLING ----------
SIDEBAR_CSS = """
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');
    
    /* Sidebar Glassmorphism Effect */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.35) !important;
        backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.4) !important;
    }
    
    .sidebar-profile {
        text-align: center;
        padding: 10px 0 14px 0;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        margin-bottom: 12px;
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
        font-size: 24px;
        color: white;
        overflow: hidden;
        border: 2px solid #ffffff;
        box-shadow: 0 4px 12px rgba(79, 141, 255, 0.2);
    }
    .sidebar-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .sidebar-name {
        font-size: 15px;
        font-weight: 700;
        color: #1e293b;
    }
    .sidebar-role {
        font-size: 12px;
        color: #64748b;
    }
    .sidebar-plan {
        display: inline-block;
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        padding: 2px 12px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 600;
        margin-top: 4px;
    }

    /* Active Nav Item */
    .nav-gradient-active {
        background: linear-gradient(135deg, #4f8dff 0%, #6c5ce7 100%) !important;
        color: #ffffff !important;
        padding: 10px 16px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 4px;
        box-shadow: 0 4px 14px rgba(79, 141, 255, 0.35);
    }
    .nav-gradient-active i {
        color: #ffffff !important;
        font-size: 16px;
        width: 20px;
        text-align: center;
    }

    /* Unactive Navigation Buttons */
    div[data-testid="stSidebar"] button {
        border: none !important;
        background: transparent !important;
        color: #64748b !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
        padding: 10px 16px !important;
    }
    div[data-testid="stSidebar"] button:hover {
        background: rgba(79, 141, 255, 0.12) !important;
        color: #2563eb !important;
    }
</style>
"""

# ---------- RENDER SIDEBAR ----------
def render_sidebar():
    username = st.session_state.get("username", "User")
    user_data = st.session_state.get("users_db", {}).get(username, {})
    profile = user_data.get("profile", {})
    current_page = st.session_state.get("current_page", "home")
    profile_pic = st.session_state.get("profile_pic")
    
    if profile_pic and isinstance(profile_pic, str) and len(profile_pic) > 100:
        avatar_content = f'<img src="{profile_pic}" alt="Profile"/>'
    else:
        avatar_content = f'<span>{username[0].upper() if username else "U"}</span>'
    
    st.markdown(f"""
    <div class="sidebar-profile">
        <div class="sidebar-avatar">{avatar_content}</div>
        <div class="sidebar-name">{username}</div>
        <div class="sidebar-role">{profile.get("bio", "Student")}</div>
        <div class="sidebar-plan"><i class="fas fa-star"></i> Pro Plan</div>
    </div>
    """, unsafe_allow_html=True)
    
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
            <div class="nav-gradient-active">
                <i class="fas {item['icon']}"></i>
                <span>{item['label']}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.sidebar.button(f"‎ {item['label']}", key=f"nav_{item['page']}", use_container_width=True):
                st.session_state["current_page"] = item["page"]
                st.query_params["page"] = item["page"]
                st.rerun()
    
    st.sidebar.markdown("---")
    
    if current_page == "settings":
        st.markdown("""
        <div class="nav-gradient-active">
            <i class="fas fa-gear"></i>
            <span>Settings</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.sidebar.button("‎ Settings", key="nav_settings", use_container_width=True):
            st.session_state["current_page"] = "settings"
            st.query_params["page"] = "settings"
            st.rerun()
            
    if st.sidebar.button("‎ Logout", key="nav_logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.profile_pic = None
        try:
            if os.path.exists("session.json"):
                os.remove("session.json")
        except Exception:
            pass
        st.query_params.clear()
        st.rerun()

# ---------- MAIN ROUTER ----------
def main():
    query_params = st.query_params
    page = query_params.get("page", "home")
    st.session_state["current_page"] = page
    
    if not st.session_state.get("logged_in", False):
        auth_screen()
        return
    
    # Render Sidebar inside Streamlit's Default Sidebar
    with st.sidebar:
        st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
        render_sidebar()
    
    # Page Router
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