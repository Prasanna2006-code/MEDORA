import sqlite3
from pathlib import Path


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "medora.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)

    # Return rows as dictionary-like objects
    conn.row_factory = sqlite3.Row

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():

    conn = get_db()

    # --------------------------------------------------------
    # PATIENTS
    # --------------------------------------------------------

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

            status TEXT DEFAULT 'Waiting',

            is_unidentified INTEGER DEFAULT 0,

            created_at TEXT,
            updated_at TEXT
        )
    """)


    # --------------------------------------------------------
    # ASSESSMENTS / REASSESSMENT HISTORY
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS assessments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id TEXT NOT NULL,

            urgency TEXT,
            risk_score REAL,
            risk_factors TEXT,

            heart_rate INTEGER,
            systolic_bp INTEGER,
            diastolic_bp INTEGER,
            respiratory_rate INTEGER,

            spo2 REAL,
            temperature REAL,

            pain_score INTEGER,
            gcs_score INTEGER,

            symptoms TEXT,

            timestamp TEXT,

            FOREIGN KEY (patient_id)
                REFERENCES patients(id)
                ON DELETE CASCADE
        )
    """)


    # --------------------------------------------------------
    # UNIDENTIFIED PATIENTS
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS unidentified_patients (

            id TEXT PRIMARY KEY,

            temporary_name TEXT DEFAULT 'Unknown Patient',

            estimated_age INTEGER,
            sex TEXT,

            identifying_notes TEXT,

            patient_id TEXT,

            created_at TEXT,
            updated_at TEXT,

            FOREIGN KEY (patient_id)
                REFERENCES patients(id)
                ON DELETE SET NULL
        )
    """)


    # --------------------------------------------------------
    # SYSTEM ALERTS
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id TEXT,

            alert_type TEXT,
            message TEXT,

            severity TEXT DEFAULT 'Normal',

            is_read INTEGER DEFAULT 0,

            created_at TEXT,

            FOREIGN KEY (patient_id)
                REFERENCES patients(id)
                ON DELETE CASCADE
        )
    """)


    # --------------------------------------------------------
    # INDEXES
    # --------------------------------------------------------

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_patients_urgency
        ON patients(urgency)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_patients_status
        ON patients(status)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_assessments_patient
        ON assessments(patient_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_alerts_patient
        ON alerts(patient_id)
    """)


    conn.commit()
    conn.close()


# ============================================================
# CLOSE DATABASE
# ============================================================

def close_db(conn):

    if conn:
        conn.close()


# ============================================================
# DATABASE HEALTH CHECK
# ============================================================

def database_health():

    try:

        conn = get_db()

        conn.execute("SELECT 1")

        conn.close()

        return True

    except Exception:

        return False

