"""
Offline quiz generator for Steady Study.

This module generates concise questions from:
- A manually entered topic
- Extracted PDF text
- Extracted DOCX text
- Extracted PPTX text
- Extracted TXT text

Supported question types:
- MCQ
- True/False
- Fill Blank
- Mixed
"""

import random
import re
from typing import Dict, List


MIN_QUESTION_COUNT = 1
MAX_QUESTION_COUNT = 100

MAX_TOPIC_LENGTH = 60
MAX_QUESTION_LENGTH = 190
MAX_CHOICE_LENGTH = 145


STOP_WORDS = {
    "about",
    "after",
    "again",
    "against",
    "also",
    "because",
    "before",
    "being",
    "been",
    "between",
    "could",
    "does",
    "during",
    "each",
    "from",
    "have",
    "information",
    "into",
    "material",
    "more",
    "most",
    "other",
    "over",
    "study",
    "such",
    "than",
    "that",
    "their",
    "there",
    "these",
    "they",
    "this",
    "through",
    "under",
    "using",
    "very",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "with",
    "would",
}


def clean_text(value: object) -> str:
    """
    Convert a value into clean single-spaced text.
    """

    text = str(value or "")

    # Remove null characters that can appear in extracted files.
    text = text.replace("\x00", " ")

    # Replace repeated whitespace and line breaks.
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def shorten_text(
    value: object,
    maximum_length: int
) -> str:
    """
    Shorten text without cutting through the final word.
    """

    text = clean_text(value)

    if len(text) <= maximum_length:
        return text

    shortened = text[
        :maximum_length
    ].rsplit(
        " ",
        1
    )[0]

    shortened = shortened.rstrip(
        " ,;:-"
    )

    if not shortened:
        shortened = text[:maximum_length]

    return shortened + "..."


def extract_topic(
    source_text: object
) -> str:
    """
    Generate a short topic from manually entered text
    or an uploaded document.

    The complete uploaded document is never used as
    the topic.
    """

    text = clean_text(source_text)

    if not text:
        return "the selected subject"

    first_part = re.split(
        r"[.!?;:\n]",
        text,
        maxsplit=1
    )[0].strip()

    words = first_part.split()

    if len(words) > 7:
        first_part = " ".join(
            words[:7]
        )

    first_part = shorten_text(
        first_part,
        MAX_TOPIC_LENGTH
    )

    if not first_part:
        return "the selected subject"

    return first_part


def split_into_sentences(
    source_text: object
) -> List[str]:
    """
    Split extracted document text into short,
    usable sentences.

    Long paragraphs are shortened before being used.
    """

    text = clean_text(source_text)

    if not text:
        return []

    raw_sentences = re.split(
        r"(?<=[.!?])\s+|[\r\n]+",
        text
    )

    sentences: List[str] = []
    seen_sentences = set()

    for raw_sentence in raw_sentences:

        sentence = clean_text(
            raw_sentence
        )

        sentence = sentence.strip(
            "-• \t"
        )

        # Ignore very short fragments.
        if len(sentence) < 25:
            continue

        sentence = shorten_text(
            sentence,
            MAX_CHOICE_LENGTH
        )

        identity = sentence.casefold()

        if identity in seen_sentences:
            continue

        seen_sentences.add(identity)
        sentences.append(sentence)

    return sentences


def extract_important_words(
    sentence: str
) -> List[str]:
    """
    Extract useful words for fill-in-the-blank
    questions.
    """

    words = re.findall(
        r"\b[A-Za-z][A-Za-z'-]{4,}\b",
        sentence
    )

    important: List[str] = []
    seen = set()

    for word in words:

        lowered = word.casefold()

        if lowered in STOP_WORDS:
            continue

        if lowered in seen:
            continue

        seen.add(lowered)
        important.append(word)

    return important


def normalize_quiz_type(
    quiz_type: object
) -> str:
    """
    Convert different UI labels into standard names.
    """

    normalized = re.sub(
        r"[^a-z]",
        "",
        str(
            quiz_type or "Mixed"
        ).casefold()
    )

    if normalized == "mcq":
        return "mcq"

    if normalized in {
        "truefalse",
        "trueorfalse"
    }:
        return "truefalse"

    if normalized in {
        "fillblank",
        "fillintheblank",
        "blank"
    }:
        return "fillblank"

    return "mixed"


def create_mcq(
    sentence: str,
    topic: str,
    question_number: int
) -> Dict[str, object]:
    """
    Create a concise multiple-choice question.
    """

    correct_answer = shorten_text(
        sentence,
        MAX_CHOICE_LENGTH
    )

    wrong_answers = [
        shorten_text(
            (
                f"The source states that {topic} "
                "has no practical importance."
            ),
            MAX_CHOICE_LENGTH
        ),
        shorten_text(
            (
                f"The source presents an unrelated "
                f"claim about {topic}."
            ),
            MAX_CHOICE_LENGTH
        ),
        shorten_text(
            (
                "The study material provides no "
                "information supporting this statement."
            ),
            MAX_CHOICE_LENGTH
        )
    ]

    choices = [
        correct_answer,
        *wrong_answers
    ]

    # Use a local predictable randomizer.
    randomizer = random.Random(
        question_number + len(topic)
    )

    randomizer.shuffle(choices)

    return {
        "type": "MCQ",

        "question": shorten_text(
            (
                "Which statement is supported by the "
                f"study material about {topic}?"
            ),
            MAX_QUESTION_LENGTH
        ),

        "choices": choices,

        "correct_answer": correct_answer,

        "explanation": (
            "The correct option is based directly "
            "on the supplied study material."
        )
    }


