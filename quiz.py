# quiz.py - Quiz Page (Fixed - CSS removed, uses app.py gradient)
import html
import io
import json
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def get_profile_picture(username: str):
    """Return the active profile picture from session state or users_db."""
    picture = st.session_state.get("profile_pic")
    if picture:
        return picture

    users = st.session_state.get("users_db", {})
    profile = users.get(username, {}).get("profile", {})
    picture = profile.get("profile_pic")
    if picture:
        st.session_state["profile_pic"] = picture
    return picture


# ----------------------------- State -----------------------------

def initialize_quiz_state() -> None:
    defaults = {
        "current_quiz": [],
        "quiz_answers": {},
        "quiz_topic": "",
        "quiz_difficulty": "Medium",
        "quiz_type": "Mixed",
        "quiz_stage": "setup",
        "quiz_result": None,
        "quiz_history_saved": False,
        "quiz_time_limit": "No limit",
        "quiz_deadline": None,
        "quiz_started_at": None,
        "quiz_alert": None,
        "quiz_auto_submitted": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_alert(kind: str, message: str) -> None:
    st.session_state["quiz_alert"] = {"kind": kind, "message": message}


def render_alert() -> None:
    alert = st.session_state.pop("quiz_alert", None)
    if not alert:
        return
    kind = alert.get("kind", "info")
    icon = "✓" if kind == "success" else "!" if kind in {"error", "warning"} else "i"
    st.markdown(
        f'<div style="display:flex;align-items:flex-start;gap:10px;margin:0 0 15px;padding:13px 15px;border:1px solid;border-radius:11px;font-size:13px;line-height:1.45;{"border-color:#cce8db;background:#f1faf6;color:#246b53;" if kind=="success" else "border-color:#f0cfd3;background:#fff4f5;color:#a73743;" if kind=="error" else "border-color:#cfdbef;background:#f3f7fd;color:#385f91;"}"><span style="display:grid;width:22px;height:22px;min-width:22px;place-items:center;border-radius:50%;color:white;font-weight:800;{"background:#34906e;" if kind=="success" else "background:#cf4b56;" if kind=="error" else "background:#4c78ad;"}">{icon}</span><div>{html.escape(alert.get("message", ""))}</div></div>',
        unsafe_allow_html=True,
    )


# ----------------------------- Services -----------------------------

def import_quiz_services():
    try:
        from database.db_manager import save_history
    except Exception:
        save_history = None

    try:
        from ai.groq_service import generate_quiz as project_generate_quiz
    except Exception:
        project_generate_quiz = None

    try:
        from file_reader import extract_text as project_extract_text
    except Exception:
        project_extract_text = None

    return save_history, project_generate_quiz, project_extract_text


# ----------------------------- Source helpers -----------------------------

def clean_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))


def source_sentences(text: str) -> List[str]:
    cleaned = clean_text(text)
    if not cleaned:
        return []
    pieces = re.split(r"(?<=[.!?。！？；;])\s*|[\r\n]+", cleaned)
    result: List[str] = []
    seen = set()
    for piece in pieces:
        sentence = clean_text(piece).strip("-• ")
        if len(sentence) < 8:
            continue
        if len(sentence) > 260:
            sentence = sentence[:260].rsplit(" ", 1)[0] or sentence[:260]
        identity = sentence.casefold()
        if identity not in seen:
            seen.add(identity)
            result.append(sentence)
    return result


def source_keywords(text: str, limit: int = 10) -> List[str]:
    cleaned = clean_text(text)

    if contains_cjk(cleaned):
        chinese_text = "".join(
            re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", cleaned)
        )
        stop_terms = {
            "这个", "一个", "我们", "你们", "他们", "以及", "可以", "进行",
            "主要", "相关", "内容", "学习", "资料", "问题", "答案", "根据",
            "提供", "使用", "通过", "其中", "为了", "没有", "不是", "什么",
        }
        counts: Dict[str, int] = {}
        for size in (2, 3, 4):
            for index in range(max(0, len(chinese_text) - size + 1)):
                term = chinese_text[index:index + size]
                if term in stop_terms:
                    continue
                if len(set(term)) == 1:
                    continue
                counts[term] = counts.get(term, 0) + 1

        ranked = sorted(
            counts,
            key=lambda item: (-counts[item], -len(item), item),
        )
        selected: List[str] = []
        for term in ranked:
            if any(term in existing or existing in term for existing in selected):
                continue
            selected.append(term)
            if len(selected) >= limit:
                break
        return selected

    stop = {
        "about", "after", "again", "also", "because", "before", "between",
        "could", "during", "from", "have", "into", "more", "most", "other",
        "over", "such", "than", "that", "their", "there", "these", "they",
        "this", "through", "under", "using", "very", "what", "when", "where",
        "which", "while", "with", "would", "information", "material", "study",
        "source", "question", "answer", "content", "topic",
    }
    counts: Dict[str, int] = {}
    forms: Dict[str, str] = {}
    for word in re.findall(r"\b[^\W\d_][\w'-]{3,}\b", cleaned, flags=re.UNICODE):
        normalized = word.casefold()
        if normalized in stop:
            continue
        counts[normalized] = counts.get(normalized, 0) + 1
        forms.setdefault(normalized, word)

    ranked = sorted(
        counts,
        key=lambda item: (-counts[item], item),
    )
    return [forms[item] for item in ranked[:limit]]


def source_analysis(text: str) -> Dict[str, object]:
    cleaned = clean_text(text)
    sentences = source_sentences(cleaned)
    summary = " ".join(sentences[:2]) if sentences else cleaned[:360]

    if len(summary) > 420:
        summary = summary[:420].rsplit(" ", 1)[0] + "..."

    keywords = source_keywords(cleaned, 10)
    source_units = len(cleaned) if contains_cjk(cleaned) else len(cleaned.split())

    return {
        "word_count": source_units,
        "sentence_count": len(sentences),
        "keyword_count": len(keywords),
        "topics": keywords[:6],
        "topic_count": len(keywords[:6]),
        "summary": summary or "Add a topic or upload a file to preview.",
        "keywords": keywords,
    }


