import sqlite3
from datetime import datetime

DB_NAME = "quiz.db"


def get_connection():

    return sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # Users

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Quiz History

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        topic TEXT,

        difficulty TEXT,

        quiz_type TEXT,

        score INTEGER,

        total INTEGER,

        percentage REAL,

        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_user(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (username,password)
            VALUES (?,?)
            """,
            (
                username,
                password
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def get_user(
        username,
        password
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=?
        AND password=?
        """,
        (
            username,
            password
        )
    )

    result = cursor.fetchone()

    conn.close()

    return result


def save_history(
    username,
    topic,
    difficulty,
    quiz_type,
    score,
    total,
    percentage
):

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO history(

        username,
        topic,
        difficulty,
        quiz_type,
        score,
        total,
        percentage,
        created_at

        )

        VALUES(
        ?,?,?,?,?,?,?,?
        )
        """,

        (
            username,
            topic,
            difficulty,
            quiz_type,
            score,
            total,
            percentage,
            created_at
        )
    )

    conn.commit()

    conn.close()


def get_history(
        username
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
        topic,
        difficulty,
        quiz_type,
        score,
        total,
        percentage,
        created_at

        FROM history

        WHERE username=?

        ORDER BY id DESC
        """,
        (username,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_leaderboard():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

        username,

        SUM(score) as total_score,

        COUNT(*) as quizzes

        FROM history

        GROUP BY username

        ORDER BY total_score DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows
