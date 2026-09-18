from typing import Any, Dict, List


def get_patient_value(patient: Any, field: str, default: Any = None):
    if isinstance(patient, dict):
        return patient.get(field, default)

    return getattr(patient, field, default)


def build_patient_summary(patient: Any) -> Dict[str, Any]:
    return {
        "name": get_patient_value(patient, "name", "Unknown"),
        "age": get_patient_value(patient, "age"),
        "sex": get_patient_value(patient, "sex"),
        "symptoms": get_patient_value(patient, "symptoms", ""),
        "disorders": get_patient_value(patient, "disorders", ""),
        "heart_rate": get_patient_value(patient, "heart_rate"),
        "systolic_bp": get_patient_value(patient, "systolic_bp"),
        "diastolic_bp": get_patient_value(patient, "diastolic_bp"),
        "respiratory_rate": get_patient_value(
            patient,
            "respiratory_rate"
        ),
        "spo2": get_patient_value(patient, "spo2"),
        "temperature": get_patient_value(patient, "temperature"),
        "pain_score": get_patient_value(patient, "pain_score"),
        "gcs_score": get_patient_value(patient, "gcs_score"),
        "arrival_mode": get_patient_value(
            patient,
            "arrival_mode",
            "Walk-in"
        )
    }


def create_ai_prompt(
    patient: Any,
    urgency: str,
    risk_score: float,
    risk_factors: List[str]
) -> str:

    data = build_patient_summary(patient)

    risk_factor_text = ", ".join(risk_factors)

    prompt = (
        "You are an AI decision-support assistant for MEDORA.\n\n"
        "Explain the existing triage assessment to healthcare staff.\n\n"
        "Do not diagnose the patient.\n"
        "Do not prescribe medication.\n"
        "Do not invent missing information.\n\n"
        "Patient:\n"
        f"Name: {data['name']}\n"
        f"Age: {data['age']}\n"
        f"Sex: {data['sex']}\n"
        f"Symptoms: {data['symptoms']}\n"
        f"Existing disorders: {data['disorders'] or 'None reported'}\n\n"
        "Vital signs:\n"
        f"Heart rate: {data['heart_rate']} bpm\n"
        f"Blood pressure: "
        f"{data['systolic_bp']}/{data['diastolic_bp']} mmHg\n"
        f"Respiratory rate: {data['respiratory_rate']}/min\n"
        f"SpO2: {data['spo2']}%\n"
        f"Temperature: {data['temperature']} °C\n"
        f"Pain score: {data['pain_score']}/10\n"
        f"GCS: {data['gcs_score']}/15\n"
        f"Arrival mode: {data['arrival_mode']}\n\n"
        "Triage result:\n"
        f"Urgency: {urgency}\n"
        f"Risk score: {risk_score}%\n"
        f"Risk factors: {risk_factor_text}\n\n"
        "Provide:\n"
        "1. A short explanation of the triage result.\n"
        "2. Important warning indicators.\n"
        "3. Information that should be reassessed.\n"
        "4. A safety note.\n\n"
        "Do not replace professional clinical judgment."
    )

    return prompt


def generate_local_explanation(
    urgency: str,
    risk_score: float,
    risk_factors: List[str]
) -> Dict[str, Any]:

    if urgency == "Critical":
        summary = (
            "The assessment identified warning indicators "
            "that place the patient in the highest configured "
            "triage priority."
        )

    elif urgency == "Urgent":
        summary = (
            "The assessment identified warning indicators "
            "that place the patient in an urgent triage priority."
        )

    else:
        summary = (
            "The assessment did not identify major warning "
            "indicators requiring a higher triage priority."
        )

    return {
        "summary": summary,
        "urgency": urgency,
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "reassessment": (
            "Reassess symptoms and vital signs if the "
            "patient's condition changes."
        ),
        "disclaimer": (
            "MEDORA is an AI-assisted triage prototype "
            "and does not replace professional clinical judgment."
        )
    }


def generate_ai_service(
    patient: Any,
    urgency: str,
    risk_score: float,
    risk_factors: List[str]
) -> Dict[str, Any]:

    prompt = create_ai_prompt(
        patient,
        urgency,
        risk_score,
        risk_factors
    )

    explanation = generate_local_explanation(
        urgency,
        risk_score,
        risk_factors
    )

    return {
        "success": True,
        "provider": "MEDORA AI Service",
        "explanation": explanation,
        "ai_prompt": prompt
    }


def ai_service_health() -> Dict[str, Any]:
    return {
        "service": "MEDORA AI Service",
        "status": "ready",
        "external_api": False
    }