def split_source(text: str, batch_count: int, chunk_size: int = 4200) -> List[str]:
    cleaned = clean_text(text)
    if not cleaned:
        return []
    if len(cleaned) <= chunk_size:
        return [cleaned] * max(1, batch_count)

    sentences = source_sentences(cleaned)
    chunks: List[str] = []
    current: List[str] = []
    current_length = 0
    for sentence in sentences:
        if current and current_length + len(sentence) > chunk_size:
            chunks.append(" ".join(current))
            current = []
            current_length = 0
        current.append(sentence)
        current_length += len(sentence) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks or [cleaned[:chunk_size]]


# ----------------------------- Grounded generators -----------------------------

def normalize_question(item: object) -> Optional[Dict[str, object]]:
    if not isinstance(item, dict):
        return None
    question = clean_text(item.get("question"))
    answer = clean_text(item.get("correct_answer"))
    if not question or not answer:
        return None

    choices = item.get("choices", [])
    if not isinstance(choices, list):
        choices = []
    choices = [clean_text(choice) for choice in choices if clean_text(choice)]

    q_type = clean_text(item.get("type", "MCQ")) or "MCQ"
    normalized = re.sub(r"[^a-z]", "", q_type.casefold())
    if "truefalse" in normalized:
        q_type = "TrueFalse"
        choices = ["True", "False"]
    elif "blank" in normalized:
        q_type = "FillBlank"
        choices = []
    else:
        q_type = "MCQ" if choices else "FillBlank"

    return {
        "type": q_type,
        "question": question,
        "choices": choices,
        "correct_answer": answer,
        "explanation": clean_text(item.get("explanation")) or "The answer is supported by the supplied source.",
    }


def grounded_offline_quiz(source: str, count: int, difficulty: str, quiz_type: str) -> List[Dict[str, object]]:
    cleaned = clean_text(source)
    sentences = source_sentences(cleaned)
    chinese = contains_cjk(cleaned)

    if not sentences:
        sentences = [cleaned]

    short_topic_only = len(cleaned) <= 80 and len(sentences) <= 1
    selected_type = re.sub(r"[^a-z]", "", quiz_type.casefold())
    cards: List[Dict[str, object]] = []

    for index in range(max(1, int(count))):
        sentence = sentences[index % len(sentences)]
        keywords = source_keywords(sentence, 8)
        mode = selected_type
        if mode == "mixed":
            mode = ["mcq", "truefalse", "fillblank"][index % 3]

        if short_topic_only:
            if chinese:
                prompts = [
                    "本测验的主题是什么？",
                    "请选择本次学习内容的主题。",
                    "请写出需要复习的主题。",
                ]
                question = prompts[index % len(prompts)]
                choices = [cleaned, "数学", "历史", "地理"] if mode == "mcq" else []
                card_type = "MCQ" if choices else "FillBlank"
                answer = cleaned
                explanation = f"题目来源于用户输入的主题：{cleaned}。"
            else:
                prompts = [
                    "What is the selected topic for this quiz?",
                    "Which topic should be reviewed in this practice set?",
                    "Enter the topic supplied for this quiz.",
                ]
                question = prompts[index % len(prompts)]
                choices = [cleaned, "Mathematics", "History", "Geography"] if mode == "mcq" else []
                card_type = "MCQ" if choices else "FillBlank"
                answer = cleaned
                explanation = f'The user supplied "{cleaned}" as the quiz topic.'
        elif mode == "fillblank" and keywords:
            answer = keywords[index % len(keywords)]
            question = re.sub(re.escape(answer), "______", sentence, count=1, flags=re.IGNORECASE)
            choices = []
            card_type = "FillBlank"
            explanation = sentence
        elif mode == "truefalse":
            question = sentence
            choices = ["True", "False"]
            card_type = "TrueFalse"
            answer = "True"
            explanation = "This statement appears in the supplied source."
        else:
            answer = sentence
            if chinese:
                question = "根据提供的学习资料，哪一项陈述是正确的？"
                distractors = [
                    "该陈述未在提供的资料中出现。",
                    "资料表达了完全相反的意思。",
                    "该选项与学习资料无关。",
                ]
            else:
                question = "Which statement is supported by the supplied study material?"
                distractors = [
                    "This statement is not present in the supplied material.",
                    "The source states the opposite of this option.",
                    "This option is unrelated to the supplied material.",
                ]
            choices = [answer] + distractors
            random.Random(index + len(cleaned)).shuffle(choices)
            card_type = "MCQ"
            explanation = "The correct statement is taken directly from the supplied source."

        cards.append({
            "type": card_type,
            "question": question,
            "choices": choices,
            "correct_answer": answer,
            "explanation": explanation,
            "difficulty": difficulty,
        })

    return cards[:count]


