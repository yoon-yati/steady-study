import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# This file is located in the project root.
PROJECT_ROOT = Path(__file__).resolve().parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()


def validate_api_key():
    """
    Validate that a plausible Groq API key was loaded.

    The complete key is never displayed.
    """

    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Add it to the .env file in the project root."
        )

    if not GROQ_API_KEY.startswith("gsk_"):
        raise ValueError(
            "GROQ_API_KEY has an invalid format. "
            "Create a new key in GroqCloud."
        )

    if len(GROQ_API_KEY) < 20:
        raise ValueError(
            "GROQ_API_KEY appears incomplete. "
            "Copy the complete key from GroqCloud."
        )


validate_api_key()

client = Groq(
    api_key=GROQ_API_KEY
)


def clean_json_response(content):
    """
    Remove Markdown code fences and extract the JSON array.
    """

    if not content:
        raise ValueError("Groq returned an empty response.")

    cleaned = content.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned
    )

    array_start = cleaned.find("[")
    array_end = cleaned.rfind("]")

    if array_start == -1 or array_end == -1:
        raise ValueError(
            "Groq did not return a valid JSON array."
        )

    cleaned = cleaned[array_start:array_end + 1]

    return json.loads(cleaned)


def normalize_question(question):
    """
    Convert different AI question formats into one standard format.
    """

    if not isinstance(question, dict):
        return None

    question_text = str(
        question.get("question", "")
    ).strip()

    correct_answer = str(
        question.get("correct_answer", "")
    ).strip()

    explanation = str(
        question.get(
            "explanation",
            "No explanation was provided."
        )
    ).strip()

    question_type = str(
        question.get("type", "MCQ")
    ).strip()

    choices = question.get("choices", [])

    if not isinstance(choices, list):
        choices = []

    choices = [
        str(choice).strip()
        for choice in choices
        if str(choice).strip()
    ]

    if not question_text or not correct_answer:
        return None

    normalized_type = (
        question_type
        .lower()
        .replace("_", "")
        .replace("-", "")
        .replace("/", "")
        .replace(" ", "")
    )

    if "truefalse" in normalized_type:
        question_type = "TrueFalse"
        choices = ["True", "False"]

    elif "fillblank" in normalized_type or "blank" in normalized_type:
        question_type = "FillBlank"

    else:
        question_type = "MCQ"

    return {
        "type": question_type,
        "question": question_text,
        "choices": choices,
        "correct_answer": correct_answer,
        "explanation": explanation
    }


def generate_quiz(
    source_text,
    question_count,
    difficulty,
    quiz_type="Mixed"
):
    """
    Generate a professional quiz using Groq.
    """

    source_text = str(source_text).strip()

    if not source_text:
        raise ValueError(
            "The topic or source material cannot be empty."
        )

    question_count = max(
        1,
        min(int(question_count), 20)
    )

    # Avoid exceeding the model's request limit.
    source_text = source_text[:3000]

    prompt = f"""
Create exactly {question_count} high-quality educational quiz questions.

SOURCE MATERIAL:
{source_text}

DIFFICULTY:
{difficulty}

QUESTION FORMAT:
{quiz_type}

If the format is Mixed, include a balanced combination of:
- Multiple-choice questions
- True-or-false questions
- Fill-in-the-blank questions

Rules:
1. Questions must be based only on the supplied source material.
2. Avoid repeated or nearly identical questions.
3. MCQ questions must have exactly four plausible choices.
4. True-or-false questions must use ["True", "False"].
5. Fill-in-the-blank questions may have an empty choices list.
6. Every question must include the exact correct answer.
7. Every question must include a short educational explanation.
8. Match the requested difficulty.
9. Return only a valid JSON array.
10. Do not include Markdown or introductory text.

Required JSON structure:
[
  {{
    "type": "MCQ",
    "question": "Question text",
    "choices": ["Choice 1", "Choice 2", "Choice 3", "Choice 4"],
    "correct_answer": "Exact correct choice",
    "explanation": "Short educational explanation"
  }},
  {{
    "type": "TrueFalse",
    "question": "Statement",
    "choices": ["True", "False"],
    "correct_answer": "True",
    "explanation": "Short educational explanation"
  }},
  {{
    "type": "FillBlank",
    "question": "Complete this sentence: Python is a ____ language.",
    "choices": [],
    "correct_answer": "programming",
    "explanation": "Short educational explanation"
  }}
]
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert educational assessment designer. "
                    "Return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.25,
        max_tokens=4000
    )

    content = response.choices[0].message.content

    raw_quiz = clean_json_response(content)

    normalized_quiz = []

    for question in raw_quiz:
        normalized = normalize_question(question)

        if normalized is not None:
            normalized_quiz.append(normalized)

    if not normalized_quiz:
        raise ValueError(
            "Groq returned no valid quiz questions."
        )

    return normalized_quiz[:question_count]
print(
    "Groq key loaded:",
    bool(GROQ_API_KEY),
    "Prefix:",
    GROQ_API_KEY[:4] if GROQ_API_KEY else "missing",
    "Length:",
    len(GROQ_API_KEY)
)