from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import datetime
import uuid
from schemas import PatientInput
from triage import calculate_triage

app = FastAPI(title="MEDORA", version="1.0")

# Allow frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "medora.db"


# -------------------------
# DATABASE
# -------------------------

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            name TEXT,
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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            urgency TEXT,
            risk_score REAL,
            risk_factors TEXT,
            timestamp TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    """)

    conn.commit()
    conn.close()


init_db()


# -------------------------
# INPUT SCHEMA
# -------------------------

class PatientInput(BaseModel):
    name: str = "Unknown"
    age: int
    sex: str
    symptoms: str
    disorders: str = ""

    heart_rate: int
    systolic_bp: int
    diastolic_bp: int
    respiratory_rate: int
    spo2: float
    temperature: float

    pain_score: int
    gcs_score: int

    arrival_mode: str = "Walk-in"


# -------------------------
# TRIAGE ENGINE
# -------------------------

def calculate_triage(patient):
    score = 0
    risk_factors = []

    # Oxygen
    if patient.spo2 < 90:
        score += 5
        risk_factors.append("Severely low SpO₂")
    elif patient.spo2 < 94:
        score += 3
        risk_factors.append("Low SpO₂")

    # Heart rate
    if patient.heart_rate > 120:
        score += 3
        risk_factors.append("High heart rate")
    elif patient.heart_rate < 50:
        score += 3
        risk_factors.append("Low heart rate")

    # Respiratory rate
    if patient.respiratory_rate > 30:
        score += 4
        risk_factors.append("High respiratory rate")
    elif patient.respiratory_rate < 10:
        score += 4
        risk_factors.append("Low respiratory rate")

    # Blood pressure
    if patient.systolic_bp < 90:
        score += 5
        risk_factors.append("Low systolic blood pressure")

    if patient.systolic_bp > 180:
        score += 4
        risk_factors.append("Very high systolic blood pressure")

    # Temperature
    if patient.temperature >= 39.5:
        score += 3
        risk_factors.append("High temperature")

    # GCS
    if patient.gcs_score < 9:
        score += 6
        risk_factors.append("Severely reduced GCS")
    elif patient.gcs_score < 13:
        score += 4
        risk_factors.append("Reduced GCS")

    # Pain
    if patient.pain_score >= 8:
        score += 2
        risk_factors.append("Severe pain")

    # Age
    if patient.age >= 75:
        score += 2
        risk_factors.append("Advanced age")
    elif patient.age <= 5:
        score += 2
        risk_factors.append("Very young age")

    # Arrival mode
    if patient.arrival_mode.lower() == "ambulance":
        score += 1
        risk_factors.append("Arrived by ambulance")

    # Symptoms
    symptoms = patient.symptoms.lower()

    emergency_keywords = [
        "chest pain",
        "difficulty breathing",
        "shortness of breath",
        "unconscious",
        "seizure",
        "severe bleeding",
        "stroke",
        "paralysis"
    ]

    for keyword in emergency_keywords:
        if keyword in symptoms:
            score += 5
            risk_factors.append(f"Warning symptom: {keyword}")
            break

    # Final urgency
    if score >= 8:
        urgency = "Critical"
    elif score >= 4:
        urgency = "Urgent"
    else:
        urgency = "Non-urgent"

    return urgency, score, risk_factors


# -------------------------
# CREATE PATIENT
# -------------------------

@app.post("/patients")
def create_patient(patient: PatientInput):

    patient_id = "MED-" + uuid.uuid4().hex[:6].upper()
    now = datetime.now().isoformat()

    urgency, risk_score, risk_factors = calculate_triage(patient)

    conn = get_db()

    conn.execute("""
        INSERT INTO patients (
            id, name, age, sex, symptoms, disorders,
            heart_rate, systolic_bp, diastolic_bp,
            respiratory_rate, spo2, temperature,
            pain_score, gcs_score, arrival_mode,
            urgency, risk_score, risk_factors,
            created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        patient.name,
        patient.age,
        patient.sex,
        patient.symptoms,
        patient.disorders,
        patient.heart_rate,
        patient.systolic_bp,
        patient.diastolic_bp,
        patient.respiratory_rate,
        patient.spo2,
        patient.temperature,
        patient.pain_score,
        patient.gcs_score,
        patient.arrival_mode,
        urgency,
        risk_score,
        ", ".join(risk_factors),
        now,
        now
    ))

    conn.execute("""
        INSERT INTO assessments (
            patient_id,
            urgency,
            risk_score,
            risk_factors,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        patient_id,
        urgency,
        risk_score,
        ", ".join(risk_factors),
        now
    ))

    conn.commit()
    conn.close()

    return {
        "patient_id": patient_id,
        "urgency": urgency,
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "timestamp": now
    }


# -------------------------
# GET ALL PATIENTS
# -------------------------

@app.get("/patients")
def get_patients():

    conn = get_db()

    patients = conn.execute("""
        SELECT *
        FROM patients
        ORDER BY
            CASE urgency
                WHEN 'Critical' THEN 1
                WHEN 'Urgent' THEN 2
                WHEN 'Non-urgent' THEN 3
            END,
            updated_at DESC
    """).fetchall()

    conn.close()

    return [dict(patient) for patient in patients]


# -------------------------
# GET ONE PATIENT
# -------------------------

@app.get("/patients/{patient_id}")
def get_patient(patient_id: str):

    conn = get_db()

    patient = conn.execute(
        "SELECT * FROM patients WHERE id = ?",
        (patient_id,)
    ).fetchone()

    conn.close()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return dict(patient)


# -------------------------
# REASSESS PATIENT
# -------------------------

@app.put("/patients/{patient_id}/reassess")
def reassess_patient(
    patient_id: str,
    patient: PatientInput
):

    conn = get_db()

    existing = conn.execute(
        "SELECT * FROM patients WHERE id = ?",
        (patient_id,)
    ).fetchone()

    if not existing:
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    urgency, risk_score, risk_factors = calculate_triage(patient)

    now = datetime.now().isoformat()

    conn.execute("""
        UPDATE patients
        SET
            name = ?,
            age = ?,
            sex = ?,
            symptoms = ?,
            disorders = ?,
            heart_rate = ?,
            systolic_bp = ?,
            diastolic_bp = ?,
            respiratory_rate = ?,
            spo2 = ?,
            temperature = ?,
            pain_score = ?,
            gcs_score = ?,
            arrival_mode = ?,
            urgency = ?,
            risk_score = ?,
            risk_factors = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        patient.name,
        patient.age,
        patient.sex,
        patient.symptoms,
        patient.disorders,
        patient.heart_rate,
        patient.systolic_bp,
        patient.diastolic_bp,
        patient.respiratory_rate,
        patient.spo2,
        patient.temperature,
        patient.pain_score,
        patient.gcs_score,
        patient.arrival_mode,
        urgency,
        risk_score,
        ", ".join(risk_factors),
        now,
        patient_id
    ))

    # Preserve previous assessment
    conn.execute("""
        INSERT INTO assessments (
            patient_id,
            urgency,
            risk_score,
            risk_factors,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        patient_id,
        urgency,
        risk_score,
        ", ".join(risk_factors),
        now
    ))

    conn.commit()
    conn.close()

    return {
        "patient_id": patient_id,
        "urgency": urgency,
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "timestamp": now
    }


# -------------------------
# PATIENT TIMELINE
# -------------------------

@app.get("/patients/{patient_id}/timeline")
def get_timeline(patient_id: str):

    conn = get_db()

    timeline = conn.execute("""
        SELECT
            urgency,
            risk_score,
            risk_factors,
            timestamp
        FROM assessments
        WHERE patient_id = ?
        ORDER BY timestamp ASC
    """, (patient_id,)).fetchall()

    conn.close()

    return [dict(item) for item in timeline]


# -------------------------
# DASHBOARD STATISTICS
# -------------------------

@app.get("/dashboard")
def dashboard():

    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) FROM patients"
    ).fetchone()[0]

    critical = conn.execute(
        "SELECT COUNT(*) FROM patients WHERE urgency = 'Critical'"
    ).fetchone()[0]

    urgent = conn.execute(
        "SELECT COUNT(*) FROM patients WHERE urgency = 'Urgent'"
    ).fetchone()[0]

    non_urgent = conn.execute(
        "SELECT COUNT(*) FROM patients WHERE urgency = 'Non-urgent'"
    ).fetchone()[0]

    conn.close()

    return {
        "total_patients": total,
        "critical": critical,
        "urgent": urgent,
        "non_urgent": non_urgent
    }


# -------------------------
# HEALTH CHECK
# -------------------------

@app.get("/")
def root():

    return {
        "system": "MEDORA",
        "status": "running",
        "description": "AI-assisted emergency triage system"
    }