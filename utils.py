# utils.py - Helper Functions (Fixed Timetable Generation)
import re
import hashlib
import time
import json
import os
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

import streamlit as st

# ---------- PDF Support ----------
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# ---------- Groq AI Setup ----------
try:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    if GROQ_API_KEY:
        import groq

        groq_client = groq.Client(api_key=GROQ_API_KEY)
        AI_AVAILABLE = True
    else:
        AI_AVAILABLE = False
except Exception:
    AI_AVAILABLE = False

# ---------- Domain Modules ----------
DOMAIN_MODULES = {
    "programming": [
        "Variables & Data Types", "Control Flow", "Functions",
        "OOP Concepts", "Inheritance", "Polymorphism",
        "Data Structures", "Algorithms", "Complexity",
        "Debugging", "Testing", "Version Control",
        "Frameworks", "Libraries", "APIs",
        "System Design", "Architecture", "Deployment"
    ],
    "language": [
        "Alphabet & Pronunciation", "Basic Vocabulary", "Greetings",
        "Grammar Rules", "Sentence Structure", "Tenses",
        "Reading Comprehension", "Writing Skills", "Listening",
        "Speaking Practice", "Conversation", "Idioms",
        "Advanced Grammar", "Literature", "Cultural Context",
        "Fluency Practice", "Debate", "Presentation"
    ],
    "science": [
        "Scientific Method", "Experiments", "Data Collection",
        "Physics: Mechanics", "Thermodynamics", "Waves",
        "Chemistry: Atoms", "Reactions", "Periodic Table",
        "Biology: Cells", "Genetics", "Ecology",
        "Earth Science", "Astronomy", "Geology",
        "Advanced Topics", "Research", "Innovation"
    ],
    "math": [
        "Arithmetic", "Algebra", "Equations",
        "Geometry", "Trigonometry", "Vectors",
        "Calculus", "Differentiation", "Integration",
        "Statistics", "Probability", "Data Analysis",
        "Linear Algebra", "Matrices", "Eigenvalues",
        "Advanced Math", "Proofs", "Theorems"
    ],
    "history": [
        "Ancient Civilizations", "Timeline", "Key Events",
        "Medieval Period", "Renaissance", "Exploration",
        "Modern History", "Wars", "Revolutions",
        "Cultural History", "Art", "Philosophy",
        "Political History", "Governance", "Diplomacy",
        "Historiography", "Research", "Analysis"
    ],
    "default": [
        "Introduction", "Core Concepts", "Fundamentals",
        "Intermediate Topics", "Applications", "Practice",
        "Advanced Concepts", "Specialization", "Research",
        "Projects", "Case Studies", "Real-world Examples",
        "Review", "Assessment", "Feedback",
        "Expert Level", "Innovation", "Future Trends"
    ]
}


# ---------- Helper Functions ----------
def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def parse_time_to_minutes(time_str: str) -> int:
    try:
        parts = time_str.split(":")
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        return hours * 60 + minutes
    except:
        return 240


def format_time_12hr(dt: datetime) -> str:
    hour = dt.hour % 12
    if hour == 0:
        hour = 12
    minute = dt.minute
    am_pm = "AM" if dt.hour < 12 else "PM"
    return f"{hour}:{minute:02d} {am_pm}"


def format_duration(minutes: int) -> str:
    minutes = int(minutes)
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if remaining_minutes == 0:
        return f"{hours} hr"
    return f"{hours} hr {remaining_minutes} min"


def detect_domain(tokens: List[str]) -> str:
    tset = set(tokens)
    if any(x in tset for x in
           ("java", "python", "c++", "javascript", "programming", "code", "algorithm", "data", "structure", "oop")):
        return "programming"
    if any(x in tset for x in
           ("english", "myanmar", "japanese", "korean", "chinese", "language", "grammar", "vocabulary", "ielts",
            "toefl")):
        return "language"
    if any(x in tset for x in ("physics", "chemistry", "biology", "science", "experiment", "research")):
        return "science"
    if any(x in tset for x in ("math", "calculus", "algebra", "geometry", "statistics", "mathematics")):
        return "math"
    if any(x in tset for x in ("history", "ancient", "modern", "civilization", "war")):
        return "history"
    return "default"