def strict_smart_quiz(
    project_generate_quiz,
    source: str,
    count: int,
    difficulty: str,
    quiz_type: str,
    source_kind: str,
    focus: str,
    output_language: str,
    custom_instructions: str,
) -> List[Dict[str, object]]:
    if project_generate_quiz is None:
        raise RuntimeError("Smart generation service is unavailable.")

    if source_kind == "topic":
        boundary = (
            "The SOURCE is a topic supplied by the learner. Generate accurate educational "
            "questions specifically about that topic. Never switch to Python or any unrelated subject."
        )
    else:
        boundary = (
            "The SOURCE is extracted study material. Every question and answer must be supported "
            "by the material. Do not use outside facts, references, footnotes, page numbers, file names, "
            "or unrelated sentences. Test only content the learner needs to read and remember."
        )

    prompt_source = f"""
SOURCE-GROUNDING RULES:
1. {boundary}
2. The exact subject is the SOURCE below.
3. Do not output questions about Python unless Python is actually in the SOURCE.
4. Do not invent facts that conflict with the SOURCE.
5. Ignore bibliography, references, headers, footers, and navigation text.
6. Keep questions concise, clear, and useful for study.
7. Output language: {output_language}.
8. Learning focus: {focus}.
9. Additional learner instructions: {custom_instructions.strip() or 'None'}.

SOURCE:
{source}
""".strip()

    raw = project_generate_quiz(prompt_source, count, difficulty, quiz_type)
    if not isinstance(raw, list):
        raise TypeError("Smart generation must return a list of questions.")

    normalized: List[Dict[str, object]] = []
    for item in raw:
        question = normalize_question(item)
        if question is not None:
            normalized.append(question)
    return normalized[:count]


def generate_in_batches(
    source: str,
    total: int,
    difficulty: str,
    quiz_type: str,
    mode: str,
    project_generate_quiz,
    source_kind: str,
    focus: str,
    language: str,
    instructions: str,
) -> List[Dict[str, object]]:
    total = max(1, min(int(total), 100))
    batch_size = 10
    batch_count = (total + batch_size - 1) // batch_size
    chunks = split_source(source, batch_count)
    progress = st.progress(0, text="Preparing questions...")
    result: List[Dict[str, object]] = []
    seen = set()

    for batch_index in range(batch_count):
        requested = min(batch_size, total - len(result))
        if requested <= 0:
            break
        chunk = chunks[batch_index % len(chunks)]

        if mode == "Smart generation":
            generated = strict_smart_quiz(
                project_generate_quiz,
                chunk,
                requested,
                difficulty,
                quiz_type,
                source_kind,
                focus,
                language,
                instructions,
            )
        else:
            generated = grounded_offline_quiz(chunk, requested, difficulty, quiz_type)

        for item in generated:
            normalized = normalize_question(item)
            if normalized is None:
                continue
            identity = re.sub(r"\W+", "", normalized["question"].casefold(), flags=re.UNICODE)
            if identity and identity not in seen:
                seen.add(identity)
                result.append(normalized)
            if len(result) >= total:
                break

        progress.progress((batch_index + 1) / batch_count, text=f"Completed part {batch_index + 1} of {batch_count}")

    progress.empty()
    return result[:total]


# ----------------------------- Timer -----------------------------

def parse_time_limit(label: str) -> Optional[int]:
    if not label or label == "No limit":
        return None
    match = re.search(r"(\d+)", label)
    return int(match.group(1)) * 60 if match else None


def initialize_timer(label: str) -> None:
    seconds = parse_time_limit(label)
    st.session_state.quiz_started_at = time.time()
    st.session_state.quiz_deadline = time.time() + seconds if seconds else None
    st.session_state.quiz_auto_submitted = False


def widget_key(index: int, question: Dict[str, object]) -> str:
    q_type = str(question.get("type", "MCQ")).casefold()
    return f"quiz_answer_{index}_{'text' if 'blank' in q_type else 'choice'}"


def collect_answers() -> Dict[int, str]:
    answers: Dict[int, str] = {}
    for index, question in enumerate(st.session_state.current_quiz):
        value = st.session_state.get(widget_key(index, question))
        if value is not None and clean_text(value):
            answers[index] = str(value)
    return answers


def grade_and_finish(auto_submit: bool = False) -> None:
    questions = st.session_state.current_quiz
    answers = collect_answers()
    score = 0

    for index, question in enumerate(questions):
        given = clean_text(answers.get(index, "")).casefold()
        correct = clean_text(question.get("correct_answer", "")).casefold()
        if given and given == correct:
            score += 1

    started_at = st.session_state.get("quiz_started_at") or time.time()
    elapsed_seconds = max(0, int(time.time() - started_at))
    selected_limit = parse_time_limit(st.session_state.get("quiz_time_limit", "No limit"))

    if auto_submit and selected_limit is not None:
        elapsed_seconds = selected_limit

    total = len(questions)
    st.session_state.quiz_answers = answers
    st.session_state.quiz_result = {
        "score": score,
        "total": total,
        "percentage": round(score / total * 100, 2) if total else 0,
        "auto_submitted": auto_submit,
        "elapsed_seconds": elapsed_seconds,
        "answered_count": len(answers),
        "unanswered_count": max(0, total - len(answers)),
    }
    st.session_state.quiz_auto_submitted = auto_submit
    st.session_state.quiz_stage = "result"
    if auto_submit:
        set_alert("warning", "Time expired. The answers saved before the deadline were submitted automatically.")
    st.rerun()


