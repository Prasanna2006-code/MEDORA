from database import get_db


def create_patient_record(
    patient_id,
    name,
    age,
    sex,
    symptoms,
    disorders,
    heart_rate,
    systolic_bp,
    diastolic_bp,
    respiratory_rate,
    spo2,
    temperature,
    pain_score,
    gcs_score,
    arrival_mode,
    urgency,
    risk_score,
    risk_factors,
    created_at,
    updated_at
):
    conn = get_db()

    conn.execute("""
        INSERT INTO patients (
            id,
            name,
            age,
            sex,
            symptoms,
            disorders,
            heart_rate,
            systolic_bp,
            diastolic_bp,
            respiratory_rate,
            spo2,
            temperature,
            pain_score,
            gcs_score,
            arrival_mode,
            urgency,
            risk_score,
            risk_factors,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        name,
        age,
        sex,
        symptoms,
        disorders,
        heart_rate,
        systolic_bp,
        diastolic_bp,
        respiratory_rate,
        spo2,
        temperature,
        pain_score,
        gcs_score,
        arrival_mode,
        urgency,
        risk_score,
        risk_factors,
        created_at,
        updated_at
    ))

    conn.commit()
    conn.close()


def get_patient_by_id(patient_id):
    conn = get_db()

    patient = conn.execute(
        "SELECT * FROM patients WHERE id = ?",
        (patient_id,)
    ).fetchone()

    conn.close()

    return dict(patient) if patient else None


def get_all_patients():
    conn = get_db()

    patients = conn.execute("""
        SELECT *
        FROM patients
        ORDER BY
            CASE urgency
                WHEN 'Critical' THEN 1
                WHEN 'Urgent' THEN 2
                WHEN 'Non-urgent' THEN 3
                ELSE 4
            END,
            updated_at DESC
    """).fetchall()

    conn.close()

    return [dict(patient) for patient in patients]


def update_patient(
    patient_id,
    name,
    age,
    sex,
    symptoms,
    disorders,
    heart_rate,
    systolic_bp,
    diastolic_bp,
    respiratory_rate,
    spo2,
    temperature,
    pain_score,
    gcs_score,
    arrival_mode,
    urgency,
    risk_score,
    risk_factors,
    updated_at
):
    conn = get_db()

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
        name,
        age,
        sex,
        symptoms,
        disorders,
        heart_rate,
        systolic_bp,
        diastolic_bp,
        respiratory_rate,
        spo2,
        temperature,
        pain_score,
        gcs_score,
        arrival_mode,
        urgency,
        risk_score,
        risk_factors,
        updated_at,
        patient_id
    ))

    conn.commit()
    conn.close()


def add_assessment(
    patient_id,
    urgency,
    risk_score,
    risk_factors,
    timestamp
):
    conn = get_db()

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
        risk_factors,
        timestamp
    ))

    conn.commit()
    conn.close()


def get_patient_timeline(patient_id):
    conn = get_db()

    timeline = conn.execute("""
        SELECT
            id,
            patient_id,
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