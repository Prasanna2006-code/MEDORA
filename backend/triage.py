def calculate_triage(patient):
    """
    MEDORA AI-assisted triage engine.

    Returns:
        urgency
        risk_score
        risk_factors
    """

    score = 0
    risk_factors = []

    # -------------------------
    # SpO2
    # -------------------------

    if patient.spo2 < 90:
        score += 5
        risk_factors.append("Severely low SpO₂")

    elif patient.spo2 < 94:
        score += 3
        risk_factors.append("Low SpO₂")

    # -------------------------
    # Heart Rate
    # -------------------------

    if patient.heart_rate > 120:
        score += 3
        risk_factors.append("High heart rate")

    elif patient.heart_rate < 50:
        score += 3
        risk_factors.append("Low heart rate")

    # -------------------------
    # Respiratory Rate
    # -------------------------

    if patient.respiratory_rate > 30:
        score += 4
        risk_factors.append("High respiratory rate")

    elif patient.respiratory_rate < 10:
        score += 4
        risk_factors.append("Low respiratory rate")

    # -------------------------
    # Blood Pressure
    # -------------------------

    if patient.systolic_bp < 90:
        score += 5
        risk_factors.append("Low systolic blood pressure")

    elif patient.systolic_bp > 180:
        score += 4
        risk_factors.append("Very high systolic blood pressure")

    # -------------------------
    # Temperature
    # -------------------------

    if patient.temperature >= 39.5:
        score += 3
        risk_factors.append("High temperature")

    # -------------------------
    # GCS
    # -------------------------

    if patient.gcs_score < 9:
        score += 6
        risk_factors.append("Severely reduced GCS")

    elif patient.gcs_score < 13:
        score += 4
        risk_factors.append("Reduced GCS")

    # -------------------------
    # Pain
    # -------------------------

    if patient.pain_score >= 8:
        score += 2
        risk_factors.append("Severe pain")

    # -------------------------
    # Age
    # -------------------------

    if patient.age >= 75:
        score += 2
        risk_factors.append("Advanced age")

    elif patient.age <= 5:
        score += 2
        risk_factors.append("Very young age")

    # -------------------------
    # Arrival Mode
    # -------------------------

    if patient.arrival_mode.lower() == "ambulance":
        score += 1
        risk_factors.append("Arrived by ambulance")

    # -------------------------
    # Symptom Analysis
    # -------------------------

    symptoms = patient.symptoms.lower()

    emergency_keywords = {
        "chest pain": "Chest pain",
        "difficulty breathing": "Difficulty breathing",
        "shortness of breath": "Shortness of breath",
        "unconscious": "Unconsciousness",
        "seizure": "Seizure",
        "severe bleeding": "Severe bleeding",
        "stroke": "Possible stroke symptoms",
        "paralysis": "Paralysis"
    }

    for keyword, description in emergency_keywords.items():

        if keyword in symptoms:
            score += 5
            risk_factors.append(description)
            break

    # -------------------------
    # Comorbidity Analysis
    # -------------------------

    disorders = patient.disorders.lower()

    high_risk_conditions = [
        "heart disease",
        "kidney disease",
        "diabetes",
        "hypertension",
        "cancer",
        "copd",
        "asthma"
    ]

    detected_conditions = []

    for condition in high_risk_conditions:

        if condition in disorders:
            detected_conditions.append(condition)

    if detected_conditions:

        score += min(len(detected_conditions), 3)

        risk_factors.append(
            "Existing condition: "
            + ", ".join(detected_conditions)
        )

    # -------------------------
    # Urgency Classification
    # -------------------------

    if score >= 8:
        urgency = "Critical"

    elif score >= 4:
        urgency = "Urgent"

    else:
        urgency = "Non-urgent"

    # -------------------------
    # Risk Score
    # -------------------------

    # Convert the rule score to a simple 0-100 scale.
    risk_score = min(round((score / 20) * 100, 1), 100)

    # Make sure at least one explanation exists.
    if not risk_factors:
        risk_factors.append("No major warning indicators detected")

    return {
        "urgency": urgency,
        "risk_score": risk_score,
        "risk_factors": risk_factors
    }