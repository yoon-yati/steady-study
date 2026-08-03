# planner.py - Student Planner (No Quick Actions, Clean UI)
import streamlit as st
import json
from datetime import datetime, timedelta
from data_manager import save_plans_db, get_plans_for_user
from learning_subjects import LEARNING_SUBJECTS
from auth import save_goals, save_notes

# ===== Helper function for profile picture =====
def get_profile_picture(username):
    """Get profile picture from session state or users_db"""
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


def show_planner_page():
    username = st.session_state.get("username", "Yoon")
    
    # ===== Load user plans =====
    user_plans = get_plans_for_user(username)
    
    # ===== Initialize session states =====
    if "goals" not in st.session_state:
        st.session_state["goals"] = {}
    if "notes" not in st.session_state:
        st.session_state["notes"] = {}
    if "planner_tab" not in st.session_state:
        st.session_state["planner_tab"] = "all"
    
    # ===== Get profile picture =====
    profile_pic = get_profile_picture(username)
    if profile_pic:
        avatar_html = f'<img src="{profile_pic}" alt="Profile picture"/>'
    else:
        avatar_html = username[0].upper()
    
    # ===== FONT AWESOME CDN =====
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    """, unsafe_allow_html=True)
    
    # ===== HIDE STREAMLIT TOOLBAR =====
    st.markdown("""
    <style>
        header { display: none !important; }
        .stDeployButton { display: none !important; }
        [data-testid="stToolbar"] { display: none !important; }
        [data-testid="stHeader"] { display: none !important; }
        .stAppDeployButton { display: none !important; }
        footer { display: none !important; }
        .st-emotion-cache-1cypcdb { display: none !important; }
        button[data-testid="baseButton-header"] { display: none !important; }
        .main > div { padding-top: 0 !important; }
        .block-container { padding-top: 0.5rem !important; padding-bottom: 4rem !important; }
        .st-emotion-cache-1r6slb0 { display: none !important; }
        .st-emotion-cache-1v3fvcr { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }
        .st-emotion-cache-12w0qpk { padding-top: 0 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # ===== CSS =====
    st.markdown("""
    <style>
        * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
        
        /* Main Header with Welcome Box */
        .main-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            flex-wrap: wrap;
            gap: 12px;
        }
        .header-left {
            display: flex;
            align-items: center;
            gap: 16px;
            flex: 1;
        }
        .welcome-box {
            background: white;
            border-radius: 14px;
            padding: 12px 20px;
            border: 1px solid #eef2f6;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            display: flex;
            align-items: center;
            gap: 12px;
            flex: 1;
        }
        .welcome-box .avatar {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4f8dff, #8b5cf6);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: 700;
            color: white;
            flex-shrink: 0;
            overflow: hidden;
            border: 2px solid #4f8dff;
        }
        .welcome-box .avatar img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 50%;
        }
        .welcome-box .welcome-content {
            flex: 1;
        }
        .welcome-box .welcome-content .title {
            font-size: 18px;
            font-weight: 700;
            color: #183153;
            margin: 0;
        }
        .welcome-box .welcome-content .title i { 
            color: #4f8dff; 
            margin-right: 8px;
        }
        .welcome-box .welcome-content .subtitle {
            font-size: 13px;
            color: #7b8797;
            margin: 2px 0 0 0;
        }
        .welcome-box .welcome-content .subtitle .greeting { 
            color: #4f8dff; 
            font-weight: 600;
        }
        .welcome-box .date-badge {
            background: #f8faff;
            padding: 6px 14px;
            border-radius: 10px;
            border: 1px solid #eef2f6;
            font-size: 12px;
            color: #7b8797;
            white-space: nowrap;
        }
        .welcome-box .date-badge i { 
            color: #4f8dff; 
            margin-right: 6px;
        }
        
        .two-col-focus {
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 20px !important;
            margin-bottom: 20px !important;
        }
        
        .focus-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            background: white;
            border-radius: 12px;
            border: 1px solid #eef2f6;
            margin-bottom: 8px;
            transition: all 0.2s ease;
        }
        .focus-item:hover { border-color: #d6e4ff; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
        .focus-item .color-bar { width: 4px; height: 32px; border-radius: 4px; flex-shrink: 0; }
        .focus-item .focus-info { flex: 1; }
        .focus-item .focus-info .task { font-size: 14px; font-weight: 600; color: #183153; }
        .focus-item .focus-info .meta { font-size: 11px; color: #7b8797; }
        .focus-item .focus-info .meta i { margin-right: 2px; }
        .focus-item .focus-tag { font-size: 10px; padding: 2px 12px; border-radius: 12px; font-weight: 600; }
        .tag-cs { background: #d5f5e3; color: #27ae60; }
        .tag-db { background: #fdebd0; color: #e67e22; }
        .tag-ai { background: #e8daef; color: #8e44ad; }
        .tag-personal { background: #d6eaf8; color: #2e86c1; }
        .tag-general { background: #fadbd8; color: #922b21; }
        
        .deadline-item {
            background: white;
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 8px;
            border: 1px solid #eef2f6;
            transition: all 0.2s ease;
        }
        .deadline-item:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
        .deadline-item .title { font-weight: 600; color: #183153; font-size: 14px; }
        .deadline-item .title i { color: #4f8dff; margin-right: 8px; }
        .deadline-item .meta { font-size: 12px; color: #7b8797; }
        .deadline-item .meta i { margin-right: 4px; }
        .deadline-item .days {
            padding: 2px 14px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
            display: inline-block;
            margin-top: 4px;
        }
        .days-urgent { background: #fdebd0; color: #e67e22; }
        .days-normal { background: #d6eaf8; color: #2e86c1; }
        .days-far { background: #d5f5e3; color: #27ae60; }
        
        .progress-container {
            background: white;
            border-radius: 12px;
            padding: 12px 16px;
            border: 1px solid #eef2f6;
            margin-top: 12px;
        }
        .progress-container .progress-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .progress-container .progress-top span {
            font-size: 13px;
            color: #7b8797;
        }
        .progress-container .progress-top .num {
            font-size: 18px;
            font-weight: 700;
            color: #4f8dff;
        }
        .progress-bar-track {
            width: 100%;
            height: 6px;
            background: #eef2f6;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 4px;
        }
        .progress-bar-track .fill {
            height: 100%;
            background: linear-gradient(90deg, #4f8dff, #6c5ce7);
            border-radius: 10px;
            transition: width 0.8s ease;
        }
        
        /* Goal Cards with Delete icon inline */
        .goal-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #f8faff;
            border-radius: 12px;
            padding: 10px 14px;
            border-left: 4px solid #6c5ce7;
            margin-bottom: 8px;
            transition: all 0.2s ease;
        }
        .goal-card:hover { background: #f0f4fe; }
        .goal-card .goal-content { flex: 1; }
        .goal-card .goal-title { font-weight: 600; color: #183153; font-size: 14px; }
        .goal-card .goal-title i { color: #6c5ce7; margin-right: 8px; }
        .goal-card .goal-meta { font-size: 11px; color: #7b8797; }
        
        /* Note Cards with Delete icon inline */
        .note-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #fef9e7;
            border-radius: 12px;
            padding: 10px 14px;
            border-left: 4px solid #fdcb6e;
            margin-bottom: 8px;
        }
        .note-card .note-content { flex: 1; }
        .note-card .note-text { font-size: 13px; color: #183153; }
        .note-card .note-text i { color: #fdcb6e; margin-right: 8px; }
        .note-card .note-date { font-size: 10px; color: #7b8797; }
        .note-card .note-date i { margin-right: 4px; }
        
        .plan-card {
            background: white;
            border-radius: 14px;
            padding: 16px 18px;
            border: 1px solid #eef2f6;
            margin-bottom: 12px;
            transition: all 0.3s ease;
        }
        .plan-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
        .plan-card .plan-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
        }
        .plan-card .plan-title { font-size: 16px; font-weight: 700; color: #183153; }
        .plan-card .plan-subjects { display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0; }
        .plan-card .plan-subjects .subj-tag { padding: 3px 14px; border-radius: 14px; font-size: 11px; font-weight: 600; }
        .subj-python { background: #d5f5e3; color: #1a7a42; }
        .subj-ai { background: #e8daef; color: #6c3483; }
        .subj-db { background: #fdebd0; color: #a04000; }
        .subj-web { background: #d6eaf8; color: #1a5276; }
        .subj-english { background: #fadbd8; color: #922b21; }
        .subj-default { background: #eaf2f8; color: #2c3e50; }
        
        .plan-card .plan-meta {
            display: flex;
            gap: 12px;
            font-size: 12px;
            color: #7b8797;
            flex-wrap: wrap;
            margin: 4px 0;
        }
        .plan-card .plan-meta span { background: #f8faff; padding: 2px 12px; border-radius: 10px; }
        .badge { padding: 3px 16px; border-radius: 14px; font-size: 11px; font-weight: 600; }
        .badge-completed { background: #d5f5e3; color: #27ae60; }
        .badge-inprogress { background: #fdebd0; color: #e67e22; }
        .badge-pending { background: #eaf2f8; color: #5b7a8a; }
        
        .progress-bar-bg {
            width: 100%;
            height: 6px;
            background: #eef2f6;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 8px;
        }
        .progress-bar-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 0.8s ease;
        }
        .progress-blue { background: linear-gradient(90deg, #4f8dff, #6c5ce7); }
        .progress-green { background: linear-gradient(90deg, #00b894, #00cec9); }
        .progress-orange { background: linear-gradient(90deg, #fdcb6e, #e17055); }
        .progress-purple { background: linear-gradient(90deg, #a29bfe, #6c5ce7); }
        .progress-pink { background: linear-gradient(90deg, #fd79a8, #e84393); }
        
        .side-section {
            background: white;
            border-radius: 14px;
            padding: 16px;
            border: 1px solid #eef2f6;
            margin-bottom: 16px;
        }
        .side-section .side-title {
            font-size: 16px;
            font-weight: 700;
            color: #183153;
            margin-bottom: 12px;
        }
        .side-section .side-title i { color: #4f8dff; margin-right: 8px; }
        .side-section .side-title span { color: #7b8797; font-weight: 400; font-size: 12px; }
        
        .custom-divider {
            border: none;
            border-top: 2px solid #eef2f6;
            margin: 16px 0;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 700;
            color: #183153;
            margin: 0 0 12px 0;
        }
        .section-title i { color: #4f8dff; margin-right: 8px; }
        
        .cal-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 2px;
            margin-top: 6px;
        }
        .cal-grid .cal-day {
            text-align: center;
            font-size: 12px;
            padding: 4px 0;
            border-radius: 6px;
            color: #183153;
        }
        .cal-grid .cal-day.weekend { color: #e74c3c; }
        .cal-grid .cal-day.today { background: #4f8dff; color: white; font-weight: 700; }
        .cal-grid .cal-day.other { color: #b0b8c4; }
        .cal-grid .cal-day .dot {
            display: inline-block;
            width: 4px;
            height: 4px;
            background: #4f8dff;
            border-radius: 50%;
            margin-top: 1px;
        }
        
        .study-overview {
            background: white;
            border-radius: 14px;
            padding: 14px 16px;
            border: 1px solid #eef2f6;
            margin-top: 12px;
        }
        .study-overview .title {
            font-weight: 700;
            color: #183153;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .study-overview .grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
        }
        .study-overview .grid .item {
            text-align: center;
        }
        .study-overview .grid .item .num {
            font-size: 18px;
            font-weight: 800;
        }
        .study-overview .grid .item .label {
            font-size: 10px;
            color: #7b8797;
        }
        .study-overview .footer {
            text-align: center;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #eef2f6;
            font-size: 12px;
            color: #27ae60;
            font-weight: 600;
        }
        
        .plan-delete-btn {
            color: #e74c3c;
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 6px;
            transition: all 0.2s ease;
            font-size: 18px;
            background: transparent;
            border: none;
            opacity: 0.5;
        }
        .plan-delete-btn:hover {
            opacity: 1;
            background: #fde8e8;
        }
        
        @media (max-width: 768px) {
            .two-col-focus { grid-template-columns: 1fr !important; }
            .main-header { flex-direction: column; align-items: stretch; }
            .header-left { flex-wrap: wrap; }
            .welcome-box { flex-wrap: wrap; }
            .welcome-box .date-badge { margin-left: auto; }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # ===== MAIN HEADER WITH WELCOME BOX =====
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    st.markdown(f"""
    <div class="main-header">
        <div class="header-left">
            <div class="welcome-box">
                <div class="avatar">{avatar_html}</div>
                <div class="welcome-content">
                    <div class="title"><i class="fas fa-clipboard-list"></i> Planner</div>
                    <div class="subtitle">{greeting}, <span class="greeting">{username}</span>! Let's plan your day and achieve your goals.</div>
                </div>
                <div class="date-badge">
                    <i class="fas fa-calendar-day"></i> {datetime.now().strftime('%B %d, %Y')}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== TODAY'S FOCUS + UPCOMING DEADLINES =====
    st.markdown('<div class="two-col-focus">', unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="section-title"><i class="fas fa-bullseye"></i> Today\'s Focus</div>', unsafe_allow_html=True)
        
        focus_items = []
        color_classes = ["#4f8dff", "#00b894", "#6c5ce7", "#fdcb6e", "#e17055"]
        tag_classes = ["tag-cs", "tag-db", "tag-ai", "tag-personal", "tag-general"]
        tag_names = ["CS", "DB", "AI", "Personal", "General"]
        
        for plan in user_plans:
            for subj in plan.get("subjects", []):
                if subj.get("status") != "completed":
                    focus_items.append({
                        "task": subj.get("topic", "Unknown"),
                        "category": plan.get("title", "General"),
                        "time": plan.get("start_time", "9:00 AM")
                    })
        
        if not focus_items:
            focus_items = [
                {"task": "Data Structures Assignment", "category": "CS", "time": "9:00 AM"},
                {"task": "Database Study", "category": "DB", "time": "11:00 AM"},
                {"task": "AI Project", "category": "AI", "time": "2:00 PM"},
                {"task": "English Practice", "category": "General", "time": "4:00 PM"},
                {"task": "Gym Workout", "category": "Personal", "time": "6:00 PM"}
            ]
        
        for i, item in enumerate(focus_items[:5]):
            color = color_classes[i % len(color_classes)]
            tag_class = tag_classes[i % len(tag_classes)]
            tag_name = tag_names[i % len(tag_names)]
            st.markdown(f"""
            <div class="focus-item">
                <div class="color-bar" style="background:{color};"></div>
                <div class="focus-info">
                    <div class="task">{item['task']}</div>
                    <div class="meta"><i class="fas fa-tag"></i> {item['category']} • <i class="far fa-clock"></i> {item['time']}</div>
                </div>
                <span class="focus-tag {tag_class}">{tag_name}</span>
            </div>
            """, unsafe_allow_html=True)
        
        total_tasks = len(focus_items)
        completed_tasks = sum(1 for plan in user_plans for subj in plan.get("subjects", []) if subj.get("status") == "completed")
        if total_tasks == 0:
            total_tasks = 5
            completed_tasks = 2
        progress_pct = int((completed_tasks / total_tasks) * 100)
        
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-top">
                <span><i class="fas fa-tasks" style="color:#4f8dff;"></i> {completed_tasks} of {total_tasks} tasks completed</span>
                <span class="num">{progress_pct}%</span>
            </div>
            <div class="progress-bar-track">
                <div class="fill" style="width:{progress_pct}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="section-title"><i class="fas fa-clock"></i> Upcoming Deadlines</div>', unsafe_allow_html=True)
        
        deadlines = []
        if user_plans:
            for plan in user_plans[:4]:
                days = plan.get('days_left', plan.get('weeks', 0) * 7)
                deadlines.append({
                    "title": plan.get('title', 'Plan'),
                    "date": plan.get('start_date', ''),
                    "days": days
                })
        
        if not deadlines:
            deadlines = [
                {"title": "Database Project Report", "date": "May 26, 2025", "days": 2},
                {"title": "AI Assignment", "date": "May 28, 2025", "days": 4},
                {"title": "Web Development Project", "date": "May 31, 2025", "days": 7},
                {"title": "Math Quiz", "date": "Jun 2, 2025", "days": 9}
            ]
        
        for item in deadlines[:4]:
            days = item['days']
            if days <= 3:
                days_class = "days-urgent"
            elif days <= 7:
                days_class = "days-normal"
            else:
                days_class = "days-far"
            
            st.markdown(f"""
            <div class="deadline-item">
                <div class="title"><i class="fas fa-file-alt"></i> {item['title']}</div>
                <div class="meta"><i class="far fa-calendar-alt"></i> {item['date']}</div>
                <span class="days {days_class}">{days} days left</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    
    # ===== THREE COLUMN: Goals + Notes + Create =====
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("""
        <div class="side-section">
            <div class="side-title"><i class="fas fa-flag-checkered"></i> My Goals <span>• Active</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        user_goals = st.session_state["goals"].get(username, [])
        active_goals = [g for g in user_goals if g.get("status") != "Completed"]
        
        if active_goals:
            for i, goal in enumerate(active_goals[:3]):
                col_goal1, col_goal2 = st.columns([5, 1])
                with col_goal1:
                    st.markdown(f"""
                    <div class="goal-card">
                        <div class="goal-content">
                            <div class="goal-title"><i class="fas fa-check-circle"></i> {goal.get('title', 'Goal')}</div>
                            <div class="goal-meta">{goal.get('description', '')[:40]}{'...' if len(goal.get('description', '')) > 40 else ''}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_goal2:
                    if st.button("🗑️", key=f"del_goal_{i}", help="Delete this goal"):
                        if username in st.session_state["goals"]:
                            goals = st.session_state["goals"][username]
                            for idx_g, g in enumerate(goals):
                                if g.get('title') == goal.get('title') and g.get('created_at') == goal.get('created_at'):
                                    del goals[idx_g]
                                    break
                            save_goals()
                            st.rerun()
        else:
            st.markdown("""
            <div style="text-align:center; padding:16px; color:#7b8797; font-size:13px;">
                <i class="fas fa-plus-circle" style="color:#4f8dff;"></i> No active goals. Set one!
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("➕ Add Goal", expanded=False):
            with st.form("quick_goal_form"):
                goal_title = st.text_input("Title", placeholder="e.g., Master Python")
                goal_desc = st.text_input("Description", placeholder="Brief description")
                col_a, col_b = st.columns(2)
                with col_a:
                    goal_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                with col_b:
                    goal_progress = st.slider("Progress", 0, 100, 0)
                
                if st.form_submit_button("🎯 Add Goal", use_container_width=True):
                    if goal_title:
                        if username not in st.session_state["goals"]:
                            st.session_state["goals"][username] = []
                        st.session_state["goals"][username].append({
                            "title": goal_title,
                            "description": goal_desc,
                            "deadline": (datetime.now().date() + timedelta(days=30)).strftime("%Y-%m-%d"),
                            "priority": goal_priority,
                            "progress": goal_progress,
                            "status": "Active",
                            "created_at": datetime.now().strftime("%Y-%m-%d")
                        })
                        save_goals()
                        st.success("✅ Goal added!")
                        st.rerun()
                    else:
                        st.error("Enter a title!")
    
    with col2:
        st.markdown("""
        <div class="side-section">
            <div class="side-title"><i class="fas fa-sticky-note"></i> Quick Notes</div>
        </div>
        """, unsafe_allow_html=True)
        
        user_notes = st.session_state["notes"].get(username, [])
        
        if user_notes:
            for i, note in enumerate(user_notes[-3:]):
                col_note1, col_note2 = st.columns([5, 1])
                with col_note1:
                    st.markdown(f"""
                    <div class="note-card">
                        <div class="note-content">
                            <div class="note-text"><i class="fas fa-pencil-alt"></i> {note.get('content', '')[:50]}{'...' if len(note.get('content', '')) > 50 else ''}</div>
                            <div class="note-date"><i class="far fa-calendar-alt"></i> {note.get('created_at', '')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_note2:
                    if st.button("🗑️", key=f"del_note_{i}", help="Delete this note"):
                        if username in st.session_state["notes"]:
                            notes = st.session_state["notes"][username]
                            for idx_n, n in enumerate(notes):
                                if n.get('content') == note.get('content') and n.get('created_at') == note.get('created_at'):
                                    del notes[idx_n]
                                    break
                            save_notes()
                            st.rerun()
        else:
            st.markdown("""
            <div style="text-align:center; padding:16px; color:#7b8797; font-size:13px;">
                <i class="fas fa-plus-circle" style="color:#4f8dff;"></i> No notes yet. Add one!
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("📝 Add Note", expanded=False):
            with st.form("quick_note_form"):
                note_content = st.text_area("Note", height=60, placeholder="Write something...")
                if st.form_submit_button("📝 Save Note", use_container_width=True):
                    if note_content:
                        if username not in st.session_state["notes"]:
                            st.session_state["notes"][username] = []
                        st.session_state["notes"][username].append({
                            "content": note_content,
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        save_notes()
                        st.success("✅ Note saved!")
                        st.rerun()
                    else:
                        st.error("Enter some text!")
    
    with col3:
        st.markdown("""
        <div class="side-section">
            <div class="side-title"><i class="fas fa-plus-circle"></i> Create New Plan</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📝 Simple Plan", expanded=True):
            with st.form("simple_plan_form"):
                plan_title = st.text_input("Plan Title", placeholder="e.g., Data Structures")
                col_a, col_b = st.columns(2)
                with col_a:
                    weeks = st.number_input("Weeks", min_value=1, max_value=52, value=4)
                with col_b:
                    hours = st.number_input("Hours/day", min_value=1, max_value=12, value=4)
                
                all_subjects = list(LEARNING_SUBJECTS.keys())
                selected = st.multiselect("Subjects", all_subjects, default=all_subjects[:2] if all_subjects else [])
                
                if st.form_submit_button("🚀 Create Plan", use_container_width=True):
                    if not plan_title:
                        st.error("Enter a title!")
                    elif not selected:
                        st.error("Select at least one subject!")
                    else:
                        new_plan = {
                            "id": f"plan_{datetime.now().timestamp()}",
                            "title": plan_title,
                            "subjects": [{"topic": t, "status": "pending", "progress": 0} for t in selected],
                            "weeks": int(weeks),
                            "hours_per_day": int(hours),
                            "start_date": datetime.now().strftime("%Y-%m-%d"),
                            "status": "in_progress",
                            "progress": 0,
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "days_left": int(weeks) * 7
                        }
                        
                        if username not in st.session_state["plans_db"]:
                            st.session_state["plans_db"][username] = []
                        st.session_state["plans_db"][username].append(new_plan)
                        save_plans_db(st.session_state["plans_db"])
                        
                        st.success("✅ Plan created!")
                        st.rerun()
        
        with st.expander("➕ Add New Subject", expanded=False):
            with st.form("advanced_plan_form"):
                st.markdown("#### 📚 Plan Details")
                plan_title = st.text_input("Plan Title", placeholder="e.g., React Learning Plan")
                col_a, col_b = st.columns(2)
                with col_a:
                    weeks = st.number_input("Weeks", min_value=1, max_value=52, value=4)
                with col_b:
                    hours = st.number_input("Hours/day", min_value=1, max_value=12, value=4)
                
                st.markdown("---")
                st.markdown("#### ➕ Add New Subject")
                
                col_c, col_d = st.columns(2)
                with col_c:
                    new_subject_name = st.text_input("Subject Name", placeholder="e.g., React.js")
                with col_d:
                    new_subject_icon = st.text_input("Icon", placeholder="⚛️", value="📚")
                
                new_subject_desc = st.text_input("Description", placeholder="Brief description")
                
                st.markdown("#### 📹 Add Videos")
                st.caption("Format: Title, URL (one per line)")
                new_video_input = st.text_area(
                    "Video links",
                    placeholder="Python Basics, https://youtu.be/xxx\nFunctions, https://youtu.be/yyy",
                    height=80
                )
                
                if st.form_submit_button("➕ Add Subject & Create Plan", use_container_width=True):
                    if not plan_title:
                        st.error("Please enter a plan title!")
                    elif not new_subject_name:
                        st.error("Please enter a subject name!")
                    elif not new_video_input:
                        st.error("Please add at least one video link!")
                    else:
                        videos = []
                        for line in new_video_input.strip().split("\n"):
                            if "," in line:
                                title, url = line.split(",", 1)
                                videos.append({"title": title.strip(), "url": url.strip()})
                            elif "youtu" in line:
                                videos.append({"title": new_subject_name, "url": line.strip()})
                        
                        if not videos:
                            st.error("Please add valid video links!")
                        else:
                            LEARNING_SUBJECTS[new_subject_name] = {
                                "icon": new_subject_icon or "📚",
                                "description": new_subject_desc or f"Learn {new_subject_name}",
                                "roadmap": {"Beginner": videos}
                            }
                            
                            if "subjects" not in st.session_state:
                                st.session_state["subjects"] = []
                            if new_subject_name not in [s.get("topic") for s in st.session_state["subjects"]]:
                                st.session_state["subjects"].append({
                                    "topic": new_subject_name,
                                    "skill": "beginner",
                                    "progress": 0
                                })
                            
                            new_plan = {
                                "id": f"plan_{datetime.now().timestamp()}",
                                "title": plan_title,
                                "subjects": [{"topic": new_subject_name, "status": "pending", "progress": 0}],
                                "weeks": int(weeks),
                                "hours_per_day": int(hours),
                                "start_date": datetime.now().strftime("%Y-%m-%d"),
                                "status": "in_progress",
                                "progress": 0,
                                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "days_left": int(weeks) * 7
                            }
                            
                            if username not in st.session_state["plans_db"]:
                                st.session_state["plans_db"][username] = []
                            st.session_state["plans_db"][username].append(new_plan)
                            save_plans_db(st.session_state["plans_db"])
                            
                            st.success(f"✅ Plan '{plan_title}' created!")
                            st.rerun()
        
        st.markdown("""
        <div style="margin-top:8px; text-align:center; font-size:12px; color:#7b8797;">
            Use <span style="color:#4f8dff; font-weight:600;">Simple Plan</span> for quick creation
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    
    # ===== MY STUDY PLAN =====
    st.markdown('<div class="section-title"><i class="fas fa-book"></i> My Study Plan</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        filter_status = st.selectbox("Filter by Status", ["All", "Completed", "In Progress", "Pending"])
    with col2:
        filter_subject = st.selectbox("Filter by Subject", ["All"] + list(set([s.get("topic", "") for plan in user_plans for s in plan.get("subjects", [])])))
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.rerun()
    
    if user_plans:
        filtered_plans = user_plans
        if filter_status != "All":
            filtered_plans = [p for p in filtered_plans if p.get("status", "pending").replace("_", " ").title() == filter_status]
        
        progress_colors = ["progress-blue", "progress-green", "progress-orange", "progress-purple", "progress-pink"]
        
        for idx, plan in enumerate(filtered_plans):
            prog_color = progress_colors[idx % len(progress_colors)]
            status = plan.get('status', 'pending')
            status_class = "badge-completed" if status == "completed" else "badge-inprogress" if status == "in_progress" else "badge-pending"
            status_text = "Completed" if status == "completed" else "In Progress" if status == "in_progress" else "Pending"
            progress = plan.get('progress', 0)
            plan_id = plan.get('id', f'plan_{idx}')
            
            col_plan1, col_plan2 = st.columns([6, 1])
            with col_plan1:
                st.markdown(f"""
                <div class="plan-card">
                    <div class="plan-header">
                        <div>
                            <div class="plan-title"><i class="fas fa-graduation-cap" style="color:#4f8dff; margin-right:8px;"></i>{plan.get('title', 'Untitled Plan')}</div>
                            <div class="plan-meta">
                                <span><i class="far fa-clock"></i> {plan.get('weeks', 0)} weeks</span>
                                <span><i class="fas fa-hourglass-half"></i> {plan.get('hours_per_day', 0)}h/day</span>
                                <span><i class="far fa-calendar-alt"></i> {plan.get('start_date', '')}</span>
                            </div>
                        </div>
                        <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                            <span style="font-size:13px; font-weight:600; color:#183153;">{progress}%</span>
                            <span class="badge {status_class}">{status_text}</span>
                        </div>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill {prog_color}" style="width:{progress}%;"></div>
                    </div>
                    <div class="plan-subjects">
                """, unsafe_allow_html=True)
                
                subject_colors = ["subj-python", "subj-ai", "subj-db", "subj-web", "subj-english", "subj-default"]
                for i, subj in enumerate(plan.get("subjects", [])[:6]):
                    subj_color = subject_colors[i % len(subject_colors)]
                    st.markdown(f"""
                    <span class="subj-tag {subj_color}"><i class="fas fa-book" style="margin-right:4px;"></i>{subj.get('topic', '')}</span>
                    """, unsafe_allow_html=True)
                
                if len(plan.get("subjects", [])) > 6:
                    st.markdown(f"""
                    <span class="subj-tag subj-default">+{len(plan.get("subjects", [])) - 6} more</span>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div></div>", unsafe_allow_html=True)
            
            with col_plan2:
                if st.button("🗑️", key=f"del_plan_{idx}_{plan_id}", help="Delete this plan"):
                    if username in st.session_state["plans_db"]:
                        plans = st.session_state["plans_db"][username]
                        for i, p in enumerate(plans):
                            if p.get('id') == plan_id:
                                del plans[i]
                                break
                        save_plans_db(st.session_state["plans_db"])
                        st.success("✅ Plan deleted!")
                        st.rerun()
    else:
        st.info("📌 No plans yet. Create your first study plan!")