# ---------- AI Validation ----------
def ai_validate_meaning(text: str, text_type: str = "subject") -> Tuple[str, bool]:
    cache_key = f"{text_type}_{text.strip().lower()}"
    if cache_key in st.session_state.get("validation_cache", {}):
        return st.session_state["validation_cache"][cache_key]

    if not AI_AVAILABLE:
        if re.search(r'[a-zA-Z]', text) and len(text) >= 2:
            result = (text, True)
            st.session_state["validation_cache"][cache_key] = result
            return result
        result = (text, False)
        st.session_state["validation_cache"][cache_key] = result
        return result

    if not re.search(r'[a-zA-Z]', text) or len(text) < 2:
        result = (text, False)
        st.session_state["validation_cache"][cache_key] = result
        return result

    text_clean = text.strip()
    text_lower = text_clean.lower()

    educational_terms = [
        "lecture", "chapter", "topic", "unit", "lesson", "part",
        "module", "section", "week", "day", "grade", "level",
        "stage", "year", "semester", "class", "session",
        "assignment", "project", "lab", "tutorial", "workshop",
        "presentation", "discussion", "review", "quiz", "test",
        "exam", "final", "midterm", "assessment", "evaluation"
    ]

    for term in educational_terms:
        patterns = [
            rf'^{term}\s*\d+$',
            rf'^{term}\s*:\s*\d+$',
            rf'^\d+\s*{term}$',
            rf'^{term}\s*-\s*\d+$',
        ]
        for pattern in patterns:
            if re.match(pattern, text_lower):
                result = (text_clean.title(), True)
                st.session_state["validation_cache"][cache_key] = result
                return result

    language_levels = {
        "n1": "JLPT N1", "n2": "JLPT N2", "n3": "JLPT N3", "n4": "JLPT N4", "n5": "JLPT N5",
        "topik1": "TOPIK 1", "topik2": "TOPIK 2", "topik3": "TOPIK 3",
        "topik4": "TOPIK 4", "topik5": "TOPIK 5", "topik6": "TOPIK 6",
        "hsk1": "HSK 1", "hsk2": "HSK 2", "hsk3": "HSK 3",
        "hsk4": "HSK 4", "hsk5": "HSK 5", "hsk6": "HSK 6",
        "ielts": "IELTS", "toefl": "TOEFL", "toeic": "TOEIC", "pte": "PTE",
        "duolingo": "Duolingo English Test",
        "a1": "CEFR A1", "a2": "CEFR A2", "b1": "CEFR B1",
        "b2": "CEFR B2", "c1": "CEFR C1", "c2": "CEFR C2",
    }

    for abbr, full_name in language_levels.items():
        if text_lower == abbr or text_lower.startswith(abbr):
            result = (full_name, True)
            st.session_state["validation_cache"][cache_key] = result
            return result

    prof_certs = {
        "lcci": "LCCI", "acca": "ACCA", "cfa": "CFA", "cpa": "CPA",
        "pmp": "PMP", "scrum": "Scrum Master", "aws": "AWS",
        "azure": "Azure", "gcp": "GCP", "devops": "DevOps",
        "ccna": "CCNA", "ccnp": "CCNP", "ceh": "CEH", "cissp": "CISSP",
        "itil": "ITIL", "prince2": "PRINCE2", "sixsigma": "Six Sigma",
        "cima": "CIMA", "cim": "CIM", "dip": "Diploma",
    }

    for abbr, full_name in prof_certs.items():
        if text_lower == abbr or text_lower.startswith(abbr):
            result = (full_name, True)
            st.session_state["validation_cache"][cache_key] = result
            return result

    tech_terms = {
        "ai": "Artificial Intelligence", "ml": "Machine Learning",
        "dl": "Deep Learning", "nlp": "Natural Language Processing",
        "cv": "Computer Vision", "ds": "Data Science",
        "python": "Python Programming", "java": "Java Programming",
        "c++": "C++ Programming", "javascript": "JavaScript",
        "react": "React.js", "angular": "Angular", "vue": "Vue.js",
        "node": "Node.js", "django": "Django", "flask": "Flask",
        "sql": "SQL", "nosql": "NoSQL", "mongodb": "MongoDB",
        "mysql": "MySQL", "postgres": "PostgreSQL",
        "blockchain": "Blockchain", "iot": "IoT",
        "robotics": "Robotics", "automation": "Automation",
    }

    for abbr, full_name in tech_terms.items():
        if text_lower == abbr or text_lower.startswith(abbr):
            result = (full_name, True)
            st.session_state["validation_cache"][cache_key] = result
            return result

    countries_languages = [
        "japan", "myanmar", "korea", "china", "vietnam", "laos", "thailand",
        "japanese", "myanmar", "korean", "chinese", "vietnamese", "lao", "thai",
        "english", "french", "spanish", "german", "italian", "russian",
        "arabic", "hindi", "burmese", "khmer", "indonesian", "malay",
        "tagalog", "portuguese", "dutch", "swedish", "norwegian", "danish"
    ]

    for lang in countries_languages:
        if text_lower == lang or text_lower.startswith(lang):
            result = (lang.title(), True)
            st.session_state["validation_cache"][cache_key] = result
            return result

    academic_subjects = [
        "mathematics", "math", "physics", "chemistry", "biology", "history",
        "geography", "economics", "business", "accounting", "finance",
        "marketing", "management", "law", "psychology", "sociology",
        "anthropology", "philosophy", "linguistics", "literature"
    ]

    for subj in academic_subjects:
        if text_lower == subj or text_lower.startswith(subj):
            result = (subj.title(), True)
            st.session_state["validation_cache"][cache_key] = result
            return result

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system",
                 "content": f"""You are an educational content validator. Determine if the input has MEANING as an educational {text_type}.
                ANY educational {text_type} is VALID. INVALID: "asdfghjkl", "12345566". If misspelled, correct it.
                Return ONLY JSON: {{"valid": true/false, "corrected": "corrected text"}}"""},
                {"role": "user",
                 "content": f"Is '{text}' a meaningful educational {text_type}? If misspelled, correct it."}
            ],
            temperature=0.1,
            max_tokens=60
        )
        result = response.choices[0].message.content
        try:
            data = json.loads(result)
            is_valid = data.get("valid", False)
            corrected = data.get("corrected", text)
            result_tuple = (corrected, is_valid)
            st.session_state["validation_cache"][cache_key] = result_tuple
            return result_tuple
        except:
            if re.search(r'[a-zA-Z]', text) and len(text) >= 2:
                result_tuple = (text, True)
                st.session_state["validation_cache"][cache_key] = result_tuple
                return result_tuple
            result_tuple = (text, False)
            st.session_state["validation_cache"][cache_key] = result_tuple
            return result_tuple
    except Exception:
        if re.search(r'[a-zA-Z]', text) and len(text) >= 2:
            result_tuple = (text, True)
            st.session_state["validation_cache"][cache_key] = result_tuple
            return result_tuple
        result_tuple = (text, False)
        st.session_state["validation_cache"][cache_key] = result_tuple
        return result_tuple


