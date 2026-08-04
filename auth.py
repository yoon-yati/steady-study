# auth.py - Login & Sign Up UI (HTML Version - Mobile Friendly)
import streamlit as st
import streamlit.components.v1 as components
import json
import os
from utils import hash_password
from data_manager import save_users_db, save_session

# ============= AUTH FUNCTIONS =============

def get_profile_picture(username):
    users = st.session_state.get("users_db", {})
    if username in users:
        profile = users[username].get("profile", {})
        return profile.get("profile_pic")
    return None

def init_auth_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'users_db' not in st.session_state:
        st.session_state.users_db = {}
    if 'signup_success' not in st.session_state:
        st.session_state.signup_success = False
    if 'auth_tab' not in st.session_state:
        st.session_state.auth_tab = "login"
    if 'learning_progress' not in st.session_state:
        st.session_state.learning_progress = {}
    if 'goals' not in st.session_state:
        st.session_state.goals = {}
    if 'notes' not in st.session_state:
        st.session_state.notes = {}
    if 'profile_pic' not in st.session_state:
        st.session_state.profile_pic = None
    
    if os.path.exists("goals.json"):
        try:
            with open("goals.json", "r", encoding='utf-8') as f:
                st.session_state.goals = json.load(f)
        except:
            st.session_state.goals = {}
    else:
        st.session_state.goals = {}
    
    if os.path.exists("notes.json"):
        try:
            with open("notes.json", "r", encoding='utf-8') as f:
                st.session_state.notes = json.load(f)
        except:
            st.session_state.notes = {}
    else:
        st.session_state.notes = {}
    
    if os.path.exists("users.json"):
        try:
            with open("users.json", "r") as f:
                st.session_state.users_db = json.load(f)
        except:
            st.session_state.users_db = {}
    
    username = st.session_state.get("username")
    if username and username in st.session_state.users_db:
        if "learning_progress" in st.session_state.users_db[username]:
            st.session_state.learning_progress[username] = st.session_state.users_db[username]["learning_progress"]
        else:
            st.session_state.learning_progress[username] = {}
        
        if "goals" in st.session_state.users_db[username]:
            st.session_state.goals[username] = st.session_state.users_db[username]["goals"]
        else:
            st.session_state.goals[username] = []
        
        if "notes" in st.session_state.users_db[username]:
            st.session_state.notes[username] = st.session_state.users_db[username]["notes"]
        else:
            st.session_state.notes[username] = []
        
        pic = get_profile_picture(username)
        if pic:
            st.session_state.profile_pic = pic

