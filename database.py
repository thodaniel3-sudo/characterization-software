import sqlite3
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "mwcnt_characterization.db"


def get_connection():
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_name TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS characterization_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id INTEGER,
            technique TEXT NOT NULL,
            parameter TEXT NOT NULL,
            value REAL,
            unit TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (sample_id)
                REFERENCES samples(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_type TEXT NOT NULL,
            result_summary TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_name TEXT NOT NULL,
            file_path TEXT,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def create_sample(sample_name, description=""):
    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat(timespec="seconds")

    cursor.execute("""
        INSERT INTO samples (
            sample_name,
            description,
            created_at
        )
        VALUES (?, ?, ?)
    """, (
        sample_name,
        description,
        created_at
    ))

    sample_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return sample_id


def get_samples():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM samples
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_sample(sample_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM samples
        WHERE id = ?
    """, (sample_id,))

    row = cursor.fetchone()

    connection.close()

    return dict(row) if row else None


def save_characterization_result(
    sample_id,
    technique,
    parameter,
    value,
    unit="",
    notes=""
):
    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat(timespec="seconds")

    cursor.execute("""
        INSERT INTO characterization_results (
            sample_id,
            technique,
            parameter,
            value,
            unit,
            notes,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        sample_id,
        technique,
        parameter,
        value,
        unit,
        notes,
        created_at
    ))

    result_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return result_id


def get_characterization_results(sample_id=None):
    connection = get_connection()
    cursor = connection.cursor()

    if sample_id is None:
        cursor.execute("""
            SELECT *
            FROM characterization_results
            ORDER BY id DESC
        """)
    else:
        cursor.execute("""
            SELECT *
            FROM characterization_results
            WHERE sample_id = ?
            ORDER BY id DESC
        """, (sample_id,))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def save_analysis_history(
    analysis_type,
    result_summary
):
    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat(timespec="seconds")

    cursor.execute("""
        INSERT INTO analysis_history (
            analysis_type,
            result_summary,
            created_at
        )
        VALUES (?, ?, ?)
    """, (
        analysis_type,
        result_summary,
        created_at
    ))

    analysis_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return analysis_id


def get_analysis_history(limit=50):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM analysis_history
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def save_report(report_name, file_path):
    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat(timespec="seconds")

    cursor.execute("""
        INSERT INTO reports (
            report_name,
            file_path,
            created_at
        )
        VALUES (?, ?, ?)
    """, (
        report_name,
        str(file_path),
        created_at
    ))

    report_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return report_id


def get_reports():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM reports
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def clear_analysis_history():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM analysis_history
    """)

    connection.commit()
    connection.close()


def database_exists():
    return DATABASE_PATH.exists()


if __name__ == "__main__":
    initialize_database()

    print("MWCNT characterization database initialized.")
    print(f"Database: {DATABASE_PATH}")