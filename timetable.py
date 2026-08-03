# timetable.py - Fixed Version (CSS removed, uses app.py gradient)
import streamlit as st
import time
import base64
import datetime
from utils import (
    parse_time_to_minutes, ai_generate_timetable, generate_timetable_pdf,
    REPORTLAB_AVAILABLE, AI_AVAILABLE, ai_get_study_tips, ai_validate_meaning
)
from data_manager import save_plan_for_user, get_plans_for_user

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


def show_timetable_page():
    username = st.session_state["username"]

    # ===== FONT AWESOME CDN =====
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    """, unsafe_allow_html=True)

    # ===== Get profile picture =====
    profile_pic = get_profile_picture(username)
    if profile_pic:
        avatar_html = f'<img src="{profile_pic}" alt="Profile" style="width:44px;height:44px;border-radius:50%;object-fit:cover;">'
    else:
        avatar_html = username[0].upper()

    # ===== MAIN HEADER WITH WELCOME BOX =====
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:12px;">
        <div style="display:flex;align-items:center;gap:16px;flex:1;">
            <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:12px 20px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.10);display:flex;align-items:center;gap:12px;flex:1;backdrop-filter:blur(12px);">
                <div style="width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#4f8dff,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700;color:white;flex-shrink:0;overflow:hidden;border:2px solid rgba(255,255,255,0.5);">
                    {avatar_html}
                </div>
                <div style="flex:1;">
                    <div style="font-size:18px;font-weight:700;color:#183153;margin:0;">
                        <i class="fas fa-calendar-alt" style="color:#4f8dff;margin-right:8px;"></i> Timetable
                    </div>
                    <div style="font-size:13px;color:#5a6a7e;margin:2px 0 0 0;">
                        {greeting}, <span style="color:#4f8dff;font-weight:600;">{username}</span>! Create your personalized study schedule.
                    </div>
                </div>
                <div style="background:rgba(248,250,255,0.7);padding:6px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.3);font-size:12px;color:#5a6a7e;white-space:nowrap;">
                    <i class="fas fa-calendar-day" style="color:#4f8dff;margin-right:6px;"></i> {datetime.datetime.now().strftime('%B %d, %Y')}
                </div>
            </div>
        </div>
    </div>
    <hr style="border:none;border-top:2px solid rgba(255,255,255,0.3);margin:16px 0;">
    """, unsafe_allow_html=True)

    # ---- SETTINGS ----
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:16px 20px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.08);margin-bottom:16px;backdrop-filter:blur(12px);">
        <div style="font-size:15px;font-weight:700;color:#183153;margin-bottom:14px;display:flex;align-items:center;gap:10px;">
            <i class="fas fa-sliders-h" style="color:#4f8dff;font-size:18px;"></i> Timetable Settings
            <span style="background:rgba(240,244,254,0.8);color:#4f8dff;font-size:10px;padding:2px 14px;border-radius:20px;font-weight:600;margin-left:auto;">
                <i class="fas fa-cog"></i> Configure
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        study_hours_options = ["0:30", "1:00", "1:30", "2:00", "2:30", "3:00", "3:30", "4:00", "4:30", "5:00", "5:30",
                               "6:00", "6:30", "7:00", "7:30", "8:00"]
        current_hours = st.session_state.get("study_hours", "4:00")
        if current_hours not in study_hours_options:
            current_hours = "4:00"
        study_hours = st.selectbox("⏰ Study Hours", options=study_hours_options, index=study_hours_options.index(current_hours),
                                   key="study_hours_select")
        st.session_state["study_hours"] = study_hours
    with col2:
        start_time_options = []
        for h in range(24):
            for m in [0, 30]:
                start_time_options.append(f"{h:02d}:{m:02d}")
        current_start = st.session_state.get("start_time", "09:00")
        if current_start not in start_time_options:
            current_start = "09:00"
        start_time = st.selectbox("▶️ Start Time", options=start_time_options, index=start_time_options.index(current_start),
                                  key="start_time_select")
        st.session_state["start_time"] = start_time
    with col3:
        weeks = st.selectbox("📅 Weeks", options=list(range(1, 13)), index=1)

    st.markdown('<hr style="border:none;border-top:2px solid rgba(255,255,255,0.3);margin:16px 0;">', unsafe_allow_html=True)

    # ---- SUBJECTS ----
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:16px 20px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.08);margin-bottom:16px;backdrop-filter:blur(12px);">
        <div style="font-size:15px;font-weight:700;color:#183153;margin-bottom:14px;display:flex;align-items:center;gap:10px;">
            <i class="fas fa-book" style="color:#4f8dff;font-size:18px;"></i> Subjects
            <span style="background:rgba(240,244,254,0.8);color:#4f8dff;font-size:10px;padding:2px 14px;border-radius:20px;font-weight:600;margin-left:auto;">
                <i class="fas fa-plus-circle"></i> Add Your Topics
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    subjects_to_remove = []

    if "subjects" not in st.session_state:
        st.session_state.subjects = []

    for idx, subject in enumerate(st.session_state.subjects):
        with st.container():
            cols = st.columns([2, 3, 1.5, 0.3])
            with cols[0]:
                topic = st.text_input("Subject", value=subject.get("topic", ""), key=f"topic_{idx}", placeholder="e.g. Python")
                if topic.strip():
                    st.session_state.subjects[idx]["topic"] = topic
            with cols[1]:
                courses_input = st.text_input("Topics", value=", ".join(subject.get("courses", [])) if subject.get("courses") else "", key=f"courses_{idx}", placeholder="Lecture 1, Chapter 2")
                if courses_input.strip():
                    st.session_state.subjects[idx]["courses"] = [c.strip() for c in courses_input.split(",") if c.strip()]
                else:
                    st.session_state.subjects[idx]["courses"] = []
            with cols[2]:
                current_skill = subject.get("skill", "beginner")
                if current_skill not in ["beginner", "intermediate", "advanced"]:
                    current_skill = "beginner"
                skill = st.selectbox("Skill", ["beginner", "intermediate", "advanced"],
                                     index=["beginner", "intermediate", "advanced"].index(current_skill),
                                     key=f"skill_{idx}")
                st.session_state.subjects[idx]["skill"] = skill
            with cols[3]:
                if st.button("✕", key=f"remove_{idx}", help="Remove this subject"):
                    subjects_to_remove.append(idx)

    for idx in sorted(subjects_to_remove, reverse=True):
        st.session_state.subjects.pop(idx)
        st.rerun()

    # Add Subject button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("➕ Add Subject", use_container_width=True, key="add_subject_btn"):
            st.session_state.subjects.append({"topic": "", "skill": "beginner", "courses": []})
            st.rerun()

    st.markdown('<hr style="border:none;border-top:2px solid rgba(255,255,255,0.3);margin:16px 0;">', unsafe_allow_html=True)

    # ---- GENERATE BUTTON ----
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate Timetable", use_container_width=True, key="generate_btn"):
            valid_subjects = [s for s in st.session_state.subjects if s.get("topic", "").strip()]
            if not valid_subjects:
                st.error("⚠️ Please add at least one valid subject!")
            else:
                hours_float = parse_time_to_minutes(st.session_state["study_hours"]) / 60
                with st.spinner("🤖 AI is generating your personalized timetable..."):
                    timetable_data = ai_generate_timetable(valid_subjects, weeks, hours_float,
                                                           st.session_state["start_time"])
                    save_plan_for_user(username, {
                        "subjects": valid_subjects,
                        "timetable": timetable_data,
                        "generated_at": time.ctime(),
                        "weeks": weeks,
                        "hours_per_day": hours_float,
                        "start_time": st.session_state["start_time"],
                        "ai_generated": AI_AVAILABLE
                    })
                    st.success(f"✅ Timetable generated for {len(valid_subjects)} subjects!")
                    st.rerun()

    st.markdown('<hr style="border:none;border-top:2px solid rgba(255,255,255,0.3);margin:16px 0;">', unsafe_allow_html=True)

    # ================================================================
    # ===== DISPLAY TIMETABLES WITH TOTAL HOURS CALCULATION =====
    # ================================================================
    user_plans = get_plans_for_user(username)

    if user_plans:
        latest_plan = user_plans[-1]
        subjects = latest_plan.get("subjects", [])
        timetable_data = latest_plan.get("timetable", {})
        weeks = latest_plan.get("weeks", 2)
        hours_per_day = latest_plan.get("hours_per_day", 4)
        start_time = latest_plan.get("start_time", "09:00")

        # ===== TOTAL HOURS CALCULATION =====
        total_hours = 0
        total_sessions = 0
        total_days = 0

        if timetable_data.get("weekly_schedule"):
            for week in timetable_data["weekly_schedule"]:
                for day in week.get("days", []):
                    total_days += 1
                    slots = day.get("slots", [])
                    total_sessions += len(slots)
                    
                    for slot in slots:
                        dur = slot.get("duration", "")
                        
                        if dur:
                            try:
                                if "h" in dur:
                                    h_str = dur.replace("h", "").strip()
                                    if h_str:
                                        hours = float(h_str)
                                        total_hours += hours
                                elif "min" in dur or "m" in dur:
                                    min_str = dur.replace("min", "").replace("m", "").strip()
                                    if min_str:
                                        minutes = float(min_str)
                                        total_hours += minutes / 60
                                else:
                                    try:
                                        hours = float(dur)
                                        total_hours += hours
                                    except:
                                        pass
                            except:
                                pass
                        
                        if not dur:
                            start = slot.get("start", "")
                            end = slot.get("end", "")
                            if start and end:
                                try:
                                    try:
                                        start_dt = datetime.datetime.strptime(start.strip(), "%I:%M %p")
                                        end_dt = datetime.datetime.strptime(end.strip(), "%I:%M %p")
                                    except:
                                        start_dt = datetime.datetime.strptime(start.strip(), "%H:%M")
                                        end_dt = datetime.datetime.strptime(end.strip(), "%H:%M")
                                    
                                    hours = (end_dt - start_dt).seconds / 3600
                                    if hours < 0:
                                        hours += 24
                                    total_hours += hours
                                except:
                                    pass

        total_hours = round(total_hours, 1)

        # Stats
        st.markdown(f"""
        <div style="display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 16px 0;">
            <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:14px 16px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.08);text-align:center;flex:1;min-width:80px;backdrop-filter:blur(12px);">
                <div style="font-size:22px;font-weight:800;color:#183153;"><i class="fas fa-hourglass-half" style="font-size:18px;color:#4f8dff;margin-right:4px;"></i>{total_hours}h</div>
                <div style="font-size:11px;color:#7b8797;font-weight:500;margin-top:2px;">Total Hours</div>
            </div>
            <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:14px 16px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.08);text-align:center;flex:1;min-width:80px;backdrop-filter:blur(12px);">
                <div style="font-size:22px;font-weight:800;color:#183153;"><i class="fas fa-book" style="font-size:18px;color:#4f8dff;margin-right:4px;"></i>{len(subjects)}</div>
                <div style="font-size:11px;color:#7b8797;font-weight:500;margin-top:2px;">Subjects</div>
            </div>
            <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:14px 16px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.08);text-align:center;flex:1;min-width:80px;backdrop-filter:blur(12px);">
                <div style="font-size:22px;font-weight:800;color:#183153;"><i class="fas fa-tasks" style="font-size:18px;color:#4f8dff;margin-right:4px;"></i>{total_sessions}</div>
                <div style="font-size:11px;color:#7b8797;font-weight:500;margin-top:2px;">Sessions</div>
            </div>
            <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:14px 16px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.08);text-align:center;flex:1;min-width:80px;backdrop-filter:blur(12px);">
                <div style="font-size:22px;font-weight:800;color:#183153;"><i class="fas fa-calendar-week" style="font-size:18px;color:#4f8dff;margin-right:4px;"></i>{weeks}</div>
                <div style="font-size:11px;color:#7b8797;font-weight:500;margin-top:2px;">Weeks</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Subject tags
        subject_tags = ""
        for s in subjects:
            topic = s.get("topic", "Unknown")
            skill = s.get("skill", "beginner")
            skill_emoji = "🌱" if skill == "beginner" else "🌿" if skill == "intermediate" else "🌟"
            subject_tags += f'<span style="background:rgba(248,250,255,0.8);padding:4px 14px;border-radius:20px;font-size:12px;font-weight:500;color:#183153;border:1px solid rgba(255,255,255,0.3);"><i class="fas fa-book" style="margin-right:6px;color:#4f8dff;"></i>{topic} <span style="font-size:10px;color:#4f8dff;font-weight:600;">{skill_emoji} {skill}</span></span>'

        st.markdown(f"""
        <div style="margin: 6px 0 14px 0;">
            <div style="display:flex;flex-wrap:wrap;gap:6px;margin:6px 0;">{subject_tags}</div>
            <div style="font-size:12px;color:#7b8797;margin-top:4px;">
                <i class="fas fa-clock"></i> {hours_per_day}h/day &nbsp;·&nbsp; <i class="fas fa-play"></i> Starts at {start_time} &nbsp;·&nbsp; <i class="fas fa-calendar-alt"></i> {total_days} days
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr style="border:none;border-top:2px solid rgba(255,255,255,0.3);margin:16px 0;">', unsafe_allow_html=True)

        # Weekly Timetables
        if timetable_data.get("weekly_schedule"):
            seen_weeks = set()
            unique_weeks = []

            for week in timetable_data["weekly_schedule"]:
                week_num = week.get('week', 0)
                if week_num not in seen_weeks:
                    seen_weeks.add(week_num)
                    unique_weeks.append(week)

            for week in unique_weeks:
                week_num = week.get('week', 0)

                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.88);padding:12px 20px;border-radius:12px;margin:16px 0 12px 0;display:flex;align-items:center;gap:12px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">
                    <span style="background:rgba(240,244,254,0.8);color:#4f8dff;padding:2px 14px;border-radius:20px;font-size:12px;font-weight:600;"><i class="fas fa-calendar-week"></i> Week</span>
                    <h3 style="font-size:16px;font-weight:700;color:#183153;margin:0;"><i class="fas fa-flag" style="color:#4f8dff;margin-right:8px;"></i> {week_num}</h3>
                </div>
                """, unsafe_allow_html=True)

                all_time_slots = []
                for day in week.get("days", []):
                    for slot in day.get("slots", []):
                        time_range = f"{slot.get('start', '')} - {slot.get('end', '')}"
                        if time_range not in all_time_slots and slot.get('start') and slot.get('end'):
                            all_time_slots.append(time_range)

                def parse_time(t):
                    try:
                        return datetime.datetime.strptime(t.split(" - ")[0].strip(), "%I:%M %p")
                    except:
                        try:
                            return datetime.datetime.strptime(t.split(" - ")[0].strip(), "%H:%M")
                        except:
                            return datetime.datetime.strptime("12:00 AM", "%I:%M %p")

                all_time_slots.sort(key=parse_time)

                html = f'''
                <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:16px;border:1px solid rgba(255,255,255,0.3);box-shadow:0 4px 16px rgba(79,141,255,0.08);overflow-x:auto;margin:12px 0 20px 0;backdrop-filter:blur(12px);">
                <table style="width:100%;border-collapse:collapse;font-size:13px;min-width:600px;">
                    <thead>
                        <tr>
                            <th style="background:rgba(240,244,254,0.6);padding:12px 10px;font-weight:700;color:#183153;border:none;text-align:center;font-size:12px;letter-spacing:0.5px;text-transform:uppercase;border-bottom:2px solid rgba(255,255,255,0.3);">
                                <i class="fas fa-clock" style="margin-right:6px;color:#4f8dff;"></i> TIME
                            </th>
                '''

                days = week.get("days", [])
                for day in days:
                    day_name = day.get("day", "---")
                    if len(day_name) > 5:
                        day_name = day_name[:3]
                    html += f'<th style="background:rgba(240,244,254,0.6);padding:12px 10px;font-weight:700;color:#183153;border:none;text-align:center;font-size:12px;letter-spacing:0.5px;text-transform:uppercase;border-bottom:2px solid rgba(255,255,255,0.3);"><i class="fas fa-calendar-day" style="margin-right:6px;color:#4f8dff;"></i> {day_name.upper()}</th>'
                html += '</tr></thead><tbody>'

                subject_colors = {}
                color_index = 0
                color_classes = ['#4f8dff', '#6c5ce7', '#00b894', '#fdcb6e']

                for time_slot in all_time_slots:
                    html += f'<tr><td style="padding:10px 8px;border-bottom:1px solid rgba(255,255,255,0.3);text-align:center;font-size:12px;font-weight:700;color:#4f8dff;font-size:11px;min-width:80px;text-align:left;background:rgba(248,250,255,0.4);padding-left:12px;border-radius:8px 0 0 8px;"><i class="fas fa-clock" style="margin-right:4px;"></i> {time_slot}</td>'
                    for day in days:
                        matching_slots = [s for s in day.get("slots", []) if
                                          f"{s.get('start', '')} - {s.get('end', '')}" == time_slot]
                        if matching_slots:
                            slot = matching_slots[0]
                            subject = slot.get("subject", "")

                            if subject not in subject_colors:
                                subject_colors[subject] = color_classes[color_index % len(color_classes)]
                                color_index += 1

                            subject_short = subject[:20] if subject else "Study"
                            focus_short = slot.get("focus", "")[:20] if slot.get("focus") else "Focus"
                            color = subject_colors.get(subject, '#4f8dff')

                            html += f'''
                            <td style="padding:10px 8px;border-bottom:1px solid rgba(255,255,255,0.3);text-align:center;font-size:12px;border-left:3px solid {color};">
                                <div style="font-weight:700;color:#183153;font-size:13px;padding:4px 2px;"><i class="fas fa-book-open" style="color:#4f8dff;margin-right:4px;"></i> {subject_short}</div>
                                <div style="font-size:10px;color:#7b8797;padding:2px 2px;font-weight:400;"><i class="fas fa-bullseye" style="margin-right:4px;"></i> {focus_short}</div>
                            </td>
                            '''
                        else:
                            html += '<td style="padding:10px 8px;border-bottom:1px solid rgba(255,255,255,0.3);text-align:center;font-size:12px;color:#b0b8c4;font-style:italic;font-size:12px;"><i class="fas fa-coffee" style="margin-right:4px;"></i> Free</td>'
                    html += '</tr>'

                html += '</tbody></table></div>'
                st.components.v1.html(html, height=480, scrolling=True)

                if week.get("note"):
                    st.caption(f"📌 {week['note']}")

                st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:24px 28px;border:1px solid rgba(255,255,255,0.3);text-align:center;color:#7b8797;box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">
                <span style="font-size:40px;display:block;margin-bottom:8px;"><i class="fas fa-file-alt"></i></span>
                <p style="margin:0;font-weight:500;">No timetable data available.</p>
            </div>
            """, unsafe_allow_html=True)

        # PDF DOWNLOAD BUTTON
        if timetable_data.get("weekly_schedule") and REPORTLAB_AVAILABLE:
            try:
                pdf_bytes = generate_timetable_pdf(username, timetable_data, subjects)
                b64 = base64.b64encode(pdf_bytes).decode()

                download_button_html = f'''
                <div style="display:flex;justify-content:center;margin:16px 0 8px 0;">
                    <a href="data:application/pdf;base64,{b64}" download="timetable_{username}.pdf" style="text-decoration: none;">
                        <button style="background:linear-gradient(90deg,#4f8dff,#6c5ce7);color:white;border:none;padding:12px 32px;border-radius:12px;font-weight:700;font-size:14px;transition:all 0.3s ease;box-shadow:0 4px 16px rgba(79,141,255,0.30);cursor:pointer;display:inline-flex;align-items:center;gap:10px;">
                            <i class="fas fa-file-pdf" style="font-size:18px;"></i>
                            <span>Download PDF</span>
                            <i class="fas fa-download" style="font-size:18px;"></i>
                        </button>
                    </a>
                </div>
                '''
                st.markdown(download_button_html, unsafe_allow_html=True)

            except Exception as e:
                st.warning("⚠️ PDF generation failed. Please check if reportlab is installed.")
        elif not REPORTLAB_AVAILABLE:
            st.info("📌 PDF download requires reportlab. Install with: pip install reportlab")

    else:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.88);border-radius:14px;padding:24px 28px;border:1px solid rgba(255,255,255,0.3);text-align:center;color:#7b8797;box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">
            <span style="font-size:40px;display:block;margin-bottom:8px;"><i class="fas fa-plus-circle"></i></span>
            <p style="margin:0;font-weight:500;">Add your subjects and generate a timetable to get started!</p>
        </div>
        """, unsafe_allow_html=True)