# ---------- AI Timetable Generation ----------
def ai_generate_timetable(subjects: List[Dict[str, Any]], weeks: int, hours_per_day: float, start_time: str) -> Dict[
    str, Any]:
    if not AI_AVAILABLE:
        return generate_timetable_manual(subjects, weeks, hours_per_day, start_time)
    try:
        subject_details = []
        for s in subjects:
            topic = s.get("topic", "Other")
            skill = s.get("skill", "beginner")
            courses = s.get("courses", [])
            if courses:
                course_str = ", ".join(courses)
                subject_details.append(f"{topic} ({skill}) - Courses: {course_str}")
            else:
                subject_details.append(f"{topic} ({skill})")
        subject_list = ", ".join(subject_details)

        prompt = f"""
        Generate a study timetable for: {subject_list}
        Weeks: {weeks}, Study hours/day: {hours_per_day}, Start: {start_time}
        Rules: Total study time/day = {hours_per_day}h, include 35% Break slots, each day different.
        Return JSON: {{"weekly_schedule": [{{"week": 1, "days": [{{"day": "Monday", "slots": [{{"subject": "Subject", "start": "09:00 AM", "end": "10:00 AM", "focus": "Topic", "duration": "60 min"}}]}}]}}]}}
        """
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": "Generate timetable JSON only."},
                      {"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=2000
        )
        result = response.choices[0].message.content
        try:
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                if "weekly_schedule" in data:
                    return data
        except Exception:
            pass
        return generate_timetable_manual(subjects, weeks, hours_per_day, start_time)
    except Exception:
        return generate_timetable_manual(subjects, weeks, hours_per_day, start_time)


