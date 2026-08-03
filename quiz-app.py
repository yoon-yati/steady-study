import os
import streamlit as st

from database.db_manager import (
    create_tables,
    add_user,
    get_user
)

from groq_service import generate_quiz
from offline_generator import generate_offline_quiz
from file_reader import extract_text

# --------------------------
# SETUP
# --------------------------

st.set_page_config(
    page_title="AI Quiz Master",
    page_icon="🎓",
    layout="wide"
)

create_tables()

# --------------------------
# SESSION
# --------------------------

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "quiz" not in st.session_state:
    st.session_state.quiz = []

if "score" not in st.session_state:
    st.session_state.score = 0

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

if "quiz_topic" not in st.session_state:
    st.session_state.quiz_topic = ""

if "quiz_difficulty" not in st.session_state:
    st.session_state.quiz_difficulty = ""

if "quiz_type" not in st.session_state:
    st.session_state.quiz_type = "Mixed"

# --------------------------
# CSS
# --------------------------

css_path = os.path.join(
    os.path.dirname(__file__),
    "styles.css"
)

if os.path.exists(css_path):
    with open(
        css_path,
        "r",
        encoding="utf-8"
    ) as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True
        )

# --------------------------
# HOME PAGE
# --------------------------


if st.session_state.page == "Home":

    hero_html = (
        '<section class="home-hero">'
        '<div class="home-badge">'
        '✨ AI-Powered Learning Platform'
        '</div>'
        '<h1 class="home-title">'
        'Learn Smarter with '
        '<span>AI Quiz Master</span>'
        '</h1>'
        '<p class="home-description">'
        'Turn your topics, notes, PDF files, Word documents, '
        'PowerPoint presentations, and text files into interactive '
        'quizzes powered by artificial intelligence.'
        '</p>'
        '</section>'
    )

    st.markdown(
        hero_html,
        unsafe_allow_html=True
    )

    button_left, button_right = st.columns(2)

    with button_left:
        if st.button(
            "🚀 Create Free Account",
            key="home_register",
            use_container_width=True
        ):
            st.session_state.page = "Register"
            st.rerun()

    with button_right:
        if st.button(
            "🔐 Login to Continue",
            key="home_login",
            use_container_width=True
        ):
            st.session_state.page = "Login"
            st.rerun()

    features_title = (
        '<section class="home-features-title">'
        '<p>BUILT FOR MODERN LEARNING</p>'
        '<h2>Everything you need to study effectively</h2>'
        '</section>'
    )

    st.markdown(
        features_title,
        unsafe_allow_html=True
    )

    feature_col1, feature_col2, feature_col3 = st.columns(3)

    with feature_col1:
        st.markdown(
            (
                '<div class="feature-card">'
                '<div class="feature-icon purple-icon">🤖</div>'
                '<h3>AI Quiz Generation</h3>'
                '<p>Generate professional questions with Groq AI, '
                'including helpful explanations.</p>'
                '</div>'
            ),
            unsafe_allow_html=True
        )

    with feature_col2:
        st.markdown(
            (
                '<div class="feature-card">'
                '<div class="feature-icon cyan-icon">📚</div>'
                '<h3>Multiple Question Types</h3>'
                '<p>Practise with multiple choice, true or false, '
                'fill-in-the-blank, and mixed quizzes.</p>'
                '</div>'
            ),
            unsafe_allow_html=True
        )

    with feature_col3:
        st.markdown(
            (
                '<div class="feature-card">'
                '<div class="feature-icon pink-icon">📄</div>'
                '<h3>Learn from Your Files</h3>'
                '<p>Upload PDF, Word, PowerPoint, or TXT files and '
                'create quizzes from your own materials.</p>'
                '</div>'
            ),
            unsafe_allow_html=True
        )

    feature_col4, feature_col5, feature_col6 = st.columns(3)

    with feature_col4:
        st.markdown(
            (
                '<div class="feature-card">'
                '<div class="feature-icon green-icon">📊</div>'
                '<h3>Learning Analytics</h3>'
                '<p>Review scores, learning progress, weak topics, '
                'and personalised recommendations.</p>'
                '</div>'
            ),
            unsafe_allow_html=True
        )

    with feature_col5:
        st.markdown(
            (
                '<div class="feature-card">'
                '<div class="feature-icon orange-icon">⚡</div>'
                '<h3>Online and Offline</h3>'
                '<p>Use Groq AI or continue practising with '
                'the built-in Offline mode.</p>'
                '</div>'
            ),
            unsafe_allow_html=True
        )

    with feature_col6:
        st.markdown(
            (
                '<div class="feature-card">'
                '<div class="feature-icon blue-icon">🏆</div>'
                '<h3>Improve Every Day</h3>'
                '<p>Build study streaks, unlock achievements, '
                'and track learning progress.</p>'
                '</div>'
            ),
            unsafe_allow_html=True
        )

    how_it_works_html = (
        '<section class="home-how">'
        '<p class="section-label">HOW IT WORKS</p>'
        '<h2>Start learning in three simple steps</h2>'
        '<div class="steps-row">'
        '<div class="step-item">'
        '<div class="step-number">1</div>'
        '<h3>Create an account</h3>'
        '<p>Register and sign in securely.</p>'
        '</div>'
        '<div class="step-item">'
        '<div class="step-number">2</div>'
        '<h3>Add study material</h3>'
        '<p>Enter a topic or upload your notes.</p>'
        '</div>'
        '<div class="step-item">'
        '<div class="step-number">3</div>'
        '<h3>Complete your quiz</h3>'
        '<p>Answer questions and review explanations.</p>'
        '</div>'
        '</div>'
        '</section>'
        '<footer class="home-footer">'
        '<strong>AI Quiz Master</strong>'
        '<span>Smart learning powered by artificial intelligence.</span>'
        '</footer>'
    )

    st.markdown(
        how_it_works_html,
        unsafe_allow_html=True
    )