def load_goals():
    goals_file = "goals.json"
    if os.path.exists(goals_file):
        try:
            with open(goals_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def load_notes():
    notes_file = "notes.json"
    if os.path.exists(notes_file):
        try:
            with open(notes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_goals():
    goals_file = "goals.json"
    try:
        with open(goals_file, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.get("goals", {}), f, indent=2, ensure_ascii=False)
        
        username = st.session_state.get("username")
        if username and username in st.session_state.users_db:
            st.session_state.users_db[username]["goals"] = st.session_state.goals.get(username, [])
            save_users()
        return True
    except:
        return False

def save_notes():
    notes_file = "notes.json"
    try:
        with open(notes_file, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.get("notes", {}), f, indent=2, ensure_ascii=False)
        
        username = st.session_state.get("username")
        if username and username in st.session_state.users_db:
            st.session_state.users_db[username]["notes"] = st.session_state.notes.get(username, [])
            save_users()
        return True
    except:
        return False

def save_users():
    try:
        with open("users.json", "w", encoding='utf-8') as f:
            json.dump(st.session_state.users_db, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

def save_learning_progress():
    username = st.session_state.get("username")
    if username and username in st.session_state.users_db:
        st.session_state.users_db[username]["learning_progress"] = st.session_state.learning_progress.get(username, {})
        save_users()

def handle_login(username_or_email, password):
    users = st.session_state.users_db
    
    if username_or_email in users:
        if users[username_or_email]["password"] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.username = username_or_email
            
            if "learning_progress" in users[username_or_email]:
                st.session_state.learning_progress[username_or_email] = users[username_or_email]["learning_progress"]
            else:
                st.session_state.learning_progress[username_or_email] = {}
            
            if "goals" in users[username_or_email]:
                st.session_state.goals[username_or_email] = users[username_or_email]["goals"]
            else:
                st.session_state.goals[username_or_email] = []
            
            if "notes" in users[username_or_email]:
                st.session_state.notes[username_or_email] = users[username_or_email]["notes"]
            else:
                st.session_state.notes[username_or_email] = []
            
            pic = get_profile_picture(username_or_email)
            if pic:
                st.session_state.profile_pic = pic
            
            save_session(username_or_email)
            return True, "Login successful!"
        else:
            return False, "Incorrect password!"
    
    for username, user_data in users.items():
        if user_data.get("email") == username_or_email:
            if user_data["password"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                
                if "learning_progress" in users[username]:
                    st.session_state.learning_progress[username] = users[username]["learning_progress"]
                else:
                    st.session_state.learning_progress[username] = {}
                
                if "goals" in users[username]:
                    st.session_state.goals[username] = users[username]["goals"]
                else:
                    st.session_state.goals[username] = []
                
                if "notes" in users[username]:
                    st.session_state.notes[username] = users[username]["notes"]
                else:
                    st.session_state.notes[username] = []
                
                pic = get_profile_picture(username)
                if pic:
                    st.session_state.profile_pic = pic
                
                save_session(username)
                return True, "Login successful!"
            else:
                return False, "Incorrect password!"
    
    return False, "Username or Email not found!"

def handle_signup(username, email, password, confirm_password):
    users = st.session_state.users_db
    
    if not username or not email or not password:
        return False, "Please fill all fields!"
    if password != confirm_password:
        return False, "Passwords do not match!"
    if username in users:
        return False, "Username already taken!"
    if any(user["email"] == email for user in users.values()):
        return False, "Email already registered!"
    if "@gmail.com" not in email:
        return False, "Please enter a valid Gmail address!"
    if len(password) < 6:
        return False, "Password must be at least 6 characters!"
    
    users[username] = {
        "email": email,
        "password": hash_password(password),
        "learning_progress": {},
        "goals": [],
        "notes": [],
        "profile": {
            "name": username,
            "email": email,
            "bio": "Study Planner learner",
            "profile_pic": None,
            "theme": "Light",
            "notifications": True,
            "study_hours": "4:00",
            "start_time": "09:00",
            "social": {}
        }
    }
    save_users()
    return True, "Account created successfully!"

# ============= AUTH SCREEN =============
def auth_screen():
    """Show login/signup page with HTML UI (Full Screen - Mobile Friendly)"""
    
    # Hide sidebar when showing auth
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        .stApp {
            margin: 0 !important;
            padding: 0 !important;
        }
        .stApp > div:first-child {
            padding: 0 !important;
        }
        .main > div {
            padding: 0 !important;
        }
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
        [data-testid="stAppViewContainer"] {
            padding: 0 !important;
            margin: 0 !important;
        }
        [data-testid="stHeader"] {
            display: none !important;
        }
        [data-testid="stToolbar"] {
            display: none !important;
        }
        [data-testid="stDecoration"] {
            display: none !important;
        }
        #MainMenu {
            visibility: hidden !important;
        }
        footer {
            visibility: hidden !important;
        }
        header {
            visibility: hidden !important;
        }
        .stDeployButton {
            display: none !important;
        }
            /* iPhone Specific Fix */
@supports (-webkit-touch-callout: none) {
    .container {
        min-height: 100vh !important;
        max-height: none !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }
    .login-card {
        margin-bottom: 30px !important;
    }
    .right {
        padding-bottom: 40px !important;
    }
}
    </style>
    """, unsafe_allow_html=True)
    
    init_auth_session()
    
    action = st.query_params.get("action", "")
    username = st.query_params.get("username", "")
    password = st.query_params.get("password", "")
    email = st.query_params.get("email", "")
    
    # Handle Login
    if action == "login":
        if username and password:
            success, message = handle_login(username, password)
            if success:
                st.query_params.clear()
                st.rerun()
            else:
                st.error(f"❌ {message}")
                st.query_params.clear()
                st.rerun()
    
    # Handle Signup
    if action == "signup":
        confirm = st.query_params.get("confirm", "")
        if username and email and password:
            success, message = handle_signup(username, email, password, confirm)
            if success:
                st.session_state.signup_success = True
                st.query_params.clear()
                st.rerun()
            else:
                st.error(f"❌ {message}")
                st.query_params.clear()
                st.rerun()
    
    # Handle Logout
    if action == "logout":
        st.session_state.logged_in = False
        st.session_state.username = None
        st.query_params.clear()
        st.rerun()
    
    if st.session_state.signup_success:
        st.success("✅ Account created successfully! Please login.")
        st.session_state.signup_success = False
        st.rerun()
    
    page = st.query_params.get("page", "login")
    is_login = (page == "login")
    
    button_text = "Login" if is_login else "Sign Up"
    button_icon = "arrow-right-to-bracket" if is_login else "user-plus"
    title = "Welcome Back!" if is_login else "Create Account"
    subtitle = "Login to continue your learning journey" if is_login else "Sign up to start your learning journey"
    
    signup_link_text = "Don't have an account? <a href='?page=signup' class='auth-link'>Sign up</a>" if is_login else "Already have an account? <a href='?page=login' class='auth-link'>Login</a>"
    
    name_field = """
    <div class="form-group">
        <label>Full Name</label>
        <input id="fullname" class="input" type="text" placeholder="Enter your full name" />
    </div>
    """ if not is_login else ""
    
    confirm_field = """
    <div class="form-group">
        <label>Confirm Password</label>
        <input id="confirm_password" class="input" type="password" placeholder="Re-enter your password" />
    </div>
    """ if not is_login else ""
    
    email_label = "Email" if not is_login else "Username or Email"
    email_placeholder = "Enter your email" if not is_login else "Enter your username or email"
    
    forgot_password = """
    <a href="#" class="forgot-link">Forgot Password?</a>
    """ if is_login else ""
    
    login_js = """
    if (!email || !password) {
        alert('Please fill in all fields!');
        return;
    }
    window.location.href = '?action=login&username=' + encodeURIComponent(email) + '&password=' + encodeURIComponent(password);
    """
    
    signup_js = """
    var fullname = document.getElementById('fullname').value;
    var confirm = document.getElementById('confirm_password').value;
    
    if (!fullname || !email || !password || !confirm) {
        alert('Please fill in all fields!');
        return;
    }
    if (password !== confirm) {
        alert('Passwords do not match!');
        return;
    }
    if (password.length < 6) {
        alert('Password must be at least 6 characters!');
        return;
    }
    if (!email.includes('@gmail.com')) {
        alert('Please enter a valid Gmail address!');
        return;
    }
    window.location.href = '?action=signup&username=' + encodeURIComponent(fullname) + '&email=' + encodeURIComponent(email) + '&password=' + encodeURIComponent(password) + '&confirm=' + encodeURIComponent(confirm);
    """
    
    js_code = signup_js if not is_login else login_js
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>Smart Study Planner</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet"/>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"/>
        <style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Inter', sans-serif;
}}

html, body {{
    width: 100%;
    min-height: 100%;
    margin: 0;
    padding: 0;
    background: radial-gradient(circle at top left, #b6d8ff 0%, #eef6ff 45%, #ffffff 100%);
}}

body {{
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}}

.container {{
    width: 100%;
    max-width: 1450px;
    display: flex;
    gap: 25px;
    border-radius: 40px;
    overflow: hidden;
    background-image: url('https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1920&q=80');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    position: relative;
    box-shadow: 0 30px 80px rgba(0, 0, 0, .08);
    padding: 0;
}}

.left {{
    flex: 1.3;
    padding: 50px 40px 50px 50px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    overflow: hidden;
    position: relative;
}}

.left::before {{
    content: "";
    position: absolute;
    right: -120px;
    top: -100px;
    width: 450px;
    height: 450px;
    background: rgba(86, 145, 255, .10);
    border-radius: 50%;
}}

.logo {{
    display: flex;
    align-items: center;
    gap: 15px;
    z-index: 2;
}}

.logo-box {{
    width: 58px;
    height: 58px;
    border-radius: 18px;
    background: linear-gradient(135deg, #4788ff, #8b5cf6);
    display: flex;
    justify-content: center;
    align-items: center;
    color: #fff;
    font-size: 26px;
    box-shadow: 0 18px 40px rgba(71, 136, 255, .35);
}}

.logo h2 {{
    font-size: 28px;
    font-weight: 800;
    color: #183153;
}}

.hero {{
    z-index: 2;
    margin-top: 30px;
}}

.hero h1 {{
    font-size: 38px;
    line-height: 1.15;
}}

.hero h1 span {{
    background: linear-gradient(90deg, #4f8dff, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.hero p {{
    margin-top: 16px;
    font-size: 15px;
    line-height: 1.5;
    max-width: 520px;
    color: #617086;
}}

.feature-grid {{
    display: grid;
    grid-template-rows: repeat(4, 1fr);
    gap: 10px;
    margin-top: 18px;
    z-index: 2;
}}

.feature {{
    background: rgba(255, 255, 255, .6);
    backdrop-filter: blur(18px);
    border-radius: 20px;
    padding: 12px;
    height: 90px;
    width: 420px;
    transition: .35s;
    box-shadow: 0 18px 35px rgba(0, 0, 0, .05);
    display: flex;
    align-items: center;
    gap:16px;
}}

.feature:hover {{
    transform: translateY(-6px);
}}

.feature i {{
    font-size: 20px;
    margin-bottom: 8px;
    color: #4f8dff;
}}

.feature h3 {{
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 4px;
    color: #183153;
}}

.feature p {{
    font-size: 12px;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    color: #6b7a8e;
}}

.middle {{
    flex: 0.8;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 18px;
    padding: 20px 10px;
}}

.progress-card {{
    width: 100%;
    max-width: 280px;
    background: rgba(255, 255, 255, .8);
    border-radius: 25px;
    padding: 22px 24px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, .08);
}}

.progress-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}}

.progress-header h3 {{
    color: #183153;
    font-size: 17px;
    font-weight: 700;
}}

.progress-header .percent {{
    color: #4f8dff;
    font-weight: 700;
    font-size: 14px;
}}

.progress-bar {{
    width: 100%;
    height: 8px;
    border-radius: 20px;
    background: #edf2fb;
    overflow: hidden;
}}

.progress-bar-fill {{
    width: 72%;
    height: 100%;
    background: linear-gradient(90deg, #4f8dff, #8b5cf6);
    border-radius: 20px;
}}

.progress-stats {{
    display: flex;
    justify-content: space-between;
    margin-top: 16px;
}}

.stat-item {{
    text-align: center;
}}

.stat-item .number {{
    color: #183153;
    font-size: 22px;
    font-weight: 800;
}}

.stat-item .label {{
    color: #7b8797;
    font-size: 11px;
    font-weight: 500;
    display: block;
    margin-top: 2px;
}}

.exam-card {{
    width: 100%;
    max-width: 280px;
    background: rgba(255, 255, 255, .8);
    border-radius: 25px;
    padding: 14px 22px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, .08);
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.exam-info h4 {{
    color: #7b8797;
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.exam-info h3 {{
    color: #183153;
    font-size: 15px;
    font-weight: 700;
    margin-top: 2px;
}}

.exam-days {{
    background: linear-gradient(135deg, #4f8dff, #8b5cf6);
    color: white;
    border-radius: 50px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: 700;
    white-space: nowrap;
}}

.right {{
    flex: 0.9;
    display: flex;
    justify-content: center;
    align-items: center;
}}

.login-card {{
    width: 100%;
    max-width: 380px;
    background: rgba(255, 255, 255, .6);
    backdrop-filter: blur(25px);
    border-radius: 30px;
    padding: 35px 30px;
    box-shadow: 0 25px 60px rgba(0, 0, 0, .08);
    margin-right:23px;
}}

.login-icon {{
    width: 65px;
    height: 65px;
    border-radius: 18px;
    background: linear-gradient(135deg, #4f8dff, #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 28px;
    margin: 0 auto 18px auto;
}}

.login-card h2 {{
    font-size: 28px;
    font-weight: 800;
    color: #183153;
    text-align: center;
    margin-bottom: 4px;
}}

.login-card > p {{
    font-size: 14px;
    color: #7b8797;
    text-align: center;
    margin-bottom: 20px;
}}

.form-group {{
    margin-bottom: 12px;
}}

.form-group label {{
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: #183153;
    margin-bottom: 4px;
}}

.input {{
    width: 100%;
    height: 48px;
    border-radius: 12px;
    border: 2px solid #e8eef8;
    padding: 0 16px;
    font-size: 14px;
    transition: .3s;
    background: white;
}}

.input:focus {{
    outline: none;
    border-color: #4f8dff;
    box-shadow: 0 0 0 4px rgba(79, 141, 255, .12);
}}

.input::placeholder {{
    color: #a0b0c0;
}}

.forgot-link {{
    display: block;
    text-align: right;
    color: #4f8dff;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none;
    margin: 2px 0 16px 0;
}}

.forgot-link:hover {{
    text-decoration: underline;
}}

.login-btn {{
    width: 100%;
    height: 50px;
    border: none;
    border-radius: 14px;
    background: linear-gradient(90deg, #4f8dff, #8b5cf6);
    color: white;
    font-size: 16px;
    font-weight: 700;
    cursor: pointer;
    transition: .35s;
    box-shadow: 0 16px 35px rgba(79, 141, 255, .3);
}}

.login-btn:hover {{
    transform: translateY(-3px);
    box-shadow: 0 20px 45px rgba(79, 141, 255, .4);
}}

.divider {{
    display: flex;
    align-items: center;
    gap: 15px;
    margin: 18px 0 14px 0;
}}

.divider hr {{
    flex: 1;
    border: none;
    height: 1px;
    background: #e8eef8;
}}

.divider span {{
    color: #a0b0c0;
    font-size: 12px;
    font-weight: 500;
    white-space: nowrap;
}}

.social-buttons {{
    display: flex;
    gap: 10px;
}}

.social-btn {{
    flex: 1;
    height: 46px;
    border-radius: 12px;
    border: 2px solid #e8eef8;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    color: #183153;
    cursor: pointer;
    transition: .3s;
}}

.social-btn:hover {{
    border-color: #4f8dff;
    background: #f7faff;
}}

.social-btn i {{
    font-size: 16px;
}}

.auth-link {{
    color: #4f8dff;
    font-weight: 700;
    text-decoration: none;
    cursor: pointer;
}}

.auth-link:hover {{
    text-decoration: underline;
}}

.signup-link {{
    text-align: center;
    margin-top: 16px;
    font-size: 14px;
    color: #7b8797;
}}

/* ========== MOBILE RESPONSIVE ========== */
@media (max-width: 1200px) {{
    .container {{
        flex-wrap: wrap;
        height: auto;
        min-height: 90vh;
        padding: 20px;
        gap: 20px;
    }}
    .left {{
        flex: 1 1 100%;
        padding: 30px;
    }}
    .middle {{
        flex: 1 1 100%;
        flex-direction: row;
        flex-wrap: wrap;
        justify-content: center;
        width: 100%;
        padding: 10px;
    }}
    .right {{
        flex: 1 1 100%;
        padding: 20px;
    }}
    .login-card {{
        max-width: 450px;
        margin-right: 0;
    }}
    .progress-card, .exam-card {{
        max-width: 300px;
    }}
}}

@media (max-width: 768px) {{
    .container {{
        flex-direction: column !important;
        padding: 15px !important;
        border-radius: 25px !important;
        min-height: auto !important;
    }}
    .left {{
        padding: 20px !important;
        flex: 1 1 auto !important;
    }}
    .middle {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
        padding: 10px !important;
        gap: 12px !important;
    }}
    .progress-card, .exam-card {{
        max-width: 100% !important;
        padding: 12px 16px !important;
    }}
    .progress-stats {{
        gap: 8px !important;
    }}
    .progress-stats .stat-item .number {{
        font-size: 18px !important;
    }}
    .right {{
        padding: 10px !important;
        width: 100% !important;
        flex: 1 1 auto !important;
    }}
    .login-card {{
        max-width: 100% !important;
        padding: 25px 20px !important;
        margin-right: 0 !important;
        border-radius: 20px !important;
    }}
    .login-card h2 {{
        font-size: 24px !important;
    }}
    .hero h1 {{
        font-size: 30px !important;
    }}
    .hero p {{
        font-size: 13px !important;
    }}
    .feature-grid {{
        grid-template-columns: 1fr 1fr !important;
        gap: 8px !important;
    }}
    .feature {{
        width: 100% !important;
        height: auto !important;
        padding: 10px !important;
        gap: 10px !important;
        border-radius: 14px !important;
    }}
    .feature i {{
        font-size: 16px !important;
    }}
    .feature h3 {{
        font-size: 12px !important;
    }}
    .feature p {{
        font-size: 10px !important;
    }}
    .logo h2 {{
        font-size: 22px !important;
    }}
    .logo-box {{
        width: 46px !important;
        height: 46px !important;
        font-size: 20px !important;
    }}
    .login-btn {{
        height: 44px !important;
        font-size: 14px !important;
    }}
    .input {{
        height: 42px !important;
        font-size: 13px !important;
    }}
}}

@media (max-width: 480px) {{
    body {{
        padding: 8px !important;
    }}
    .container {{
        padding: 10px !important;
        border-radius: 18px !important;
    }}
    .left {{
        padding: 15px !important;
    }}
    .hero h1 {{
        font-size: 24px !important;
    }}
    .hero p {{
        font-size: 12px !important;
        margin-top: 10px !important;
    }}
    .feature-grid {{
        grid-template-columns: 1fr !important;
    }}
    .login-card {{
        padding: 20px 15px !important;
    }}
    .login-card h2 {{
        font-size: 20px !important;
    }}
    .login-icon {{
        width: 50px !important;
        height: 50px !important;
        font-size: 22px !important;
        margin-bottom: 12px !important;
    }}
    .logo h2 {{
        font-size: 18px !important;
    }}
    .logo-box {{
        width: 38px !important;
        height: 38px !important;
        font-size: 16px !important;
    }}
    .social-buttons {{
        flex-direction: column !important;
        gap: 6px !important;
    }}
    .form-group label {{
        font-size: 12px !important;
    }}
    .signup-link {{
        font-size: 12px !important;
    }}
}}
        </style>
    </head>
    <body>
    <div class="container">
        <div class="left">
            <div class="logo">
                <div class="logo-box">
                    <i class="fas fa-graduation-cap"></i>
                </div>
                <h2>Steady Study</h2>
            </div>

            <div class="hero">
                <h1>
                    Plan Smarter,<br>
                    <span>Study Better.</span>
                </h1>
                <p>
                    AI-powered study planning to help you stay organized, 
                    focused, and achieve more every day.
                </p>
            </div>

            <div class="feature-grid">
                <div class="feature">
                    <div class="icon">
                    <i class="fas fa-calendar-check"></i>
                    </div>
                    <div class="feature-text">
                    <h3>Smart Study Plan</h3>
                    <p>Get a personalized plan tailored to your goals and schedule.</p>
                    </div>
                </div>

                <div class="feature">
                <div class="icon">
                    <i class="fas fa-chart-line"></i>
                    </div>
                    <div class="feature-text">
                    <h3>Track Progress</h3>
                    <p>Monitor your progress and stay motivated every day.</p>
                    </div>
                </div>

                <div class="feature">
                <div class="icon">
                    <i class="fas fa-robot"></i>
                    </div>
                    <div class="feature-text">
                    <h3>AI Assistant</h3>
                    <p>Get intelligent suggestions and answers to your study questions.</p>
                    </div>
                </div>

                <div class="feature">
                <div class="icon">
                    <i class="fas fa-book-open"></i>
                    </div>
                     <div class="feature-text">
                    <h3>Learning Hub</h3>
                    <p>Store notes, organize resources, and manage every subject easily.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="middle">
            <div class="progress-card">
                <div class="progress-header">
                    <h3>Today's Progress</h3>
                    <span class="percent">72%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-bar-fill"></div>
                </div>
                <div class="progress-stats">
                    <div class="stat-item">
                        <span class="number">5.6h</span>
                        <span class="label">Study Time</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">8/12</span>
                        <span class="label">Tasks Done</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">4</span>
                        <span class="label">Subjects</span>
                    </div>
                </div>
            </div>

            <div class="exam-card">
                <div class="exam-info">
                    <h4>Upcoming Exam</h4>
                    <h3>Machine Learning</h3>
                </div>
                <div class="exam-days">12 Days Left</div>
            </div>
        </div>

        <div class="right">
            <div class="login-card">
            
                <div class="login-icon">
                    <i class="fas fa-graduation-cap"></i>
                </div>
                <h2>{title}</h2>
                <p>{subtitle}</p>

                {name_field}

                <div class="form-group">
                    <label>{email_label}</label>
                    <input id="email_input" class="input" type="text" placeholder="{email_placeholder}" />
                </div>

                <div class="form-group">
                    <label>Password</label>
                    <input id="password_input" class="input" type="password" placeholder="Enter your password" />
                </div>

                {confirm_field}

                {forgot_password}

                <button class="login-btn" id="submitBtn">
                    <i class="fas fa-{button_icon}" style="margin-right: 8px;"></i> {button_text}
                </button>

                <p class="signup-link">
                    {signup_link_text}
                </p>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('submitBtn').addEventListener('click', function(e) {{
            e.preventDefault();
            
            var email = document.getElementById('email_input').value;
            var password = document.getElementById('password_input').value;
            
            {js_code}
        }});
    </script>
    </body>
    </html>
    """
    
    # ✅ scrolling=True နဲ့ height ကိုပြင်ပါ
    components.html(html_content, height=1000, scrolling=True)