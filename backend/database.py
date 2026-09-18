import sqlite3

DATABASE_NAME = "medora.db"


def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()

    # Patient information and current triage status
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            sex TEXT,
            symptoms TEXT,
            disorders TEXT,

            heart_rate INTEGER,
            systolic_bp INTEGER,
            diastolic_bp INTEGER,
            respiratory_rate INTEGER,
            spo2 REAL,
            temperature REAL,

            pain_score INTEGER,
            gcs_score INTEGER,
            arrival_mode TEXT,

            urgency TEXT,
            risk_score REAL,
            risk_factors TEXT,

            created_at TEXT,
            updated_at TEXT
        )
    """)

    # Every assessment is preserved here.
    # This allows MEDORA to show the patient's complete timeline.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id TEXT NOT NULL,

            urgency TEXT,
            risk_score REAL,
            risk_factors TEXT,

            timestamp TEXT,

            FOREIGN KEY (patient_id)
                REFERENCES patients(id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def close_db(conn):
    if conn:
        conn.close()