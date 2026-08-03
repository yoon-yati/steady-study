# dashboard.py - CSS မပါဘဲ ရိုးရိုးဗားရှင်း
import streamlit as st
from datetime import datetime, timedelta
import calendar
from data_manager import get_plans_for_user

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

def show_dashboard():
    username = st.session_state.get("username", "Gamone Pwint Phoo")
    user_data = st.session_state.get("users_db", {}).get(username, {})
    profile = user_data.get("profile", {})
    
    user_plans = get_plans_for_user(username)
    total_plans = len(user_plans)
    total_subjects = len(st.session_state.get("subjects", []))
    
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    total_tasks = 0
    completed_tasks = 0
    for plan in user_plans:
        for subj in plan.get("subjects", []):
            total_tasks += 1
            if subj.get("status") == "completed":
                completed_tasks += 1
    
    if total_tasks == 0:
        total_tasks = 12
        completed_tasks = 8
    
    overall_progress = 0
    if user_plans:
        overall_progress = int(sum([p.get("progress", 0) for p in user_plans]) / len(user_plans))
    else:
        overall_progress = 72
    
    subject_names = []
    if st.session_state.get("subjects", []):
        subject_names = [s.get("topic", "") for s in st.session_state.subjects[:4]]
    if not subject_names:
        subject_names = ["Python", "AI", "DBMS", "English"]
    
    upcoming_exam = st.session_state.get("exams", [{"name": "Machine Learning", "days_left": 12, "date": "26 Jul 2026"}])[0]
    
    user_goals = st.session_state.get("goals", {}).get(username, [])
    active_goals = [g for g in user_goals if g.get("status") != "Completed"]
    goal_count = len(active_goals)
    goal_text = active_goals[0].get('title', 'Set your first goal!')[:25] if active_goals else '🎯 Set your first goal!'
    
    # Study Streak
    study_streak = st.session_state.get("study_streak", 12)
    
    # ===== Get profile picture =====
    profile_pic = get_profile_picture(username)
    
    # ===== FONT AWESOME CDN =====
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    """, unsafe_allow_html=True)
    
    # ============ PROFILE SECTION ============
    if profile_pic:
        avatar_html = f'<img src="{profile_pic}" alt="Profile" style="width:56px;height:56px;border-radius:50%;object-fit:cover;">'
    else:
        avatar_html = username[0].upper()
    
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;background:rgba(255,255,255,0.88);border-radius:16px;padding:16px 20px;margin-bottom:20px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.10);backdrop-filter:blur(12px);">
        <div style="width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#4f8dff,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:700;color:white;flex-shrink:0;overflow:hidden;border:2px solid rgba(255,255,255,0.5);">
            {avatar_html}
        </div>
        <div style="flex:1;">
            <h2 style="font-size:18px;font-weight:700;color:#183153;margin:0;">{username}</h2>
            <p style="font-size:14px;color:#4f8dff;font-weight:600;margin:2px 0 0 0;"><i class="fas fa-hand-peace"></i> Welcome back!</p>
        </div>
        <div style="background:#fef9e7;color:#f39c12;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:600;display:flex;align-items:center;gap:6px;">
            <i class="fas fa-fire"></i> {study_streak} days
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ============ QUICK STATS (4 Cards with Icons) ============
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px;">
        <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:14px 16px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.08);text-align:center;backdrop-filter:blur(12px);">
            <i class="fas fa-book" style="font-size:24px;color:#4f8dff;display:block;margin-bottom:4px;"></i>
            <div style="font-size:22px;font-weight:800;color:#183153;">{total_subjects if total_subjects > 0 else 4}</div>
            <div style="font-size:12px;color:#7b8797;font-weight:500;">Subjects</div>
        </div>
        <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:14px 16px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.08);text-align:center;backdrop-filter:blur(12px);">
            <i class="fas fa-tasks" style="font-size:24px;color:#4f8dff;display:block;margin-bottom:4px;"></i>
            <div style="font-size:22px;font-weight:800;color:#183153;">{completed_tasks}/{total_tasks}</div>
            <div style="font-size:12px;color:#7b8797;font-weight:500;">Tasks Done</div>
        </div>
        <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:14px 16px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.08);text-align:center;backdrop-filter:blur(12px);">
            <i class="fas fa-chart-line" style="font-size:24px;color:#4f8dff;display:block;margin-bottom:4px;"></i>
            <div style="font-size:22px;font-weight:800;color:#183153;">{overall_progress}%</div>
            <div style="font-size:12px;color:#7b8797;font-weight:500;">Progress</div>
        </div>
        <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:14px 16px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.08);text-align:center;backdrop-filter:blur(12px);">
            <i class="fas fa-flag-checkered" style="font-size:24px;color:#4f8dff;display:block;margin-bottom:4px;"></i>
            <div style="font-size:22px;font-weight:800;color:#183153;">{goal_count}</div>
            <div style="font-size:12px;color:#7b8797;font-weight:500;">Goals</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ============ MAIN TWO-COLUMN LAYOUT ============
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        # ----- TODAY'S SCHEDULE -----
        st.markdown('<div style="font-size:16px;font-weight:700;color:#183153;margin:16px 0 10px 0;"><i class="fas fa-calendar-day" style="color:#4f8dff;margin-right:8px;"></i> Today\'s Schedule</div>', unsafe_allow_html=True)
        
        schedule_items = []
        if user_plans:
            for plan in user_plans[:3]:
                for subj in plan.get("subjects", [])[:3]:
                    status = subj.get("status", "pending")
                    status_class = "status-completed" if status == "completed" else "status-inprogress" if status == "in_progress" else "status-pending"
                    status_text = "Completed" if status == "completed" else "In Progress" if status == "in_progress" else "Pending"
                    schedule_items.append({
                        "time": plan.get("start_time", "09:00AM"),
                        "task": subj.get("topic", "Unknown"),
                        "status": status_text,
                        "status_class": status_class
                    })
        
        if not schedule_items:
            schedule_items = [
                {"time": "09:00AM", "task": "Python Programming", "status": "Completed", "status_class": "status-completed"},
                {"time": "10:30AM", "task": "Functions and Modules", "status": "Completed", "status_class": "status-completed"},
                {"time": "11:00AM", "task": "Artificial Intelligence", "status": "In Progress", "status_class": "status-inprogress"},
                {"time": "12:30PM", "task": "Search Algorithms", "status": "Pending", "status_class": "status-pending"},
                {"time": "02:00PM", "task": "Database Systems", "status": "Pending", "status_class": "status-pending"},
                {"time": "03:30PM", "task": "Normalization", "status": "Pending", "status_class": "status-pending"},
            ]
        
        for item in schedule_items[:6]:
            st.markdown(f"""
            <div style="display:flex;align-items:center;padding:10px 14px;background:rgba(255,255,255,0.88);border-radius:10px;margin-bottom:6px;border-left:3px solid #4f8dff;box-shadow:0 2px 8px rgba(79,141,255,0.06);backdrop-filter:blur(12px);">
                <span style="font-weight:600;font-size:12px;color:#183153;min-width:65px;">{item['time']}</span>
                <span style="flex:1;font-size:13px;color:#183153;margin:0 10px;">{item['task']}</span>
                <span style="padding:2px 12px;border-radius:12px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.3px;background:{'#d5f5e3' if item['status']=='Completed' else '#fdebd0' if item['status']=='In Progress' else '#eaf2f8'};color:{'#27ae60' if item['status']=='Completed' else '#e67e22' if item['status']=='In Progress' else '#5b7a8a'};">{item['status']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # ----- RECENT TIMETABLES -----
        st.markdown('<div style="font-size:16px;font-weight:700;color:#183153;margin:16px 0 10px 0;"><i class="fas fa-clock-rotate-left" style="color:#4f8dff;margin-right:8px;"></i> Recent Timetables</div>', unsafe_allow_html=True)
        
        if user_plans:
            for plan in user_plans[-2:]:
                subjects_list = plan.get("subjects", [])
                subject_names_short = ", ".join([s.get("topic", "") for s in subjects_list[:3]])
                if len(subjects_list) > 3:
                    subject_names_short += f" +{len(subjects_list)-3} more"
                weeks = plan.get('weeks', 2)
                hours = plan.get('hours_per_day', 4)
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.88);padding:12px 14px;border-radius:10px;margin-bottom:6px;border-left:3px solid #8b5cf6;box-shadow:0 2px 8px rgba(79,141,255,0.06);backdrop-filter:blur(12px);">
                    <div style="font-weight:600;color:#183153;font-size:13px;"><i class="fas fa-book-open" style="color:#4f8dff;margin-right:8px;"></i> {subject_names_short}</div>
                    <div style="font-size:11px;color:#7b8797;margin-top:2px;"><i class="fas fa-clock"></i> {weeks} weeks • {hours}.0h/day</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📌 No timetables yet. Create one in Timetable!")
    
    with right_col:
        # ----- CALENDAR -----
        st.markdown('<div style="font-size:16px;font-weight:700;color:#183153;margin:0 0 10px 0;"><i class="fas fa-calendar-alt" style="color:#4f8dff;margin-right:8px;"></i> Calendar</div>', unsafe_allow_html=True)

        today = datetime.now()

        if 'calendar_month' not in st.session_state:
            st.session_state.calendar_month = today.month
        if 'calendar_year' not in st.session_state:
            st.session_state.calendar_year = today.year

        current_month = st.session_state.calendar_month
        current_year = st.session_state.calendar_year

        nav_cols = st.columns([1, 3, 1])
        with nav_cols[0]:
            if st.button("◀", key="prev_month"):
                if current_month == 1:
                    st.session_state.calendar_month = 12
                    st.session_state.calendar_year = current_year - 1
                else:
                    st.session_state.calendar_month = current_month - 1
                st.rerun()
        with nav_cols[1]:
            st.markdown(
                f"<div style='text-align:center;font-weight:700;color:#183153;font-size:14px;'>{calendar.month_name[current_month]} {current_year}</div>",
                unsafe_allow_html=True
            )
        with nav_cols[2]:
            if st.button("▶", key="next_month"):
                if current_month == 12:
                    st.session_state.calendar_month = 1
                    st.session_state.calendar_year = current_year + 1
                else:
                    st.session_state.calendar_month = current_month + 1
                st.rerun()

        cal = calendar.monthcalendar(current_year, current_month)

        exam_dates = set()
        for exam in st.session_state.get("exams", []):
            date_str = exam.get("date")
            if date_str:
                try:
                    exam_date = datetime.strptime(date_str, "%d %b %Y")
                    exam_dates.add((exam_date.year, exam_date.month, exam_date.day))
                except:
                    pass

        days_header = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        html = '<div style="border:1px solid rgba(255,255,255,0.3);border-radius:12px;padding:12px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">'
        html += '<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:2px;margin-top:6px;">'

        for d in days_header:
            is_weekend = d in ['Sun', 'Sat']
            html += f'<div style="text-align:center;font-size:12px;padding:4px 0;border-radius:6px;color:#183153;font-weight:700;font-size:10px;color:#7b8797;">{d}</div>'

        for week in cal:
            for day in week:
                if day == 0:
                    html += '<div style="text-align:center;font-size:12px;padding:4px 0;border-radius:6px;color:#b0b8c4;"></div>'
                else:
                    is_today = (day == today.day and current_month == today.month and current_year == today.year)
                    has_event = (current_year, current_month, day) in exam_dates
                    html += f'<div style="text-align:center;font-size:12px;padding:4px 0;border-radius:6px;color:#183153;{"background:#4f8dff;color:white;font-weight:700;" if is_today else ""}">{day}'
                    if has_event and not is_today:
                        html += '<div style="display:inline-block;width:4px;height:4px;background:#4f8dff;border-radius:50%;margin-top:1px;"></div>'
                    html += '</div>'

        html += '</div></div>'
        st.markdown(html, unsafe_allow_html=True)
        
        # ----- OVERALL PROGRESS -----
        st.markdown('<div style="font-size:16px;font-weight:700;color:#183153;margin:16px 0 10px 0;"><i class="fas fa-chart-simple" style="color:#4f8dff;margin-right:8px;"></i> Overall Progress</div>', unsafe_allow_html=True)
        
        subject_progress = {}
        if user_plans:
            for plan in user_plans:
                for subj in plan.get("subjects", []):
                    topic = subj.get("topic", "Unknown")
                    progress = subj.get("progress", 0)
                    if topic not in subject_progress:
                        subject_progress[topic] = []
                    subject_progress[topic].append(progress)
        
        subject_avg = {}
        for topic, progs in subject_progress.items():
            subject_avg[topic] = int(sum(progs) / len(progs)) if progs else 0
        
        if not subject_avg:
            subject_avg = {"Python": 80, "AI": 72, "Database Systems": 65, "English": 50}
        
        for name, pct in list(subject_avg.items())[:5]:
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;font-size:12px;color:#183153;font-weight:500;">
                    <span><i class="fas fa-circle" style="color:#4f8dff;font-size:8px;margin-right:6px;"></i>{name}</span>
                    <span style="font-weight:600;color:#4f8dff;">{pct}%</span>
                </div>
                <div style="width:100%;height:4px;background:#eef2f6;border-radius:10px;overflow:hidden;margin-top:3px;">
                    <div style="height:100%;background:linear-gradient(90deg,#4f8dff,#8b5cf6);border-radius:10px;transition:width 0.6s ease;width:{pct}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # ----- STUDY OVERVIEW -----
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:14px 16px;border:1px solid rgba(255,255,255,0.3);margin-top:12px;backdrop-filter:blur(12px);">
            <div style="font-weight:700;color:#183153;font-size:14px;margin-bottom:10px;">
                <i class="fas fa-chart-line" style="color:#4f8dff;"></i> Study Overview
            </div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;">
                <div style="text-align:center;">
                    <div style="font-size:18px;font-weight:800;color:#4f8dff;">{total_subjects if total_subjects > 0 else 6}</div>
                    <div style="font-size:10px;color:#7b8797;"><i class="fas fa-book"></i> Subjects</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:18px;font-weight:800;color:#00b894;">{len(user_plans)}</div>
                    <div style="font-size:10px;color:#7b8797;"><i class="fas fa-check-circle"></i> Plans</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:18px;font-weight:800;color:#6c5ce7;">{overall_progress}%</div>
                    <div style="font-size:10px;color:#7b8797;"><i class="fas fa-chart-pie"></i> Progress</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:18px;font-weight:800;color:#fdcb6e;">{goal_count}</div>
                    <div style="font-size:10px;color:#7b8797;"><i class="fas fa-flag"></i> Goals</div>
                </div>
            </div>
            <div style="text-align:center;margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.3);">
                <span style="font-size:12px;color:#27ae60;font-weight:600;">
                    <i class="fas fa-star" style="color:#fdcb6e;"></i> Keep it up! You're doing great.
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)