# --------------------------
# REGISTER
# --------------------------

# --------------------------
# REGISTER PAGE
# --------------------------

elif st.session_state.page == "Register":

    st.header("Create Account")
    st.caption("Create an account to start generating quizzes.")

    username = st.text_input(
        "Username",
        key="register_username",
        placeholder="Enter at least 3 characters"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="register_password",
        placeholder="Enter at least 8 characters"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        key="register_confirm_password",
        placeholder="Enter your password again"
    )

    if st.button(
        "Create Account",
        key="create_account_button",
        use_container_width=True
    ):
        clean_username = username.strip()

        if len(clean_username) < 3:
            st.error(
                "Username must contain at least 3 characters."
            )

        elif len(password) < 8:
            st.error(
                "Password must contain at least 8 characters."
            )

        elif password != confirm_password:
            st.error("Passwords do not match.")

        else:
            try:
                success = add_user(
                    clean_username,
                    password
                )

                if success is False:
                    st.error("This username already exists.")

                else:
                    st.success(
                        "Registration successful. "
                        "Redirecting to Login..."
                    )

                    st.session_state.page = "Login"
                    st.rerun()

            except Exception as error:
                st.error(
                    f"Could not create the account: {error}"
                )

    register_back_col, register_login_col = st.columns(2)

    with register_back_col:
        if st.button(
            "← Back to Home",
            key="register_back_home",
            use_container_width=True
        ):
            st.session_state.page = "Home"
            st.rerun()

    with register_login_col:
        if st.button(
            "Already have an account?",
            key="register_open_login",
            use_container_width=True
        ):
            st.session_state.page = "Login"
            st.rerun()


# --------------------------
# LOGIN PAGE
# --------------------------

elif st.session_state.page == "Login":

    st.header("Welcome Back")
    st.caption("Login to continue learning.")

    username = st.text_input(
        "Username",
        key="login_username",
        placeholder="Enter your username"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_password",
        placeholder="Enter your password"
    )

    if st.button(
        "Login",
        key="login_button",
        use_container_width=True
    ):
        clean_username = username.strip()

        if not clean_username:
            st.error("Please enter your username.")

        elif not password:
            st.error("Please enter your password.")

        else:
            try:
                user = get_user(
                    clean_username,
                    password
                )

                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = clean_username
                    st.session_state.quiz = []
                    st.session_state.user_answers = {}
                    st.session_state.score = 0
                    st.session_state.page = "QuizSetup"
                    st.rerun()

                else:
                    st.error(
                        "The username or password is incorrect."
                    )

            except Exception as error:
                st.error(f"Login failed: {error}")

    login_back_col, login_register_col = st.columns(2)

    with login_back_col:
        if st.button(
            "← Back to Home",
            key="login_back_home",
            use_container_width=True
        ):
            st.session_state.page = "Home"
            st.rerun()

    with login_register_col:
        if st.button(
            "Create an account",
            key="login_open_register",
            use_container_width=True
        ):
            st.session_state.page = "Register"
            st.rerun()


# --------------------------
# QUIZ SETUP
# --------------------------