# ================================================================
# ===== FIXED: generate_timetable_manual (Exact time only) =====
# ================================================================
def generate_timetable_manual(subjects: List[Dict[str, Any]], weeks: int, hours_per_day: float, start_time: str) -> \
Dict[str, Any]:
    weeks = max(1, int(weeks))
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    try:
        start_dt = datetime.strptime(start_time, "%H:%M")
    except:
        start_dt = datetime.strptime("09:00", "%H:%M")

    total_subjects = len(subjects)
    if total_subjects == 0:
        return {"weekly_schedule": []}

    total_minutes = hours_per_day * 60
    if total_minutes < 15:
        total_minutes = 15

    weekly_schedule = []

    for week_num in range(1, weeks + 1):
        week_schedule = []

        for day_idx, day in enumerate(days):
            day_slots = []
            current_time = start_dt
            remaining_minutes = total_minutes

            # Determine number of slots for the day
            num_slots = max(1, total_subjects)
            # Cap slots to avoid too short durations
            if num_slots > 4:
                num_slots = 4
            # If total time is small, reduce slots
            if total_minutes < 30:
                num_slots = 1

            # Shuffle subjects for variety
            shuffled_subjects = subjects.copy()
            seed = week_num * 7 + day_idx
            shuffled_subjects = sorted(shuffled_subjects, key=lambda x: (hash(x.get("topic", "") + str(seed)) % 1000))

            # Distribute total_minutes across slots (round to 5 min)
            base_minutes = total_minutes // num_slots
            extra_minutes = total_minutes % num_slots

            slot_durations = []
            for i in range(num_slots):
                dur = base_minutes
                if i < extra_minutes:
                    dur += 1
                # Round to nearest 5
                dur = int(round(dur / 5) * 5)
                if dur < 1:
                    dur = 5
                slot_durations.append(dur)

            # Adjust last slot to match total exactly
            total_duration_sum = sum(slot_durations)
            if total_duration_sum != total_minutes:
                diff = total_minutes - total_duration_sum
                slot_durations[-1] += diff
                if slot_durations[-1] < 1:
                    slot_durations[-1] = 5

            for slot_idx in range(num_slots):
                if remaining_minutes <= 0:
                    break

                minutes = min(slot_durations[slot_idx] if slot_idx < len(slot_durations) else remaining_minutes,
                              remaining_minutes)
                if minutes <= 0:
                    continue

                # Get subject for this slot
                subject_data = shuffled_subjects[slot_idx % len(shuffled_subjects)]
                topic = subject_data.get("topic", "Study")
                skill = subject_data.get("skill", "beginner")
                courses = subject_data.get("courses", [])

                if courses and isinstance(courses, list):
                    focus_idx = (week_num * 7 + day_idx + slot_idx) % len(courses)
                    focus_area = courses[focus_idx]
                else:
                    tokens = re.findall(r'[a-zA-Z]+', topic.lower())
                    domain = detect_domain(tokens)
                    modules = DOMAIN_MODULES.get(domain, DOMAIN_MODULES["default"])
                    focus_idx = (week_num * 7 + day_idx + slot_idx) % len(modules)
                    focus_area = modules[focus_idx]

                end_time = current_time + timedelta(minutes=minutes)

                day_slots.append({
                    "subject": topic,
                    "start": format_time_12hr(current_time),
                    "end": format_time_12hr(end_time),
                    "duration": format_duration(int(minutes)),
                    "focus": focus_area,
                    "skill": skill,
                    "minutes": int(minutes)
                })

                current_time = end_time
                remaining_minutes -= minutes

            # If there's leftover time due to rounding, add a final slot
            end_of_day = start_dt + timedelta(minutes=total_minutes)
            if current_time < end_of_day:
                leftover = (end_of_day - current_time).total_seconds() / 60
                if leftover > 5:
                    subject_data = shuffled_subjects[slot_idx % len(shuffled_subjects)] if shuffled_subjects else {
                        "topic": "Study"}
                    topic = subject_data.get("topic", "Study")
                    day_slots.append({
                        "subject": topic,
                        "start": format_time_12hr(current_time),
                        "end": format_time_12hr(end_of_day),
                        "duration": format_duration(int(leftover)),
                        "focus": "Review / Practice",
                        "skill": "practice",
                        "minutes": int(leftover)
                    })
                    current_time = end_of_day

            week_schedule.append({
                "day": day,
                "slots": day_slots
            })

        weekly_schedule.append({
            "week": week_num,
            "days": week_schedule
        })

    return {"weekly_schedule": weekly_schedule}