# ✅ အသစ် code (ဒီဟာကိုထည့်ပါ)
@st.fragment(run_every=1.0)
def render_countdown() -> None:
    # ✅ အကုန်လုံးကိုစစ်ပါ
    quiz_stage = st.session_state.get("quiz_stage")
    current_quiz = st.session_state.get("current_quiz")
    deadline = st.session_state.get("quiz_deadline")
    
    # ✅ ဒါတွေမရှိရင် ဘာမှမလုပ်ပါနဲ့
    if quiz_stage != "answer" or not current_quiz or not deadline:
        return
    
    remaining = max(0, int(deadline - time.time()))
    minutes, seconds = divmod(remaining, 60)
    
    if remaining <= 60:
        css = 'border-color:#efc7cc;background:rgba(255,244,245,0.9);'
        css_strong = 'color:#c74855;'
    elif remaining <= 300:
        css = 'border-color:#ecd29f;background:rgba(255,250,240,0.9);'
        css_strong = ''
    else:
        css = 'border-color:#eef2f6;background:rgba(255,255,255,0.88);'
        css_strong = ''
    
    st.markdown(
        f'<div style="min-width:150px;padding:11px 14px;border:1px solid;border-radius:12px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.04);backdrop-filter:blur(8px);{css}">'
        f'<strong style="display:block;color:#183153;font-size:20px;letter-spacing:.03em;{css_strong}">{minutes:02d}:{seconds:02d}</strong>'
        '<span style="color:#7b8797;font-size:11px;">Time remaining</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    
    # ✅ Auto-submit မလုပ်ခင် ထပ်စစ်ပါ
    if remaining <= 0 and st.session_state.get("quiz_stage") == "answer":
        if st.session_state.get("current_quiz"):
            grade_and_finish(auto_submit=True)

# ----------------------------- Downloads -----------------------------

def safe_pdf(value: object) -> str:
    return html.escape(str(value or "")).replace("\n", "<br/>")


def build_pdf(questions, title, answers=None, include_answers=False):
    if not REPORTLAB_AVAILABLE:
        return None
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )
    styles = getSampleStyleSheet()
    story = [Paragraph(safe_pdf(title), styles["Title"]), Spacer(1, 9)]
    for index, question in enumerate(questions):
        story.append(Paragraph(f"<b>Question {index + 1}</b>", styles["Heading3"]))
        story.append(Paragraph(safe_pdf(question.get("question")), styles["BodyText"]))
        for choice_index, choice in enumerate(question.get("choices", []) or []):
            story.append(Paragraph(f"{chr(65 + choice_index)}. {safe_pdf(choice)}", styles["BodyText"]))
        if include_answers:
            story.append(Paragraph(f"<b>Your answer:</b> {safe_pdf((answers or {}).get(index, 'No answer'))}", styles["BodyText"]))
            story.append(Paragraph(f"<b>Correct answer:</b> {safe_pdf(question.get('correct_answer'))}", styles["BodyText"]))
            story.append(Paragraph(f"<b>Explanation:</b> {safe_pdf(question.get('explanation'))}", styles["BodyText"]))
        story.append(Spacer(1, 10))
    document.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ----------------------------- UI -----------------------------