elif st.session_state.page == "QuizSetup":

    if not st.session_state.logged_in:
        st.warning("Please log in before creating a quiz.")

        if st.button("Go to Login"):
            st.session_state.page = "Login"
            st.rerun()

        st.stop()

    st.title(f"Welcome, {st.session_state.username} 👋")

    st.caption(
        "Enter a topic or upload study material to generate a quiz."
    )

    text_topic = st.text_input(
        "Enter Topic",
        key="quiz_topic_input",
        placeholder="For example: Python functions, Biology, English grammar"
    )

    uploaded_file = st.file_uploader(
        "Upload Study Material",
        type=["pdf", "docx", "pptx", "txt"],
        key="quiz_file_uploader"
    )

    setup_col1, setup_col2 = st.columns(2)

    with setup_col1:
        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard"],
            key="quiz_difficulty_selector"
        )

    with setup_col2:
        mode = st.radio(
            "Quiz Mode",
            ["AI", "Offline"],
            key="quiz_mode_selector",
            horizontal=True
        )

    question_count = st.slider(
        "Question Count",
        min_value=1,
        max_value=20,
        value=5,
        key="quiz_question_count"
    )

    if st.button(
        "🚀 Generate Quiz",
        key="generate_quiz_button",
        use_container_width=True
    ):

        content = text_topic.strip()
        display_topic = text_topic.strip() or "Uploaded study material"

        if uploaded_file is not None:
            try:
                content = extract_text(uploaded_file)
                display_topic = uploaded_file.name

            except Exception as error:
                st.error(
                    f"Could not read the uploaded file: {error}"
                )
                content = ""

        if not content or not content.strip():
            st.error(
                "Please enter a topic or upload a supported file."
            )

        else:
            content = content.strip()

            if len(content) > 3000:
                content = content[:3000]

                st.warning(
                    "The uploaded document is large. "
                    "Only the first 3,000 characters will be used."
                )

            try:
                with st.spinner("Generating your quiz..."):

                    if mode == "Offline":
                        quiz = generate_offline_quiz(
                            content,
                            int(question_count),
                            difficulty,
                            "Mixed"
                        )

                    else:
                        quiz = generate_quiz(
                            content,
                            int(question_count),
                            difficulty,
                            "Mixed"
                        )

                if not isinstance(quiz, list) or not quiz:
                    st.error(
                        "No questions were generated. "
                        "Try Offline mode, a shorter topic, "
                        "or a smaller document."
                    )

                else:
                    valid_quiz = []

                    for question in quiz:

                        if not isinstance(question, dict):
                            continue

                        question_text = question.get("question")
                        correct_answer = question.get("correct_answer")

                        if not question_text or correct_answer is None:
                            continue

                        question.setdefault("choices", [])
                        question.setdefault(
                            "explanation",
                            "No explanation was provided."
                        )

                        valid_quiz.append(question)

                    if not valid_quiz:
                        st.error(
                            "The generated questions were in an "
                            "invalid format. Please try again."
                        )

                    else:
                        st.session_state.quiz = valid_quiz
                        st.session_state.user_answers = {}
                        st.session_state.score = 0
                        st.session_state.quiz_topic = display_topic
                        st.session_state.quiz_difficulty = difficulty
                        st.session_state.quiz_type = "Mixed"
                        st.session_state.page = "AnswerQuiz"
                        st.rerun()

            except Exception as error:
                st.error(
                    f"Quiz generation failed: {error}"
                )

                if mode == "AI":
                    st.info(
                        "Check your Groq API key or try Offline mode."
                    )

    navigation_col1, navigation_col2 = st.columns(2)

    with navigation_col1:
        if st.button(
            "← Home",
            key="quiz_setup_home",
            use_container_width=True
        ):
            st.session_state.page = "Home"
            st.rerun()

    with navigation_col2:
        if st.button(
            "🚪 Logout",
            key="quiz_setup_logout",
            use_container_width=True
        ):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.quiz = []
            st.session_state.user_answers = {}
            st.session_state.score = 0
            st.session_state.page = "Home"
            st.rerun()

# --------------------------

# --------------------------
# ANSWER QUIZ
# --------------------------

