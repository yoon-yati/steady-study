# learning.py - Learning Dashboard (Font Awesome Icons)
import streamlit as st
from learning_subjects import LEARNING_SUBJECTS
from auth import save_learning_progress
from data_manager import save_plans_db, get_plans_for_user
from datetime import datetime

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

def show_learning_page():
    if "learning_progress" not in st.session_state:
        st.session_state["learning_progress"] = {}
    
    username = st.session_state.get("username", "User")
    
    if username not in st.session_state["learning_progress"]:
        st.session_state["learning_progress"][username] = {}
    
    user_progress = st.session_state["learning_progress"].get(username, {})
    
    # ===== Load user plans =====
    user_plans = get_plans_for_user(username)
    
    # ===== Calculate stats =====
    total_subjects = len(LEARNING_SUBJECTS)
    total_videos = 0
    completed_videos = 0
    for name, data in LEARNING_SUBJECTS.items():
        for level, videos in data.get("roadmap", {}).items():
            total_videos += len(videos)
        subject_progress = user_progress.get(name, {})
        completed_videos += len(subject_progress.get("completed", []))
    
    overall_progress = int((completed_videos / total_videos) * 100) if total_videos > 0 else 0
    
    # ===== Initialize view state =====
    if "learning_view_mode" not in st.session_state:
        st.session_state["learning_view_mode"] = "Grid"
    
    # ===== Get profile picture =====
    profile_pic = get_profile_picture(username)
    if profile_pic:
        avatar_html = f'<img src="{profile_pic}" alt="Profile">'
    else:
        avatar_html = username[0].upper()
    
    # ===== FONT AWESOME CDN =====
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    """, unsafe_allow_html=True)
    
    # ===== CSS =====
    st.markdown("""
    <style>
        * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
        
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
        }
        .welcome-box .avatar img {
            width: 100%;
            height: 100%;
            object-fit: cover;
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
        
        /* Stats Cards */
        .stats-grid {
            display: grid !important;
            grid-template-columns: repeat(4, 1fr) !important;
            gap: 12px !important;
            margin-bottom: 20px !important;
        }
        .stat-card {
            background: white !important;
            border-radius: 14px !important;
            padding: 16px !important;
            border: 1px solid #eef2f6 !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
            text-align: center !important;
        }
        .stat-card .stat-num { font-size: 24px; font-weight: 800; color: #183153; }
        .stat-card .stat-label { font-size: 12px; color: #7b8797; margin-top: 2px; }
        .stat-card .stat-icon { font-size: 20px; display: block; margin-bottom: 4px; color: #4f8dff; }
        
        /* Learning Cards */
        .learning-card {
            background: white;
            border-radius: 14px;
            padding: 16px;
            border: 1px solid #eef2f6;
            text-align: center;
            transition: all 0.3s ease;
            margin-bottom: 10px;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .learning-card:hover { 
            box-shadow: 0 4px 20px rgba(0,0,0,0.08); 
            transform: translateY(-4px);
            border-color: #4f8dff;
        }
        .learning-card .icon { font-size: 36px; }
        .learning-card .name { font-weight: 700; color: #183153; font-size: 14px; margin-top: 6px; }
        .learning-card .desc { font-size: 11px; color: #7b8797; }
        .learning-card .progress-text { font-size: 11px; font-weight: 600; color: #4f8dff; margin-top: 4px; }
        
        /* List View */
        .learning-list-item {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 12px 16px;
            background: white;
            border-radius: 10px;
            border: 1px solid #eef2f6;
            margin-bottom: 6px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .learning-list-item:hover {
            border-color: #4f8dff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }
        .learning-list-item .list-icon { font-size: 28px; }
        .learning-list-item .list-info { flex: 1; }
        .learning-list-item .list-info .list-name { font-weight: 700; color: #183153; font-size: 14px; }
        .learning-list-item .list-info .list-desc { font-size: 12px; color: #7b8797; }
        .learning-list-item .list-progress { font-size: 12px; font-weight: 600; color: #4f8dff; }
        
        .roadmap-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            background: #f8faff;
            border-radius: 10px;
            margin-bottom: 6px;
            border-left: 3px solid #4f8dff;
            transition: all 0.3s ease;
        }
        .roadmap-item:hover { background: #f0f4fe; }
        .roadmap-item.completed { border-left-color: #27ae60; background: #f0faf5; }
        .roadmap-item.completed .video-title { text-decoration: line-through; color: #7b8797; }
        .roadmap-item .video-title { flex: 1; color: #183153; text-decoration: none; font-size: 13px; }
        .roadmap-item .video-title:hover { color: #4f8dff; text-decoration: underline; }
        .roadmap-item .badge { background: #eef2f6; padding: 2px 12px; border-radius: 10px; font-size: 9px; font-weight: 600; color: #7b8797; }
        
        .custom-divider {
            border: none;
            border-top: 2px solid #eef2f6;
            margin: 16px 0;
        }
        
        .section-title {
            font-size: 16px;
            font-weight: 700;
            color: #183153;
            margin: 0 0 12px 0;
        }
        .section-title i { color: #4f8dff; margin-right: 8px; }
        
        /* Progress Ring */
        .progress-ring {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 14px;
            border: 1px solid #eef2f6;
        }
        .progress-ring .ring-circle {
            position: relative;
            width: 140px;
            height: 140px;
            margin: 0 auto;
        }
        .progress-ring .ring-circle svg {
            transform: rotate(-90deg);
        }
        .progress-ring .ring-circle .ring-bg {
            fill: none;
            stroke: #eef2f6;
            stroke-width: 10;
        }
        .progress-ring .ring-circle .ring-fill {
            fill: none;
            stroke: #4f8dff;
            stroke-width: 10;
            stroke-linecap: round;
            stroke-dasharray: 377;
            stroke-dashoffset: 377;
            transition: stroke-dashoffset 1s ease;
        }
        .progress-ring .ring-center {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }
        .progress-ring .ring-center .num {
            font-size: 32px;
            font-weight: 800;
            color: #183153;
        }
        .progress-ring .ring-center .label {
            font-size: 11px;
            color: #7b8797;
        }
        .progress-ring .ring-stats {
            display: flex;
            justify-content: center;
            gap: 24px;
            margin-top: 12px;
        }
        .progress-ring .ring-stats .stat-item {
            text-align: center;
        }
        .progress-ring .ring-stats .stat-item .num {
            font-weight: 700;
            color: #183153;
            font-size: 18px;
        }
        .progress-ring .ring-stats .stat-item .label {
            font-size: 11px;
            color: #7b8797;
        }
        .progress-ring .ring-footer {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #eef2f6;
            font-size: 13px;
            color: #27ae60;
            font-weight: 600;
        }
        
        /* Activity Item */
        .activity-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 14px;
            background: white;
            border-radius: 10px;
            border: 1px solid #eef2f6;
            margin-bottom: 6px;
        }
        .activity-item .act-icon { font-size: 18px; color: #4f8dff; }
        .activity-item .act-info { flex: 1; }
        .activity-item .act-info .act-title { font-weight: 600; color: #183153; font-size: 13px; }
        .activity-item .act-info .act-meta { font-size: 11px; color: #7b8797; }
        .activity-item .act-progress { font-weight: 700; color: #4f8dff; font-size: 14px; }
        
        .badge-green { background: #d5f5e3; color: #27ae60; padding: 2px 10px; border-radius: 10px; font-size: 10px; font-weight: 600; }
        .badge-orange { background: #fdebd0; color: #e67e22; padding: 2px 10px; border-radius: 10px; font-size: 10px; font-weight: 600; }
        .badge-gray { background: #eaf2f8; color: #5b7a8a; padding: 2px 10px; border-radius: 10px; font-size: 10px; font-weight: 600; }
        
        /* View Selector - Icon Buttons */
        .view-selector {
            display: flex;
            gap: 6px;
            align-items: center;
        }
        .view-selector .view-btn {
            background: white;
            border: 1px solid #eef2f6;
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 13px;
            color: #7b8797;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .view-selector .view-btn:hover {
            border-color: #4f8dff;
            color: #4f8dff;
        }
        .view-selector .view-btn.active {
            background: #f0f4fe;
            border-color: #4f8dff;
            color: #4f8dff;
        }
        .view-selector .view-btn i { margin-right: 4px; }
        
        .subject-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: repeat(2, 1fr) !important; }
            .main-header { flex-direction: column; align-items: stretch; }
            .header-left { flex-wrap: wrap; }
            .welcome-box { flex-wrap: wrap; }
            .welcome-box .date-badge { margin-left: auto; }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # ===== HEADER WITH PROFILE PICTURE =====
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
                    <div class="title"><i class="fas fa-graduation-cap"></i> Learning Dashboard</div>
                    <div class="subtitle">{greeting}, <span class="greeting">{username}</span>! Choose a subject to explore step-by-step learning roadmaps.</div>
                </div>
                <div class="date-badge">
                    <i class="fas fa-calendar-day"></i> {datetime.now().strftime('%B %d, %Y')}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== STATS CARDS =====
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-card">
            <i class="fas fa-book stat-icon"></i>
            <div class="stat-num">{total_subjects}</div>
            <div class="stat-label">Subjects</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-check-circle stat-icon"></i>
            <div class="stat-num">{completed_videos}</div>
            <div class="stat-label">Lessons Completed</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-chart-line stat-icon"></i>
            <div class="stat-num">{overall_progress}%</div>
            <div class="stat-label">Overall Progress</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-fire stat-icon"></i>
            <div class="stat-num">{st.session_state.get('study_streak', 5)}</div>
            <div class="stat-label">Day Streak</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== SUBJECT DETAIL VIEW =====
    if st.session_state.get("selected_learning_subject"):
        subject_name = st.session_state["selected_learning_subject"]
        subject_data = LEARNING_SUBJECTS.get(subject_name)
        
        if subject_data:
            subject_progress = user_progress.get(subject_name, {})
            completed_videos_subj = subject_progress.get("completed", [])
            
            total_videos_subj = 0
            roadmap = subject_data.get("roadmap", {})
            for level, videos in roadmap.items():
                total_videos_subj += len(videos)
            
            progress_pct = int((len(completed_videos_subj) / total_videos_subj) * 100) if total_videos_subj > 0 else 0
            
            st.markdown(f"""
            <div style='display:flex; align-items:center; gap:16px; margin:16px 0; padding:16px 20px; background:white; border-radius:14px; border:1px solid #eef2f6; box-shadow:0 2px 8px rgba(0,0,0,0.04);'>
                <span style='font-size:36px; color:#4f8dff;'>
                    <i class="fas {subject_data['icon']}"></i>
                </span>
                <div style='flex:1;'>
                    <h3 style='color:#183153; font-size:20px; margin:0;'>{subject_name}</h3>
                    <p style='color:#7b8797; font-size:13px; margin:2px 0 0 0;'>{subject_data['description']}</p>
                </div>
                <div style='text-align:center;'>
                    <div style='font-size:28px; font-weight:800; color:#4f8dff;'>{progress_pct}%</div>
                    <div style='font-size:11px; color:#7b8797;'>{len(completed_videos_subj)}/{total_videos_subj} videos</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='margin-bottom:16px;'>
                <div style='width:100%; height:8px; background:#eef2f6; border-radius:10px; overflow:hidden;'>
                    <div style='width:{progress_pct}%; height:100%; background:linear-gradient(90deg,#4f8dff,#6c5ce7); border-radius:10px;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
            
            levels = ["Beginner", "Intermediate", "Advanced"]
            
            for level in levels:
                if level in roadmap:
                    videos = roadmap[level]
                    level_icons = {"Beginner": "🌱", "Intermediate": "🌿", "Advanced": "🌳"}
                    st.markdown(f"### {level_icons.get(level, '📚')} {level}")
                    
                    for idx, video in enumerate(videos):
                        video_id = f"{subject_name}_{level}_{idx}"
                        is_completed = video_id in completed_videos_subj
                        
                        col1, col2, col3 = st.columns([5, 1, 1])
                        with col1:
                            st.markdown(f"""
                            <div class="roadmap-item {'completed' if is_completed else ''}">
                                <span style='font-size:14px;'>{'✅' if is_completed else '▶️'}</span>
                                <a href="{video['url']}" target="_blank" class="video-title"><i class="fas fa-play-circle" style="color:#4f8dff; margin-right:6px;"></i>{video['title']}</a>
                                <span class="badge"><i class="fas fa-video"></i></span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            if is_completed:
                                if st.button("↩️", key=f"undo_{video_id}", help="Undo completion"):
                                    if video_id in completed_videos_subj:
                                        completed_videos_subj.remove(video_id)
                                        if username not in st.session_state["learning_progress"]:
                                            st.session_state["learning_progress"][username] = {}
                                        if subject_name not in st.session_state["learning_progress"][username]:
                                            st.session_state["learning_progress"][username][subject_name] = {"completed": []}
                                        st.session_state["learning_progress"][username][subject_name]["completed"] = completed_videos_subj
                                        update_planner_progress(username, subject_name)
                                        st.rerun()
                            else:
                                if st.button("✅", key=f"complete_{video_id}", help="Mark as completed"):
                                    if video_id not in completed_videos_subj:
                                        completed_videos_subj.append(video_id)
                                        if username not in st.session_state["learning_progress"]:
                                            st.session_state["learning_progress"][username] = {}
                                        if subject_name not in st.session_state["learning_progress"][username]:
                                            st.session_state["learning_progress"][username][subject_name] = {"completed": []}
                                        st.session_state["learning_progress"][username][subject_name]["completed"] = completed_videos_subj
                                        update_planner_progress(username, subject_name)
                                        st.rerun()
                        
                        with col3:
                            if is_completed:
                                st.markdown("<span style='font-size:11px; color:#27ae60; font-weight:600;'><i class='fas fa-check-circle'></i> Done</span>", unsafe_allow_html=True)
                            else:
                                st.markdown("<span style='font-size:11px; color:#7b8797;'><i class='fas fa-clock'></i> Pending</span>", unsafe_allow_html=True)
            
            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
            if st.button("← Back to Subjects", use_container_width=True):
                st.session_state["selected_learning_subject"] = None
                st.rerun()
            return
    
    # ===== SUBJECT LIST WITH VIEW SELECTOR =====
    st.markdown("""
    <div class="subject-header">
        <div class="section-title" style="margin:0;">
            <i class="fas fa-book"></i> Available Subjects
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    
    if LEARNING_SUBJECTS:
        if st.session_state.get("learning_view_mode", "Grid") == "Grid":
            cols = st.columns(4)
            col_idx = 0
            
            for name, data in LEARNING_SUBJECTS.items():
                with cols[col_idx % 4]:
                    subject_progress = user_progress.get(name, {})
                    completed = len(subject_progress.get("completed", []))
                    total = 0
                    for level, videos in data.get("roadmap", {}).items():
                        total += len(videos)
                    progress_text = f"{total}videos"
                    
                    st.markdown(f"""
                    <div class="learning-card">
                        <div style="font-size:32px; color:#4f8dff;">
                            <i class="fas {data['icon']}"></i>
                        </div>
                        <div class="name">{name}</div>
                        <div class="desc">{data['description'][:35]}...</div>
                        <div class="progress-text"><i class="fas fa-play-circle"></i> {progress_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Study {name}", key=f"learn_grid_{name}", use_container_width=True):
                        st.session_state["selected_learning_subject"] = name
                        st.rerun()
                col_idx += 1
        else:
            # List View
            for name, data in LEARNING_SUBJECTS.items():
                subject_progress = user_progress.get(name, {})
                completed = len(subject_progress.get("completed", []))
                total = 0
                for level, videos in data.get("roadmap", {}).items():
                    total += len(videos)
                progress_text = f"{completed}/{total} videos"
                
                col_list1, col_list2 = st.columns([5, 1])
                with col_list1:
                    st.markdown(f"""
                    <div class="learning-list-item">
                        <span class="list-icon" style="font-size:28px; color:#4f8dff;">
                            <i class="fas {data['icon']}"></i>
                        </span>
                        <div class="list-info">
                            <div class="list-name">{name}</div>
                            <div class="list-desc">{data['description']}</div>
                        </div>
                        <span class="list-progress"><i class="fas fa-chart-line"></i> {progress_text}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_list2:
                    if st.button(f"Study", key=f"learn_list_{name}"):
                        st.session_state["selected_learning_subject"] = name
                        st.rerun()
    else:
        st.info("No subjects available. Go to Planner to add subjects!")
    
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    
    # ===== TWO COLUMN: Progress + Recent Activity =====
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-title"><i class="fas fa-chart-pie"></i> My Progress</div>', unsafe_allow_html=True)
        
        # Calculate circumference
        circumference = 2 * 3.14159 * 60  # r=60
        offset = circumference - (overall_progress / 100) * circumference
        
        st.markdown(f"""
        <div class="progress-ring">
            <div class="ring-circle">
                <svg width="140" height="140" viewBox="0 0 140 140">
                    <circle class="ring-bg" cx="70" cy="70" r="60"/>
                    <circle class="ring-fill" cx="70" cy="70" r="60" 
                        style="stroke-dasharray:{circumference}; stroke-dashoffset:{offset};"/>
                </svg>
                <div class="ring-center">
                    <div class="num">{overall_progress}%</div>
                    <div class="label">Overall Progress</div>
                </div>
            </div>
            <div class="ring-stats">
                <div class="stat-item">
                    <div class="num">{completed_videos}</div>
                    <div class="label"><i class="fas fa-check-circle" style="color:#27ae60;"></i> Completed</div>
                </div>
                <div class="stat-item">
                    <div class="num">{total_videos - completed_videos}</div>
                    <div class="label"><i class="fas fa-clock" style="color:#f39c12;"></i> Remaining</div>
                </div>
            </div>
            <div class="ring-footer">
                <i class="fas fa-star" style="color:#fdcb6e;"></i> Keep it up! You're doing great!
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-title"><i class="fas fa-clock"></i> Recent Learning Activity</div>', unsafe_allow_html=True)
        
        # Get recent activity from user_plans
        activities = []
        for plan in user_plans[:3]:
            for subj in plan.get("subjects", [])[:2]:
                topic = subj.get("topic")
                progress = subj.get("progress", 0)
                status = subj.get("status", "pending")
                if topic in LEARNING_SUBJECTS:
                    status_text = "Completed" if status == "completed" else "In Progress" if status == "in_progress" else "Not Started"
                    status_class = "badge-green" if status == "completed" else "badge-orange" if status == "in_progress" else "badge-gray"
                    activities.append({
                        "title": topic,
                        "progress": progress,
                        "status": status_text,
                        "status_class": status_class,
                        "time": "2h ago" if len(activities) == 0 else "Yesterday" if len(activities) == 1 else "2 days ago"
                    })
        
        if not activities:
            activities = [
                {"title": "Data Structures - Arrays and Linked Lists", "progress": 70, "status": "In Progress", "status_class": "badge-orange", "time": "2h ago"},
                {"title": "Python - Loops and Functions", "progress": 100, "status": "Completed", "status_class": "badge-green", "time": "Yesterday"},
                {"title": "JavaScript - Variables and Data Types", "progress": 60, "status": "In Progress", "status_class": "badge-orange", "time": "2 days ago"}
            ]
        
        for act in activities[:3]:
            st.markdown(f"""
            <div class="activity-item">
                <i class="fas fa-book-open act-icon"></i>
                <div class="act-info">
                    <div class="act-title">{act['title']}</div>
                    <div class="act-meta"><span class="{act['status_class']}">{act['status']}</span> • {act['time']}</div>
                </div>
                <div class="act-progress">{act['progress']}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    
    # ===== MY STUDY PLAN (Learning Subjects) =====
    st.markdown('<div class="section-title"><i class="fas fa-clipboard-list"></i> My Study Plan</div>', unsafe_allow_html=True)
    
    # Get all learning subjects from planner
    learning_subjects_in_planner = []
    for plan in user_plans:
        for subj in plan.get("subjects", []):
            topic = subj.get("topic")
            if topic in LEARNING_SUBJECTS:
                learning_subjects_in_planner.append({
                    "topic": topic,
                    "status": subj.get("status", "pending"),
                    "progress": subj.get("progress", 0),
                    "plan_id": plan.get("id"),
                    "plan_title": plan.get("title")
                })
    
    if learning_subjects_in_planner:
        cols = st.columns(3)
        for idx, item in enumerate(learning_subjects_in_planner[:6]):
            with cols[idx % 3]:
                topic = item["topic"]
                progress = item["progress"]
                status = item["status"]
                
                status_icon = "✅" if status == "completed" else "🔄" if status == "in_progress" else "⏳"
                status_color = "#27ae60" if status == "completed" else "#f39c12" if status == "in_progress" else "#7b8797"
                
                st.markdown(f"""
                <div style="background:white; border-radius:10px; padding:12px; border:1px solid #eef2f6; margin-bottom:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:600; color:#183153; font-size:13px;">{status_icon} {topic}</span>
                        <span style="font-size:12px; font-weight:700; color:{status_color};">{progress}%</span>
                    </div>
                    <div style="width:100%; height:4px; background:#eef2f6; border-radius:10px; overflow:hidden; margin-top:4px;">
                        <div style="width:{progress}%; height:100%; background:{status_color}; border-radius:10px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col_del1, col_del2 = st.columns([4, 1])
                with col_del2:
                    if st.button("🗑️", key=f"del_learning_subj_{idx}_{topic}", help="Remove from study plan"):
                        if username in st.session_state["plans_db"]:
                            plans = st.session_state["plans_db"][username]
                            for plan in plans:
                                if plan.get("id") == item["plan_id"]:
                                    subjects = plan.get("subjects", [])
                                    for i, subj in enumerate(subjects):
                                        if subj.get("topic") == topic:
                                            del subjects[i]
                                            break
                                    if not subjects:
                                        plans.remove(plan)
                                    break
                            save_plans_db(st.session_state["plans_db"])
                            st.success(f"✅ {topic} removed from study plan!")
                            st.rerun()
    else:
        st.info("No learning subjects in your study plan. Add subjects from Planner!")

# ===== UPDATE PLANNER (FUNCTION) =====
def update_planner_progress(username, subject_name):
    """Update planner progress based on learning progress"""
    from data_manager import save_plans_db
    
    user_progress = st.session_state["learning_progress"].get(username, {})
    subject_progress = user_progress.get(subject_name, {})
    completed_videos = subject_progress.get("completed", [])
    
    # Get total videos for this subject
    subject_data = LEARNING_SUBJECTS.get(subject_name, {})
    total_videos = 0
    for level, videos in subject_data.get("roadmap", {}).items():
        total_videos += len(videos)
    
    if total_videos == 0:
        return
    
    # Calculate progress percentage
    progress_pct = int((len(completed_videos) / total_videos) * 100)
    
    # Update planner
    user_plans = st.session_state.get("plans_db", {}).get(username, [])
    updated = False
    
    for plan in user_plans:
        for subj in plan.get("subjects", []):
            if subj.get("topic") == subject_name:
                # Update progress
                subj["progress"] = progress_pct
                if progress_pct == 100:
                    subj["status"] = "completed"
                elif progress_pct > 0:
                    subj["status"] = "in_progress"
                updated = True
                
                # Update overall plan progress
                plan_subjects = plan.get("subjects", [])
                if plan_subjects:
                    total_progress = sum([s.get("progress", 0) for s in plan_subjects])
                    plan["progress"] = int(total_progress / len(plan_subjects))
                    if plan["progress"] == 100:
                        plan["status"] = "completed"
                    elif plan["progress"] > 0:
                        plan["status"] = "in_progress"
    
    # Save updated plans
    if updated:
        save_plans_db(st.session_state["plans_db"])