def render_header() -> None:
    login_username = str(st.session_state.get("username") or "Student")

    users_db = st.session_state.get("users_db", {})
    user_data = users_db.get(login_username, {})
    profile = user_data.get("profile", {})

    display_name = str(
        profile.get("name")
        or profile.get("display_name")
        or login_username
    ).strip() or login_username

    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    profile_picture = get_profile_picture(login_username)
    if profile_picture:
        avatar_html = f'<img src="{html.escape(profile_picture)}" alt="Profile picture" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">'
    else:
        avatar_html = html.escape(display_name[:1].upper() or "S")

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin:0 0 22px;padding:13px 18px;border:1px solid rgba(255,255,255,0.3);border-radius:15px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.10);backdrop-filter:blur(12px);">
        <div style="display:grid;width:44px;height:44px;min-width:44px;place-items:center;overflow:hidden;border:2px solid rgba(255,255,255,0.5);border-radius:50%;background:linear-gradient(135deg,#4f8dff,#8b5cf6);color:#fff;font-size:16px;font-weight:700;">
            {avatar_html}
        </div>
        <div style="flex:1;min-width:0;">
            <div style="display:flex;align-items:center;flex-wrap:wrap;gap:8px;">
                <span style="color:#183153;font-size:18px;font-weight:700;">{html.escape(display_name)}</span>
                <span style="display:inline-flex;align-items:center;padding:3px 9px;border:1px solid #dce5ff;border-radius:999px;background:#f0f4fe;color:#4f8dff;font-size:10px;font-weight:700;line-height:1;">Quiz</span>
            </div>
            <div style="margin-top:2px;color:#7b8797;font-size:13px;line-height:1.4;">
                {greeting}! Test your knowledge with interactive quizzes.
            </div>
        </div>
        <div style="padding:6px 12px;border:1px solid rgba(255,255,255,0.3);border-radius:9px;background:rgba(248,250,255,0.7);color:#7b8797;font-size:12px;white-space:nowrap;">
            <i class="fas fa-calendar-day" style="color:#4f8dff;margin-right:6px;"></i> {datetime.now().strftime("%B %d, %Y")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Font Awesome
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    """, unsafe_allow_html=True)


def render_steps(active: int) -> None:
    labels = ["Upload", "Review", "Setup", "Create", "Start"]
    items = []
    for number, label in enumerate(labels, 1):
        state = "active" if number == active else "done" if number < active else ""
        color = "#183153" if state else "#b0b8c4"
        bg = "linear-gradient(135deg,#4f8dff,#6c5ce7)" if state else "#eef2f6"
        text_color = "white" if state else "#7b8797"
        items.append(f'<div style="display:flex;align-items:center;gap:6px;color:{color};font-size:12px;font-weight:600;white-space:nowrap;"><span style="display:grid;width:24px;height:24px;place-items:center;border-radius:50%;background:{bg};color:{text_color};font-size:11px;font-weight:700;">{number}</span>{label}</div>')
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:22px;padding:15px 20px;border:1px solid rgba(255,255,255,0.3);border-radius:14px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);flex-wrap:wrap;">' + 
        '<div style="width:16px;height:2px;background:rgba(255,255,255,0.3);"></div>'.join(items) + 
        '</div>',
        unsafe_allow_html=True,
    )


def render_setup(project_generate_quiz, project_extract_text) -> None:
    render_steps(1)
    left, right = st.columns([2.08, 0.92], gap="large")

    with left:
        st.markdown("""
        <div style="display:flex;align-items:flex-start;gap:10px;margin:0 0 13px;padding:12px 14px;border:1px solid rgba(255,255,255,0.3);border-radius:12px;background:rgba(255,255,255,0.6);backdrop-filter:blur(8px);">
            <span style="display:grid;width:24px;height:24px;min-width:24px;place-items:center;border-radius:50%;background:linear-gradient(135deg,#4f8dff,#6c5ce7);color:#fff;font-size:11px;font-weight:800;">1</span>
            <div><strong style="display:block;color:#183153;font-size:14px;font-weight:700;"><i class="fas fa-file-arrow-up" style="margin-right:6px;color:#183153;"></i> Add Material</strong>
            <small style="display:block;margin-top:1px;color:#7b8797;font-size:12px;line-height:1.4;">Enter a topic or upload a file.</small></div>
        </div>
        """, unsafe_allow_html=True)
        
        topic = st.text_input(
            "Topic or subject",
            key="quiz_setup_topic",
            placeholder="e.g. Python, English, Science",
        )
        uploaded = st.file_uploader(
            "Upload file",
            type=["pdf", "docx", "pptx", "txt"],
            key="quiz_setup_file",
            help="Supported formats: PDF, DOCX, PPTX, TXT",
        )

        source = topic.strip()
        source_kind = "topic"
        source_label = topic.strip() or "Topic not entered"
        file_error = None
        if uploaded is not None:
            source_kind = "file"
            source_label = uploaded.name
            if project_extract_text is None:
                file_error = "The project file reader is unavailable."
                source = ""
            else:
                try:
                    uploaded.seek(0)
                    source = project_extract_text(uploaded)
                except Exception as error:
                    file_error = str(error)
                    source = ""
        if file_error:
            st.error(f"File reading failed: {file_error}")

        st.markdown("""
        <div style="display:flex;align-items:flex-start;gap:10px;margin:17px 0 13px;padding:12px 14px;border:1px solid rgba(255,255,255,0.3);border-radius:12px;background:rgba(255,255,255,0.6);backdrop-filter:blur(8px);">
            <span style="display:grid;width:24px;height:24px;min-width:24px;place-items:center;border-radius:50%;background:linear-gradient(135deg,#4f8dff,#6c5ce7);color:#fff;font-size:11px;font-weight:800;">2</span>
            <div><strong style="display:block;color:#183153;font-size:14px;font-weight:700;"><i class="fas fa-brain" style="margin-right:6px;color:#183153;"></i> Smart Analysis</strong>
            <small style="display:block;margin-top:1px;color:#7b8797;font-size:12px;line-height:1.4;">Guide the question generator.</small></div>
        </div>
        """, unsafe_allow_html=True)
        
        analysis_cols = st.columns(2)
        with analysis_cols[0]:
            focus = st.selectbox(
                "Focus",
                ["Balanced", "Key Concepts", "Definitions", "Facts & Terms", "Reasoning", "Exam Review"],
                key="quiz_focus",
            )
        with analysis_cols[1]:
            language = st.selectbox(
                "Language",
                ["Same as source", "English", "Chinese", "Myanmar"],
                key="quiz_language",
            )
        instructions = st.text_area(
            "Instructions",
            placeholder="e.g. Focus on definitions and applications.",
            height=88,
            key="quiz_instructions",
        )
        check_cols = st.columns(2)
        with check_cols[0]:
            strict_source = st.checkbox("Use only supplied material", value=True, key="quiz_strict_source")
        with check_cols[1]:
            include_explanations = st.checkbox("Include explanations", value=True, key="quiz_explanations")

        st.markdown("""
        <div style="display:flex;align-items:flex-start;gap:10px;margin:17px 0 13px;padding:12px 14px;border:1px solid rgba(255,255,255,0.3);border-radius:12px;background:rgba(255,255,255,0.6);backdrop-filter:blur(8px);">
            <span style="display:grid;width:24px;height:24px;min-width:24px;place-items:center;border-radius:50%;background:linear-gradient(135deg,#4f8dff,#6c5ce7);color:#fff;font-size:11px;font-weight:800;">3</span>
            <div><strong style="display:block;color:#183153;font-size:14px;font-weight:700;"><i class="fas fa-sliders" style="margin-right:6px;color:#183153;"></i> Setup Quiz</strong>
            <small style="display:block;margin-top:1px;color:#7b8797;font-size:12px;line-height:1.4;">Choose difficulty, count, and format.</small></div>
        </div>
        """, unsafe_allow_html=True)
        
        row1 = st.columns(3)
        with row1[0]:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="quiz_setting_difficulty")
        with row1[1]:
            count = st.number_input("Questions", min_value=1, max_value=100, value=10, step=1, key="quiz_setting_count")
        with row1[2]:
            quiz_type = st.selectbox("Type", ["Mixed", "MCQ", "True/False", "Fill Blank"], key="quiz_setting_type")

        row2 = st.columns(3)
        with row2[0]:
            mode = st.radio("Mode", ["Smart generation", "Built-in practice"], key="quiz_setting_mode")
        with row2[1]:
            time_limit = st.selectbox("Time limit", ["No limit", "10 minutes", "20 minutes", "30 minutes", "45 minutes"], key="quiz_setting_time")
        with row2[2]:
            answer_order = st.selectbox("Order", ["Shuffle", "Keep order"], key="quiz_setting_order")

        render_alert()
        if st.button("Create Quiz", type="primary", use_container_width=True, key="create_quiz_button"):
            if not clean_text(source):
                set_alert("error", "Enter a topic or upload a readable study file.")
                st.rerun()
            prepared = clean_text(source)
            if len(prepared) > 40000:
                prepared = prepared[:40000]
                set_alert("info", "The first 40,000 characters were used because the source was long.")
            try:
                questions = generate_in_batches(
                    source=prepared,
                    total=int(count),
                    difficulty=difficulty,
                    quiz_type=quiz_type,
                    mode=mode,
                    project_generate_quiz=project_generate_quiz,
                    source_kind=source_kind,
                    focus=focus,
                    language=language,
                    instructions=instructions,
                )
                if not questions:
                    raise ValueError("No valid questions were created from the selected source.")
                if answer_order == "Shuffle":
                    for question in questions:
                        choices = question.get("choices", [])
                        if isinstance(choices, list) and len(choices) > 1:
                            random.shuffle(choices)
                if not include_explanations:
                    for question in questions:
                        question["explanation"] = "Explanation disabled for this quiz."
                st.session_state.current_quiz = questions
                st.session_state.quiz_answers = {}
                st.session_state.quiz_topic = source_label
                st.session_state.quiz_difficulty = difficulty
                st.session_state.quiz_type = quiz_type
                st.session_state.quiz_time_limit = time_limit
                st.session_state.quiz_result = None
                st.session_state.quiz_history_saved = False
                st.session_state.quiz_stage = "answer"
                initialize_timer(time_limit)
                set_alert("success", "Quiz created from the selected source.")
                st.rerun()
            except Exception as error:
                message = str(error)
                if mode == "Smart generation" and any(token in message.casefold() for token in ["401", "api key", "expired_api_key"]):
                    set_alert("error", "Smart generation could not authenticate. Update the Groq key or use Built-in practice.")
                else:
                    set_alert("error", f"The quiz could not be created: {message}")
                st.rerun()

    with right:
        analysis = source_analysis(source)
        keywords = analysis.get("keywords", [])
        topics = analysis.get("topics", [])
        characters = len(clean_text(source))
        reading_minutes = max(1, round(characters / 1000)) if characters else 0
        source_type = uploaded.name.rsplit(".", 1)[-1].upper() if uploaded is not None and "." in uploaded.name else "TOPIC"

        st.markdown(f"""
        <div style="margin-bottom:14px;padding:14px 18px;border:1px solid rgba(255,255,255,0.3);border-radius:14px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">
            <div style="margin-bottom:10px;color:#183153;font-size:14px;font-weight:700;"><i class="fas fa-circle-info" style="margin-right:7px;color:#4f8dff;"></i> Source Info</div>
            <div style="display:flex;align-items:center;gap:10px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.3);">
                <span style="padding:6px 7px;border-radius:7px;background:#f0f4fe;color:#4f8dff;font-size:10px;font-weight:800;"><i class="fas fa-file"></i> {html.escape(source_type)}</span>
                <div><strong style="display:block;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#183153;font-size:12px;">{html.escape(source_label)}</strong>
                <small style="display:block;margin-top:2px;color:#7b8797;font-size:10px;">{characters:,} characters</small></div>
            </div>
            <div style="display:flex;justify-content:space-between;gap:10px;padding-top:10px;color:#7b8797;font-size:11px;">
                <span><i class="fas fa-clock" style="width:13px;color:#7b8797;"></i> Reading time</span>
                <strong style="color:#183153;font-size:11px;">{reading_minutes} min</strong>
            </div>
            <div style="display:flex;justify-content:space-between;gap:10px;padding-top:6px;color:#7b8797;font-size:11px;">
                <span><i class="fas fa-signal" style="width:13px;color:#7b8797;"></i> Difficulty</span>
                <strong style="color:#183153;font-size:11px;">{html.escape(difficulty)}</strong>
            </div>
            <div style="display:flex;justify-content:space-between;gap:10px;padding-top:6px;color:#7b8797;font-size:11px;">
                <span><i class="fas fa-list" style="width:13px;color:#7b8797;"></i> Question type</span>
                <strong style="color:#183153;font-size:11px;">{html.escape(quiz_type)}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        topic_html = "".join(f'<span style="padding:3px 7px;border-radius:6px;background:#f0f4fe;color:#4f8dff;font-size:9px;font-weight:600;">{html.escape(str(item))}</span>' for item in topics) or '<span style="color:#b0b8c4;font-size:10px;">No topics found</span>'
        keyword_html = "".join(f'<span style="padding:3px 7px;border-radius:6px;background:#f0f4fe;color:#4f8dff;font-size:9px;font-weight:600;">{html.escape(str(item))}</span>' for item in keywords) or '<span style="color:#b0b8c4;font-size:10px;">No keywords found</span>'
        
        st.markdown(f"""
        <div style="margin-bottom:14px;padding:14px 18px;border:1px solid rgba(255,255,255,0.3);border-radius:14px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">
            <div style="margin-bottom:10px;color:#183153;font-size:14px;font-weight:700;"><i class="fas fa-chart-bar" style="margin-right:7px;color:#4f8dff;"></i> Source Analysis</div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:13px;">
                <div style="padding:9px 5px;border:1px solid rgba(255,255,255,0.3);border-radius:8px;background:rgba(248,250,255,0.6);text-align:center;">
                    <strong style="display:block;color:#4f8dff;font-size:16px;">{analysis.get("word_count", 0)}</strong>
                    <span style="color:#7b8797;font-size:9px;">Words</span>
                </div>
                <div style="padding:9px 5px;border:1px solid rgba(255,255,255,0.3);border-radius:8px;background:rgba(248,250,255,0.6);text-align:center;">
                    <strong style="display:block;color:#4f8dff;font-size:16px;">{analysis.get("topic_count", 0)}</strong>
                    <span style="color:#7b8797;font-size:9px;">Topics</span>
                </div>
                <div style="padding:9px 5px;border:1px solid rgba(255,255,255,0.3);border-radius:8px;background:rgba(248,250,255,0.6);text-align:center;">
                    <strong style="display:block;color:#4f8dff;font-size:16px;">{analysis.get("keyword_count", 0)}</strong>
                    <span style="color:#7b8797;font-size:9px;">Keywords</span>
                </div>
            </div>
            <div style="margin:12px 0 6px;color:#183153;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;"><i class="fas fa-align-left" style="margin-right:5px;"></i> Summary</div>
            <p style="margin:0;color:#7b8797;font-size:12px;line-height:1.5;">{html.escape(str(analysis.get("summary", "")))}</p>
            <div style="margin:12px 0 6px;color:#183153;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;"><i class="fas fa-tags" style="margin-right:5px;"></i> Topics</div>
            <div style="display:flex;flex-wrap:wrap;gap:4px;">{topic_html}</div>
            <div style="margin:12px 0 6px;color:#183153;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;"><i class="fas fa-key" style="margin-right:5px;"></i> Keywords</div>
            <div style="display:flex;flex-wrap:wrap;gap:4px;">{keyword_html}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-bottom:14px;padding:14px 18px;border:1px solid rgba(255,255,255,0.3);border-radius:14px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">
            <div style="margin-bottom:10px;color:#183153;font-size:14px;font-weight:700;"><i class="fas fa-lightbulb" style="margin-right:7px;color:#4f8dff;"></i> How it works</div>
            <div style="display:flex;align-items:flex-start;gap:9px;margin-top:10px;">
                <span style="display:grid;width:21px;height:21px;min-width:21px;place-items:center;border-radius:50%;background:#f0f4fe;color:#4f8dff;font-size:9px;font-weight:800;">1</span>
                <div><strong style="display:block;color:#183153;font-size:11px;">Add source</strong><small style="display:block;margin-top:1px;color:#7b8797;font-size:10px;line-height:1.4;">Enter a topic or upload a file.</small></div>
            </div>
            <div style="display:flex;align-items:flex-start;gap:9px;margin-top:8px;">
                <span style="display:grid;width:21px;height:21px;min-width:21px;place-items:center;border-radius:50%;background:#f0f4fe;color:#4f8dff;font-size:9px;font-weight:800;">2</span>
                <div><strong style="display:block;color:#183153;font-size:11px;">Guide analysis</strong><small style="display:block;margin-top:1px;color:#7b8797;font-size:10px;line-height:1.4;">Choose focus and add instructions.</small></div>
            </div>
            <div style="display:flex;align-items:flex-start;gap:9px;margin-top:8px;">
                <span style="display:grid;width:21px;height:21px;min-width:21px;place-items:center;border-radius:50%;background:#f0f4fe;color:#4f8dff;font-size:9px;font-weight:800;">3</span>
                <div><strong style="display:block;color:#183153;font-size:11px;">Setup quiz</strong><small style="display:block;margin-top:1px;color:#7b8797;font-size:10px;line-height:1.4;">Set difficulty, format and count.</small></div>
            </div>
            <div style="display:flex;align-items:flex-start;gap:9px;margin-top:8px;">
                <span style="display:grid;width:21px;height:21px;min-width:21px;place-items:center;border-radius:50%;background:#f0f4fe;color:#4f8dff;font-size:9px;font-weight:800;">4</span>
                <div><strong style="display:block;color:#183153;font-size:11px;">Review results</strong><small style="display:block;margin-top:1px;color:#7b8797;font-size:10px;line-height:1.4;">Submit answers and download report.</small></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_answer() -> None:
    questions = st.session_state.current_quiz
    if not questions:
        st.session_state.quiz_stage = "setup"
        st.rerun()

    render_steps(5)
    render_alert()
    head_left, head_right = st.columns([4.8, 1.2], vertical_alignment="center")
    with head_left:
        st.markdown(
            f'<div style="display:flex;align-items:flex-end;justify-content:space-between;gap:15px;margin-bottom:15px;">'
            f'<div><h2 style="margin:0;color:#183153;font-size:23px;">{html.escape(st.session_state.quiz_topic)}</h2>'
            f'<p style="margin:4px 0 0;color:#7b8797;font-size:13px;">{len(questions)} questions · {html.escape(st.session_state.quiz_difficulty)} · {html.escape(st.session_state.quiz_type)}</p></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with head_right:
        render_countdown()

    pdf_data = build_pdf(questions, f"Quiz - {st.session_state.quiz_topic}")
    if pdf_data:
        st.download_button(
            "Download questions PDF",
            data=pdf_data,
            file_name="quiz_questions.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    for index, question in enumerate(questions):
        st.markdown(
            f'<div style="margin-bottom:14px;padding:20px 22px 15px;border:1px solid rgba(255,255,255,0.3);border-radius:14px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">'
            f'<div style="display:inline-flex;margin-bottom:10px;padding:4px 8px;border-radius:999px;background:#f0f4fe;color:#4f8dff;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;">Question {index + 1} of {len(questions)}</div>'
            f'<div style="color:#183153;font-size:16px;font-weight:700;line-height:1.55;">{html.escape(str(question.get("question", "")))}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        key = widget_key(index, question)
        q_type = str(question.get("type", "MCQ")).casefold()
        choices = question.get("choices", []) or []
        if "blank" in q_type or not choices:
            st.text_input("Your answer", key=key, label_visibility="collapsed", placeholder="Type your answer")
        else:
            st.radio("Choose an answer", choices, key=key, index=None, label_visibility="collapsed")

    if st.button("Submit answers", type="primary", use_container_width=True):
        answers = collect_answers()
        missing = [str(index + 1) for index in range(len(questions)) if index not in answers]
        if missing:
            set_alert("error", "Answer every question before submitting. Missing: " + ", ".join(missing))
            st.rerun()
        grade_and_finish(auto_submit=False)


def render_result(save_history) -> None:
    questions = st.session_state.current_quiz
    answers = st.session_state.quiz_answers
    result = st.session_state.quiz_result or {"score": 0, "total": len(questions), "percentage": 0}

    render_steps(5)
    render_alert()
    percentage = result["percentage"]
    performance = "Excellent" if percentage >= 80 else "Good" if percentage >= 60 else "Developing" if percentage >= 40 else "Needs review"

    elapsed_seconds = int(result.get("elapsed_seconds", 0))
    elapsed_minutes, elapsed_remainder = divmod(elapsed_seconds, 60)
    elapsed_label = f"{elapsed_minutes:02d}:{elapsed_remainder:02d}"
    answered_count = int(result.get("answered_count", len(answers)))
    unanswered_count = int(result.get("unanswered_count", max(0, len(questions) - answered_count)))

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px;">
        <div style="padding:18px;border:1px solid rgba(255,255,255,0.3);border-radius:14px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);text-align:center;border-top:3px solid #4f8dff;backdrop-filter:blur(12px);">
            <span style="color:#7b8797;font-size:11px;">Score</span>
            <strong style="display:block;margin-top:4px;color:#183153;font-size:23px;">{result["score"]}/{result["total"]}</strong>
        </div>
        <div style="padding:18px;border:1px solid rgba(255,255,255,0.3);border-radius:14px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);text-align:center;border-top:3px solid #27ae60;backdrop-filter:blur(12px);">
            <span style="color:#7b8797;font-size:11px;">Percentage</span>
            <strong style="display:block;margin-top:4px;color:#183153;font-size:23px;">{percentage}%</strong>
        </div>
        <div style="padding:18px;border:1px solid rgba(255,255,255,0.3);border-radius:14px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);text-align:center;border-top:3px solid #fdcb6e;backdrop-filter:blur(12px);">
            <span style="color:#7b8797;font-size:11px;">Time used</span>
            <strong style="display:block;margin-top:4px;color:#183153;font-size:23px;">{elapsed_label}</strong>
        </div>
        <div style="padding:18px;border:1px solid rgba(255,255,255,0.3);border-radius:14px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);text-align:center;border-top:3px solid #6c5ce7;backdrop-filter:blur(12px);">
            <span style="color:#7b8797;font-size:11px;">Performance</span>
            <strong style="display:block;margin-top:4px;color:#183153;font-size:23px;">{performance}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if result.get("auto_submitted"):
        st.warning(
            f"Time expired, so the quiz was submitted automatically. "
            f"{answered_count} answered and {unanswered_count} unanswered question(s). "
            "Every unanswered question was counted as incorrect."
        )
    st.progress(result["score"] / result["total"] if result["total"] else 0)

    if not st.session_state.quiz_history_saved and save_history is not None:
        try:
            save_history(
                username=st.session_state.get("username", "Student"),
                topic=st.session_state.quiz_topic,
                difficulty=st.session_state.quiz_difficulty,
                quiz_type=st.session_state.quiz_type,
                score=result["score"],
                total=result["total"],
                percentage=result["percentage"],
            )
            st.session_state.quiz_history_saved = True
        except Exception as error:
            print("Quiz history save error:", error)

    pdf_data = build_pdf(questions, f"Quiz Result - {st.session_state.quiz_topic} - Time used {elapsed_label}", answers, True)
    if pdf_data:
        st.download_button(
            "Download result PDF",
            data=pdf_data,
            file_name="quiz_result.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.markdown("### Answer review")
    for index, question in enumerate(questions):
        raw_answer = answers.get(index)
        given = clean_text(raw_answer) if raw_answer is not None else "Not answered"
        correct_answer = clean_text(question.get("correct_answer", "Unavailable"))
        correct = raw_answer is not None and clean_text(raw_answer).casefold() == correct_answer.casefold()
        
        if correct:
            border_color = "#27ae60"
            status_label = "Correct"
        else:
            border_color = "#c74855"
            status_label = "Not answered · Incorrect" if raw_answer is None else "Incorrect"
            
        st.markdown(f"""
        <div style="margin:12px 0;padding:18px;border:1px solid rgba(255,255,255,0.3);border-left:4px solid {border_color};border-radius:13px;background:rgba(255,255,255,0.88);box-shadow:0 4px 16px rgba(79,141,255,0.08);backdrop-filter:blur(12px);">
            <h4 style="margin:0 0 8px;color:#183153;font-size:14px;font-weight:700;">Question {index + 1} · {status_label}</h4>
            <p style="margin:5px 0;color:#586176;font-size:13px;line-height:1.55;"><strong>{html.escape(str(question.get("question", "")))}</strong></p>
            <p style="margin:5px 0;color:#586176;font-size:13px;line-height:1.55;">Your answer: {html.escape(given)}</p>
            <p style="margin:5px 0;color:#586176;font-size:13px;line-height:1.55;">Correct answer: {html.escape(correct_answer)}</p>
            <div style="margin-top:10px;padding:11px 13px;border-radius:9px;background:rgba(247,248,251,0.6);color:#4b556a;font-size:12px;line-height:1.55;">{html.escape(str(question.get("explanation", "")))}</div>
        </div>
        """, unsafe_allow_html=True)

    new_col, home_col = st.columns(2)
    with new_col:
        if st.button("Create another quiz", type="primary", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.startswith("quiz_answer_"):
                    st.session_state.pop(key, None)
            st.session_state.current_quiz = []
            st.session_state.quiz_answers = {}
            st.session_state.quiz_result = None
            st.session_state.quiz_deadline = None
            st.session_state.quiz_stage = "setup"
            st.rerun()
    with home_col:
        if st.button("Back to dashboard", use_container_width=True):
            st.session_state.current_page = "home"
            st.session_state.dashboard_action = "home"
            st.session_state.quiz_stage = "setup"
            st.rerun()


def show_quiz_page() -> None:
    initialize_quiz_state()
    render_header()

    if not st.session_state.get("logged_in", False):
        st.warning("Please sign in to use the quiz workspace.")
        return

    save_history, project_generate_quiz, project_extract_text = import_quiz_services()

    if st.session_state.quiz_stage == "setup":
        render_setup(project_generate_quiz, project_extract_text)
    elif st.session_state.quiz_stage == "answer":
        render_answer()
    else:
        render_result(save_history)