def create_true_false(
    sentence: str,
    topic: str,
    question_number: int
) -> Dict[str, object]:
    """
    Create a concise True or False question.
    """

    if question_number % 2 == 0:

        question_text = shorten_text(
            sentence,
            MAX_QUESTION_LENGTH
        )

        correct_answer = "True"

        explanation = (
            "This statement is supported by the "
            "supplied study material."
        )

    else:

        question_text = shorten_text(
            (
                "The supplied material contains no "
                f"meaningful information about {topic}."
            ),
            MAX_QUESTION_LENGTH
        )

        correct_answer = "False"

        explanation = (
            "The supplied material contains information "
            f"related to {topic}."
        )

    return {
        "type": "TrueFalse",

        "question": question_text,

        "choices": [
            "True",
            "False"
        ],

        "correct_answer": correct_answer,

        "explanation": explanation
    }


def create_fill_blank(
    sentence: str,
    topic: str,
    question_number: int
) -> Dict[str, object]:
    """
    Create a short fill-in-the-blank question.
    """

    candidates = extract_important_words(
        sentence
    )

    if not candidates:

        return {
            "type": "FillBlank",

            "question": (
                "Complete the sentence: "
                "The main subject is ______."
            ),

            "choices": [],

            "correct_answer": topic,

            "explanation": (
                "The answer is based on the main "
                "subject of the supplied material."
            )
        }

    answer = candidates[
        question_number % len(candidates)
    ]

    blank_sentence = re.sub(
        rf"\b{re.escape(answer)}\b",
        "______",
        sentence,
        count=1,
        flags=re.IGNORECASE
    )

    blank_sentence = shorten_text(
        blank_sentence,
        MAX_QUESTION_LENGTH
    )

    return {
        "type": "FillBlank",

        "question": blank_sentence,

        "choices": [],

        "correct_answer": answer,

        "explanation": (
            f'The missing word is "{answer}", based '
            "on the supplied study material."
        )
    }


def create_fallback_question(
    topic: str,
    question_number: int,
    difficulty: str
) -> Dict[str, object]:
    """
    Create a short fallback question when the
    source contains too few usable sentences.
    """

    return {
        "type": "TrueFalse",

        "question": (
            f"Regular review can improve understanding "
            f"of {topic}."
        ),

        "choices": [
            "True",
            "False"
        ],

        "correct_answer": "True",

        "explanation": (
            "Regular review and practice generally "
            "improve understanding and recall."
        ),

        "difficulty": difficulty,

        "number": question_number + 1
    }


def generate_offline_quiz(
    source_text: object,
    question_count: int,
    difficulty: str = "Medium",
    quiz_type: str = "Mixed"
) -> List[Dict[str, object]]:
    """
    Generate concise offline quiz questions.

    Parameters:
        source_text:
            A manually entered topic or extracted
            PDF/DOCX/PPTX/TXT content.

        question_count:
            Number of questions from 1 to 100.

        difficulty:
            Easy, Medium, or Hard.

        quiz_type:
            MCQ, True/False, Fill Blank, or Mixed.

    Returns:
        A list of quiz question dictionaries.
    """

    try:
        count = int(
            question_count
        )

    except (
        TypeError,
        ValueError
    ):
        count = 5

    count = max(
        MIN_QUESTION_COUNT,
        min(
            count,
            MAX_QUESTION_COUNT
        )
    )

    topic = extract_topic(
        source_text
    )

    sentences = split_into_sentences(
        source_text
    )

    if not sentences:

        sentences = [
            (
                f"{topic} is the main subject of "
                "the supplied study material."
            )
        ]

    selected_type = normalize_quiz_type(
        quiz_type
    )

    questions: List[
        Dict[str, object]
    ] = []

    for index in range(count):

        sentence = sentences[
            index % len(sentences)
        ]

        if selected_type == "mcq":

            question = create_mcq(
                sentence,
                topic,
                index
            )

        elif selected_type == "truefalse":

            question = create_true_false(
                sentence,
                topic,
                index
            )

        elif selected_type == "fillblank":

            question = create_fill_blank(
                sentence,
                topic,
                index
            )

        else:

            question_position = index % 3

            if question_position == 0:

                question = create_mcq(
                    sentence,
                    topic,
                    index
                )

            elif question_position == 1:

                question = create_true_false(
                    sentence,
                    topic,
                    index
                )

            else:

                question = create_fill_blank(
                    sentence,
                    topic,
                    index
                )

        question["difficulty"] = difficulty
        question["number"] = index + 1

        questions.append(question)

    # Ensure the requested count is always returned.
    while len(questions) < count:

        questions.append(
            create_fallback_question(
                topic,
                len(questions),
                difficulty
            )
        )

    return questions[:count]


# Compatibility alias for old code.
generate_quiz_offline = generate_offline_quiz