elif st.session_state.page == "AnswerQuiz":

    quiz = st.session_state.quiz

    if not quiz:
        st.error("No quiz questions are available.")

        if st.button("Return to Quiz Setup"):
            st.session_state.page = "QuizSetup"
            st.rerun()

        st.stop()

    total_questions = len(quiz)

    st.title("📝 Answer the Quiz")

    st.caption(
        "Answer every question and then select Submit Quiz. "
        "Correct answers and explanations will appear only after submission."
    )

    answers = dict(st.session_state.user_answers)

    with st.form("quiz_form"):

        for index, question in enumerate(quiz):

            st.markdown("---")

            st.subheader(
                f"Question {index + 1} of {total_questions}"
            )

            question_text = str(
                question.get("question", "Question unavailable")
            )

            question_type = str(
                question.get("type", "MCQ")
            ).lower().replace("_", "").replace("/", "").replace(" ", "")

            choices = question.get("choices", [])

            normalized_choices = [
                str(choice).strip().lower()
                for choice in choices
            ]

            is_true_false = (
                "truefalse" in question_type
                or (
                    len(normalized_choices) == 2
                    and set(normalized_choices) == {"true", "false"}
                )
            )

            is_fill_blank = (
                "fillblank" in question_type
                or "blank" in question_type
                or "____" in question_text
            )

            if is_fill_blank and not choices:
                answers[index] = st.text_input(
                    question_text,
                    key=f"answer_text_{index}",
                    placeholder="Type your answer"
                )

            elif is_true_false:
                answers[index] = st.radio(
                    question_text,
                    ["True", "False"],
                    index=None,
                    key=f"answer_tf_{index}"
                )

            elif choices:
                answers[index] = st.radio(
                    question_text,
                    choices,
                    index=None,
                    key=f"answer_choice_{index}"
                )

            else:
                answers[index] = st.text_input(
                    question_text,
                    key=f"answer_fallback_{index}",
                    placeholder="Type your answer"
                )

        submitted = st.form_submit_button(
            "✅ Submit Quiz",
            use_container_width=True
        )

    if submitted:

        unanswered_questions = []

        for index in range(total_questions):
            answer = answers.get(index)

            if answer is None or not str(answer).strip():
                unanswered_questions.append(index + 1)

        if unanswered_questions:
            question_numbers = ", ".join(
                str(number)
                for number in unanswered_questions
            )

            st.error(
                "Please answer every question. "
                f"Unanswered question(s): {question_numbers}"
            )

        else:
            score = 0

            for index, question in enumerate(quiz):

                student_answer = str(
                    answers[index]
                ).strip().casefold()

                correct_answer = str(
                    question.get("correct_answer", "")
                ).strip().casefold()

                if student_answer == correct_answer:
                    score += 1

            st.session_state.user_answers = answers
            st.session_state.score = score
            st.session_state.page = "Result"
            st.rerun()
# --------------------------
# RESULT
# --------------------------

# --------------------------
# RESULT
# --------------------------

elif st.session_state.page == "Result":

    quiz = st.session_state.quiz
    answers = st.session_state.user_answers

    total = len(quiz)
    score = st.session_state.score

    if total == 0:
        st.error("No quiz result is available.")

        if st.button("Return to Quiz Setup"):
            st.session_state.page = "QuizSetup"
            st.rerun()

        st.stop()

    percentage = round((score / total) * 100, 2)

    st.title("🎉 Quiz Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Score", f"{score}/{total}")

    with col2:
        st.metric("Percentage", f"{percentage}%")

    with col3:
        if percentage >= 80:
            performance = "Excellent"
        elif percentage >= 60:
            performance = "Good"
        elif percentage >= 40:
            performance = "Keep Practising"
        else:
            performance = "Needs Revision"

        st.metric("Performance", performance)

    st.progress(
        score / total,
        text=f"{score} correct out of {total}"
    )

    st.markdown("---")
    st.header("📚 Answer Review")

    for index, question in enumerate(quiz):

        student_answer = str(
            answers.get(index, "No answer")
        ).strip()

        correct_answer = str(
            question.get("correct_answer", "Unavailable")
        ).strip()

        explanation = str(
            question.get(
                "explanation",
                "No explanation was provided."
            )
        )

        is_correct = (
            student_answer.casefold()
            == correct_answer.casefold()
        )

        if is_correct:
            st.success(
                f"✅ Question {index + 1}: Correct"
            )
        else:
            st.error(
                f"❌ Question {index + 1}: Incorrect"
            )

        st.markdown(
            f"**Question:** {question.get('question', '')}"
        )

        st.markdown(
            f"**Your answer:** {student_answer}"
        )

        st.markdown(
            f"**Correct answer:** {correct_answer}"
        )

        st.info(
            f"💡 Explanation: {explanation}"
        )

        st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🔄 Generate New Quiz",
            use_container_width=True
        ):
            st.session_state.quiz = []
            st.session_state.user_answers = {}
            st.session_state.score = 0
            st.session_state.page = "QuizSetup"
            st.rerun()

    with col2:
        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.quiz = []
            st.session_state.user_answers = {}
            st.session_state.score = 0
            st.session_state.page = "Home"
            st.rerun()