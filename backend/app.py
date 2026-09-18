from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid

from database import init_db
from schemas import (
    PatientInput,
    ReassessmentInput,
    PatientStatusUpdate,
    UnidentifiedPatientInput,
    AlertInput
)

from triage import calculate_triage

from models import (
    create_patient_record,
    get_patient_by_id,
    get_all_patients,
    update_patient,
    update_patient_status,
    add_assessment,
    get_patient_timeline,
    create_unidentified_patient,
    get_unidentified_patient,
    get_all_unidentified_patients,
    create_alert,
    get_alerts,
    mark_alert_read
)

from priority_queue import build_priority_queue, get_queue_summary

from alerts import (
    create_critical_alert,
    create_urgency_change_alert
)


app = FastAPI(
    title="MEDORA",
    description="AI-Assisted Hospital Emergency Triage and Patient Prioritization System",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


init_db()


# -------------------------
# ROOT
# -------------------------

@app.get("/")
def root():
    return {
        "system": "MEDORA",
        "status": "online",
        "message": "MEDORA Emergency Triage API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "MEDORA API"
    }


# -------------------------
# CREATE PATIENT
# -------------------------

@app.post("/patients")
def create_patient(patient: PatientInput):

    result = calculate_triage(patient)

    patient_id = "MED-" + uuid.uuid4().hex[:8].upper()

    now = datetime.now().isoformat(timespec="seconds")

    create_patient_record(
        patient_id=patient_id,
        name=patient.name,
        age=patient.age,
        sex=patient.sex,
        symptoms=patient.symptoms,
        disorders=patient.disorders,
        heart_rate=patient.heart_rate,
        systolic_bp=patient.systolic_bp,
        diastolic_bp=patient.diastolic_bp,
        respiratory_rate=patient.respiratory_rate,
        spo2=patient.spo2,
        temperature=patient.temperature,
        pain_score=patient.pain_score,
        gcs_score=patient.gcs_score,
        arrival_mode=patient.arrival_mode,
        urgency=result["urgency"],
        risk_score=result["risk_score"],
        risk_factors=", ".join(result["risk_factors"]),
        created_at=now,
        updated_at=now
    )

    add_assessment(
        patient_id=patient_id,
        urgency=result["urgency"],
        risk_score=result["risk_score"],
        risk_factors=", ".join(result["risk_factors"]),
        timestamp=now,
        heart_rate=patient.heart_rate,
        systolic_bp=patient.systolic_bp,
        diastolic_bp=patient.diastolic_bp,
        respiratory_rate=patient.respiratory_rate,
        spo2=patient.spo2,
        temperature=patient.temperature,
        pain_score=patient.pain_score,
        gcs_score=patient.gcs_score,
        symptoms=patient.symptoms
    )

    if result["urgency"] == "Critical":
        create_critical_alert(
            patient_id,
            result["risk_score"],
            result["risk_factors"]
        )

    return {
        "success": True,
        "patient_id": patient_id,
        "urgency": result["urgency"],
        "risk_score": result["risk_score"],
        "risk_factors": result["risk_factors"],
        "timestamp": now
    }


# -------------------------
# GET ALL PATIENTS
# -------------------------

@app.get("/patients")
def patients():

    records = get_all_patients()

    return {
        "success": True,
        "count": len(records),
        "patients": records
    }


# -------------------------
# GET PATIENT
# -------------------------

@app.get("/patients/{patient_id}")
def patient_details(patient_id: str):

    patient = get_patient_by_id(patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return {
        "success": True,
        "patient": patient
    }


# -------------------------
# REASSESS PATIENT
# -------------------------

@app.put("/patients/{patient_id}/reassess")
def reassess_patient(
    patient_id: str,
    reassessment: PatientInput
):

    existing_patient = get_patient_by_id(patient_id)

    if not existing_patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    old_urgency = existing_patient["urgency"]

    result = calculate_triage(reassessment)

    now = datetime.now().isoformat(timespec="seconds")

    update_patient(
        patient_id=patient_id,
        name=reassessment.name,
        age=reassessment.age,
        sex=reassessment.sex,
        symptoms=reassessment.symptoms,
        disorders=reassessment.disorders,
        heart_rate=reassessment.heart_rate,
        systolic_bp=reassessment.systolic_bp,
        diastolic_bp=reassessment.diastolic_bp,
        respiratory_rate=reassessment.respiratory_rate,
        spo2=reassessment.spo2,
        temperature=reassessment.temperature,
        pain_score=reassessment.pain_score,
        gcs_score=reassessment.gcs_score,
        arrival_mode=reassessment.arrival_mode,
        urgency=result["urgency"],
        risk_score=result["risk_score"],
        risk_factors=", ".join(result["risk_factors"]),
        updated_at=now
    )

    add_assessment(
        patient_id=patient_id,
        urgency=result["urgency"],
        risk_score=result["risk_score"],
        risk_factors=", ".join(result["risk_factors"]),
        timestamp=now,
        heart_rate=reassessment.heart_rate,
        systolic_bp=reassessment.systolic_bp,
        diastolic_bp=reassessment.diastolic_bp,
        respiratory_rate=reassessment.respiratory_rate,
        spo2=reassessment.spo2,
        temperature=reassessment.temperature,
        pain_score=reassessment.pain_score,
        gcs_score=reassessment.gcs_score,
        symptoms=reassessment.symptoms
    )

    if old_urgency != result["urgency"]:

        create_urgency_change_alert(
            patient_id,
            old_urgency,
            result["urgency"]
        )

    if result["urgency"] == "Critical":

        create_critical_alert(
            patient_id,
            result["risk_score"],
            result["risk_factors"]
        )

    return {
        "success": True,
        "patient_id": patient_id,
        "urgency": result["urgency"],
        "risk_score": result["risk_score"],
        "risk_factors": result["risk_factors"],
        "timestamp": now
    }


# -------------------------
# PATIENT STATUS
# -------------------------

@app.put("/patients/{patient_id}/status")
def change_patient_status(
    patient_id: str,
    status_data: PatientStatusUpdate
):

    patient = get_patient_by_id(patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    allowed_statuses = [
        "Waiting",
        "In Treatment",
        "Admitted",
        "Discharged"
    ]

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of: {allowed_statuses}"
        )

    update_patient_status(
        patient_id,
        status_data.status
    )

    return {
        "success": True,
        "patient_id": patient_id,
        "status": status_data.status
    }


# -------------------------
# PATIENT TIMELINE
# -------------------------

@app.get("/patients/{patient_id}/timeline")
def patient_timeline(patient_id: str):

    patient = get_patient_by_id(patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    timeline = get_patient_timeline(patient_id)

    return {
        "success": True,
        "patient_id": patient_id,
        "timeline": timeline
    }


# -------------------------
# PRIORITY QUEUE
# -------------------------

@app.get("/queue")
def priority_queue():

    queue = build_priority_queue()

    return {
        "success": True,
        "count": len(queue),
        "queue": queue
    }


@app.get("/queue/summary")
def queue_summary():

    return {
        "success": True,
        **get_queue_summary()
    }


# -------------------------
# DASHBOARD
# -------------------------

@app.get("/dashboard")
def dashboard():

    summary = get_queue_summary()

    return {
        "success": True,
        "total_patients": summary["total"],
        "critical": summary["critical"],
        "urgent": summary["urgent"],
        "non_urgent": summary["non_urgent"],
        "waiting": summary["waiting"],
        "in_treatment": summary["in_treatment"]
    }


# -------------------------
# UNIDENTIFIED PATIENT
# -------------------------

@app.post("/unidentified-patients")
def add_unidentified_patient(
    patient: UnidentifiedPatientInput
):

    temporary_id = "UNK-" + uuid.uuid4().hex[:8].upper()

    now = datetime.now().isoformat(timespec="seconds")

    create_unidentified_patient(
        temporary_id=temporary_id,
        estimated_age=patient.estimated_age,
        sex=patient.sex,
        identifying_notes=patient.identifying_notes,
        created_at=now,
        updated_at=now
    )

    return {
        "success": True,
        "temporary_id": temporary_id,
        "message": "Unidentified patient registered"
    }


@app.get("/unidentified-patients")
def unidentified_patients():

    patients = get_all_unidentified_patients()

    return {
        "success": True,
        "count": len(patients),
        "patients": patients
    }


@app.get("/unidentified-patients/{temporary_id}")
def unidentified_patient_details(
    temporary_id: str
):

    patient = get_unidentified_patient(temporary_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Unidentified patient not found"
        )

    return {
        "success": True,
        "patient": patient
    }


# -------------------------
# ALERTS
# -------------------------

@app.get("/alerts")
def alerts():

    return {
        "success": True,
        "alerts": get_alerts()
    }


@app.get("/alerts/unread")
def unread_alerts():

    return {
        "success": True,
        "alerts": get_alerts(unread_only=True)
    }


@app.post("/alerts")
def add_alert(alert: AlertInput):

    now = datetime.now().isoformat(timespec="seconds")

    create_alert(
        patient_id=alert.patient_id,
        alert_type=alert.alert_type,
        message=alert.message,
        severity=alert.severity,
        created_at=now
    )

    return {
        "success": True,
        "message": "Alert created"
    }


@app.put("/alerts/{alert_id}/read")
def read_alert(alert_id: int):

    success = mark_alert_read(alert_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    return {
        "success": True,
        "alert_id": alert_id,
        "message": "Alert marked as read"
    }


# -------------------------
# API INFORMATION
# -------------------------

@app.get("/api/info")
def api_info():

    return {
        "name": "MEDORA",
        "version": "1.0.0",
        "purpose": "AI-assisted emergency triage and patient prioritization",

        "modules": [
            "Emergency Triage",
            "Patient Management",
            "AI Triage",
            "Priority Queue",
            "Reassessment",
            "History",
            "Dashboard",
            "Unidentified Patient",
            "Alerts"
        ]
    }