# ---------- AI Study Tips ----------
def ai_get_study_tips(subject: str, skill: str) -> str:
    cache_key = f"tips_{subject}_{skill}"
    if "tips_cache" not in st.session_state:
        st.session_state["tips_cache"] = {}
    if cache_key in st.session_state["tips_cache"]:
        return st.session_state["tips_cache"][cache_key]

    if not AI_AVAILABLE:
        return f"Practice regularly and review your notes for {subject}."

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system",
                 "content": "You are a study coach. Give 3-5 practical, specific study tips for learning a subject. Be concise."},
                {"role": "user", "content": f"Give me study tips for {subject} at {skill} level."}
            ],
            temperature=0.5,
            max_tokens=200
        )
        tips = response.choices[0].message.content
        st.session_state["tips_cache"][cache_key] = tips
        return tips
    except Exception:
        return f"Practice regularly and review your notes for {subject}."


# ---------- PDF Generator - Beautiful Blue Gradient Version ----------
def generate_timetable_pdf(username: str, timetable_data: Dict[str, Any], subjects: List[Dict[str, Any]]) -> bytes:
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("reportlab not installed")

    buffer = io.BytesIO()

    # Create a custom canvas with gradient background
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    # Custom document template with gradient background
    class GradientDocTemplate(SimpleDocTemplate):
        def __init__(self, filename, **kwargs):
            SimpleDocTemplate.__init__(self, filename, **kwargs)

        def beforePage(self):
            # Get the canvas
            c = self.canv
            c.saveState()

            # Get page dimensions
            width, height = landscape(A4)

            # Draw gradient background
            # linear-gradient(145deg, #e3f2fd 0%, #bbdefb 50%, #90caf9 100%)
            gradient_colors = [
                ('#e3f2fd', 0),  # Start - Light blue
                ('#e8f4fd', 25),  # Transition
                ('#eef6fe', 35),  # Transition
                ('#bbdefb', 50),  # Middle - Medium blue
                ('#c8e5fc', 65),  # Transition
                ('#d4ebfd', 75),  # Transition
                ('#90caf9', 100),  # End - Darker light blue
            ]

            # Create gradient by drawing many small rectangles
            num_steps = 100
            for i in range(num_steps):
                # Calculate position and color
                pos = i / num_steps
                # Find which color segment we're in
                for j in range(len(gradient_colors) - 1):
                    color1, pos1 = gradient_colors[j]
                    color2, pos2 = gradient_colors[j + 1]
                    if pos1 <= pos * 100 <= pos2:
                        # Interpolate between colors
                        p = (pos * 100 - pos1) / (pos2 - pos1)
                        # Parse hex colors
                        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
                        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
                        r = r1 + (r2 - r1) * p
                        g = g1 + (g2 - g1) * p
                        b = b1 + (b2 - b1) * p
                        # Draw rectangle
                        x = 0
                        y = (height / num_steps) * i
                        rect_height = height / num_steps + 1
                        c.setFillColorRGB(r / 255.0, g / 255.0, b / 255.0)
                        c.rect(x, y, width, rect_height, fill=1, stroke=0)

            c.restoreState()

    doc = GradientDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )

    # ---------- CUSTOM STYLES ----------
    styles = getSampleStyleSheet()

    # Main header
    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        spaceAfter=2,
        textColor=colors.HexColor('#ffffff')
    )

    # Subtitle
    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#e0e7ff'),
        spaceAfter=2
    )

    # Info line style
    info_style = ParagraphStyle(
        "InfoStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#bfdbfe'),
        spaceAfter=2
    )

    # Section header
    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0d1b2a'),
        spaceBefore=6,
        spaceAfter=3
    )

    # Subject style
    subject_style = ParagraphStyle(
        "SubjectStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0d1b2a'),
        spaceAfter=2
    )

    # Skill badge style
    skill_style = ParagraphStyle(
        "SkillStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#1a73e8')
    )

    # Week header
    week_style = ParagraphStyle(
        "WeekStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#ffffff'),
        borderPadding=4,
        spaceBefore=4,
        spaceAfter=4,
        alignment=1
    )

    # Table cell style
    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#0d1b2a')
    )

    # Free cell style
    free_style = ParagraphStyle(
        "FreeStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#78909c')
    )

    # ---------- BUILD DOCUMENT ----------
    story = []

    # --- HEADER SECTION ---
    story.append(Spacer(1, 2))

    gradient_colors_header = ['#2b6cb0', '#4a90d9', '#63b3ed']

    header_text = "📚 STUDY TIMETABLE"
    subtitle_text = f"Generated for: <b><font color='#ffffff'>{username}</font></b> | {time.strftime('%Y-%m-%d %H:%M:%S')}"

    hours_per_day = timetable_data.get('hours_per_day', 4)
    start_time = timetable_data.get('start_time', '09:00')
    weeks = timetable_data.get('weeks', 2)

    if isinstance(hours_per_day, float):
        if hours_per_day == int(hours_per_day):
            hours_str = f"{int(hours_per_day)} hours"
        else:
            hours_str = f"{hours_per_day} hours"
    else:
        hours_str = f"{hours_per_day} hours"

    info_text = f"⏰ {hours_str}/day  •  🕐 {start_time}  •  📅 {weeks} weeks"

    gradient_data = []
    for i in range(len(gradient_colors_header)):
        if i == 0:
            gradient_data.append([Paragraph(header_text, header_style)])
        elif i == 1:
            gradient_data.append([Paragraph(subtitle_text, subtitle_style)])
        elif i == 2:
            gradient_data.append([Paragraph(info_text, info_style)])

    gradient_table = Table(gradient_data, colWidths=[10.5 * inch])
    gradient_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [10, 10, 10, 10]),
    ])

    for idx, color in enumerate(gradient_colors_header):
        gradient_style.add('BACKGROUND', (0, idx), (-1, idx), colors.HexColor(color))

    gradient_table.setStyle(gradient_style)
    story.append(gradient_table)

    # Decorative divider
    story.append(Spacer(1, 3))
    divider_data = [[""]]
    divider_table = Table(divider_data, colWidths=[10.5 * inch])
    divider_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, colors.HexColor('#4a90d9')),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    story.append(divider_table)
    story.append(Spacer(1, 4))

    # --- SUBJECT SECTION ---
    subject_header_colors = ['#ffffff', '#f0f7ff']
    subject_header_data = []
    for i in range(len(subject_header_colors)):
        if i == 0:
            subject_header_data.append([Paragraph("📖 SUBJECTS", section_style)])
        else:
            subject_header_data.append([""])

    subject_header_table = Table(subject_header_data, colWidths=[10.5 * inch])
    subject_header_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ])

    for idx, color in enumerate(subject_header_colors):
        subject_header_style.add('BACKGROUND', (0, idx), (-1, idx), colors.HexColor(color))

    subject_header_table.setStyle(subject_header_style)
    story.append(subject_header_table)
    story.append(Spacer(1, 2))

    # Subject data
    subject_data = []
    color_palette_subjects = [
        colors.HexColor('#e3f2fd'),
        colors.HexColor('#fce4ec'),
        colors.HexColor('#e8f5e9'),
        colors.HexColor('#fff3e0'),
    ]

    subject_row = []
    for idx, s in enumerate(subjects):
        topic = s.get('topic', 'Unknown')
        skill = s.get('skill', 'beginner')
        skill_emoji = "🌱" if skill == "beginner" else "🌿" if skill == "intermediate" else "🌟"
        skill_color = "#16a34a" if skill == "beginner" else "#1a73e8" if skill == "intermediate" else "#7c3aed"

        subject_cell = f'<b><font color="#0d1b2a">{topic}</font></b>'
        skill_cell = f'<font color="{skill_color}">{skill_emoji} {skill.upper()}</font>'

        subject_row.append([
            Paragraph(subject_cell, subject_style),
            Paragraph(skill_cell, skill_style)
        ])

    if subject_row:
        col_width = (10.5 * inch) / len(subject_row)
        subject_table = Table(
            subject_row,
            colWidths=[col_width] * len(subject_row),
            hAlign='CENTER'
        )

        subject_table_style = TableStyle([
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ])

        for i in range(len(subject_row)):
            color = color_palette_subjects[i % len(color_palette_subjects)]
            subject_table_style.add('BACKGROUND', (i, 0), (i, 0), color)
            subject_table_style.add('LINEAFTER', (i, 0), (i, 0), 1, colors.HexColor('#bbdefb'))

        subject_table.setStyle(subject_table_style)
        story.append(subject_table)

    story.append(Spacer(1, 4))

    # --- TIMETABLE DATA ---
    weekly_schedule = timetable_data.get("weekly_schedule", [])

    if not weekly_schedule:
        no_data_style = ParagraphStyle(
            "NoDataStyle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#546e7a'),
            alignment=1
        )
        story.append(Paragraph("No timetable data available", no_data_style))
    else:
        # --- WEEKLY TIMETABLES ---
        for week_idx, week in enumerate(weekly_schedule):
            week_num = week.get('week', week_idx + 1)
            days_data = week.get("days", [])

            if not days_data:
                continue

            # --- WEEK HEADER ---
            week_gradient_colors = ['#2b6cb0', '#4a90d9', '#63b3ed']

            week_gradient_data = []
            week_text = f"📅 WEEK {week_num}"

            for i in range(len(week_gradient_colors)):
                if i == 0:
                    week_gradient_data.append([Paragraph(week_text, week_style)])
                else:
                    week_gradient_data.append([""])

            week_gradient_table = Table(week_gradient_data, colWidths=[10.5 * inch])
            week_gradient_style = TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('ROUNDEDCORNERS', [6, 6, 6, 6]),
            ])

            for idx, color in enumerate(week_gradient_colors):
                week_gradient_style.add('BACKGROUND', (0, idx), (-1, idx), colors.HexColor(color))

            week_gradient_table.setStyle(week_gradient_style)
            story.append(week_gradient_table)
            story.append(Spacer(1, 3))

            # --- Collect time slots ---
            all_time_slots = []
            time_slot_to_slots = {}

            for day in days_data:
                day_name = day.get("day", "")
                for slot in day.get("slots", []):
                    start = slot.get('start', '')
                    end = slot.get('end', '')
                    if start and end:
                        time_range = f"{start} - {end}"
                        if time_range not in all_time_slots:
                            all_time_slots.append(time_range)
                            time_slot_to_slots[time_range] = {}
                        time_slot_to_slots[time_range][day_name] = slot

            def parse_time_for_sort(t):
                try:
                    return datetime.strptime(t.split(" - ")[0].strip(), "%I:%M %p")
                except:
                    try:
                        return datetime.strptime(t.split(" - ")[0].strip(), "%H:%M")
                    except:
                        return datetime.strptime("12:00 AM", "%I:%M %p")

            all_time_slots.sort(key=parse_time_for_sort)

            if all_time_slots and days_data:
                # Header row
                header_cells = ["TIME"] + [day.get("day", "---").upper()[:3] for day in days_data]
                table_data = [header_cells]

                # Data rows
                for time_slot in all_time_slots:
                    row = [time_slot]

                    for day in days_data:
                        day_name = day.get("day", "")

                        if day_name in time_slot_to_slots.get(time_slot, {}):
                            slot = time_slot_to_slots[time_slot][day_name]
                            subject = slot.get("subject", "")
                            focus = slot.get("focus", "")
                            duration = slot.get("duration", "")

                            if subject.lower() == "break":
                                cell_text = f'<font color="#78909c"><i>☕ Break</i></font>'
                                if duration:
                                    cell_text += f'<br/><font size="8" color="#78909c">{duration}</font>'
                            elif subject.lower() == "free":
                                cell_text = f'<font color="#78909c"><i>⏳ Free</i></font>'
                                if duration:
                                    cell_text += f'<br/><font size="8" color="#78909c">{duration}</font>'
                            else:
                                cell_text = f'<b><font size="10">{subject}</font></b>'
                                if focus and focus not in ["Focus", "Rest / Refresh", ""]:
                                    cell_text += f'<br/><font size="8" color="#546e7a">📖 {focus[:20]}</font>'
                                if duration:
                                    cell_text += f'<br/><font size="8" color="#1a73e8"><b>{duration}</b></font>'

                            row.append(Paragraph(cell_text, cell_style))
                        else:
                            row.append(Paragraph("—", free_style))

                    table_data.append(row)

                # Auto-calculate column widths
                time_col_width = 1.5 * inch
                remaining_width = 10.5 * inch - time_col_width
                day_col_width = remaining_width / len(days_data) if len(days_data) > 0 else 1.3 * inch

                table = Table(
                    table_data,
                    colWidths=[time_col_width] + [day_col_width] * len(days_data),
                    repeatRows=1
                )

                # Table styling with white background for readability
                table_style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('TOPPADDING', (0, 0), (-1, 0), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),

                    ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#e3f2fd')),
                    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 1), (0, -1), 9),
                    ('TEXTCOLOR', (0, 1), (0, -1), colors.HexColor('#1a73e8')),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    ('LEFTPADDING', (0, 1), (0, -1), 8),

                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('VALIGN', (1, 1), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (1, 1), (-1, -1), 9),
                    ('TOPPADDING', (0, 1), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                    ('LEFTPADDING', (0, 1), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 1), (-1, -1), 4),

                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bbdefb')),
                    ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#4a90d9')),
                    ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f5faff')]),
                ])

                # Subject color coding
                subject_colors = {}
                color_palette = [
                    colors.HexColor('#e3f2fd'),
                    colors.HexColor('#fce4ec'),
                    colors.HexColor('#e8f5e9'),
                    colors.HexColor('#fff3e0'),
                    colors.HexColor('#f3e5f5'),
                    colors.HexColor('#e0f7fa'),
                    colors.HexColor('#f1f8e9'),
                    colors.HexColor('#fbe9e7'),
                ]
                color_idx = 0

                for row_idx, row in enumerate(table_data[1:], start=1):
                    for col_idx, cell in enumerate(row[1:], start=1):
                        if hasattr(cell, 'getPlainText'):
                            text = cell.getPlainText()
                            if '<b>' in text and 'Break' not in text and 'Free' not in text:
                                import re
                                match = re.search(r'<b>(.*?)</b>', text)
                                if match:
                                    subject = match.group(1)
                                    if subject not in subject_colors:
                                        subject_colors[subject] = color_palette[color_idx % len(color_palette)]
                                        color_idx += 1
                                    table_style.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx),
                                                    subject_colors[subject])

                table.setStyle(table_style)
                story.append(table)
                story.append(Spacer(1, 5))

                if week.get("note"):
                    note_style = ParagraphStyle(
                        "NoteStyle",
                        parent=styles["Normal"],
                        fontName="Helvetica-Oblique",
                        fontSize=9,
                        leading=11,
                        textColor=colors.HexColor('#546e7a')
                    )
                    story.append(Paragraph(f"📌 {week['note']}", note_style))
                    story.append(Spacer(1, 2))
            else:
                no_slots_style = ParagraphStyle(
                    "NoSlotsStyle",
                    parent=styles["Normal"],
                    fontName="Helvetica",
                    fontSize=10,
                    leading=13,
                    textColor=colors.HexColor('#78909c'),
                    alignment=1
                )
                story.append(Paragraph("No schedule available for this week", no_slots_style))
                story.append(Spacer(1, 3))

            story.append(Spacer(1, 2))

    # --- FOOTER ---
    footer_style = ParagraphStyle(
        "FooterStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#546e7a'),
        alignment=1
    )
    story.append(Spacer(1, 6))

    footer_line_data = [[""]]
    footer_line_table = Table(footer_line_data, colWidths=[10.5 * inch])
    footer_line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
        ('LINEABOVE', (0, 0), (-1, -1), 1.5, colors.HexColor('#4a90d9')),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(footer_line_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("✨ <b>Study Planner</b>  •  Plan your week  •  Progress, not Perfection ✨", footer_style))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.read()