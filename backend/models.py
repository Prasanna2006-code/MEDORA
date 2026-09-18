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
    updated_at,
    status="Waiting",
    is_unidentified=0
):
    conn = get_db()

    conn.execute("""
        INSERT INTO patients (
            id, name, age, sex, symptoms, disorders,
            heart_rate, systolic_bp, diastolic_bp,
            respiratory_rate, spo2, temperature,
            pain_score, gcs_score, arrival_mode,
            urgency, risk_score, risk_factors,
            status, is_unidentified,
            created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        status,
        is_unidentified,
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
        SELECT * FROM patients
        ORDER BY
            CASE urgency
                WHEN 'Critical' THEN 1
                WHEN 'Urgent' THEN 2
                WHEN 'Non-urgent' THEN 3
                ELSE 4
            END,
            risk_score DESC,
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
    updated_at,
    status=None,
    is_unidentified=None
):
    conn = get_db()

    current = get_patient_by_id(patient_id)

    if not current:
        conn.close()
        return False

    final_status = (
        status if status is not None
        else current["status"]
    )

    final_unidentified = (
        is_unidentified
        if is_unidentified is not None
        else current["is_unidentified"]
    )

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
            status = ?,
            is_unidentified = ?,
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
        final_status,
        final_unidentified,
        updated_at,
        patient_id
    ))

    conn.commit()
    conn.close()

    return True


def update_patient_status(patient_id, status):
    conn = get_db()

    cursor = conn.execute("""
        UPDATE patients
        SET status = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (
        status,
        patient_id
    ))

    conn.commit()
    conn.close()

    return cursor.rowcount > 0


def add_assessment(
    patient_id,
    urgency,
    risk_score,
    risk_factors,
    timestamp,
    heart_rate=None,
    systolic_bp=None,
    diastolic_bp=None,
    respiratory_rate=None,
    spo2=None,
    temperature=None,
    pain_score=None,
    gcs_score=None,
    symptoms=None
):
    conn = get_db()

    conn.execute("""
        INSERT INTO assessments (
            patient_id,
            urgency,
            risk_score,
            risk_factors,
            heart_rate,
            systolic_bp,
            diastolic_bp,
            respiratory_rate,
            spo2,
            temperature,
            pain_score,
            gcs_score,
            symptoms,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        urgency,
        risk_score,
        risk_factors,
        heart_rate,
        systolic_bp,
        diastolic_bp,
        respiratory_rate,
        spo2,
        temperature,
        pain_score,
        gcs_score,
        symptoms,
        timestamp
    ))

    conn.commit()
    conn.close()


def get_patient_timeline(patient_id):
    conn = get_db()

    timeline = conn.execute("""
        SELECT *
        FROM assessments
        WHERE patient_id = ?
        ORDER BY timestamp ASC
    """, (
        patient_id,
    )).fetchall()

    conn.close()

    return [dict(item) for item in timeline]


def create_unidentified_patient(
    temporary_id,
    estimated_age=None,
    sex=None,
    identifying_notes="",
    patient_id=None,
    created_at=None,
    updated_at=None
):
    conn = get_db()

    conn.execute("""
        INSERT INTO unidentified_patients (
            id,
            temporary_name,
            estimated_age,
            sex,
            identifying_notes,
            patient_id,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        temporary_id,
        "Unknown Patient",
        estimated_age,
        sex,
        identifying_notes,
        patient_id,
        created_at,
        updated_at
    ))

    conn.commit()
    conn.close()


def get_unidentified_patient(temporary_id):
    conn = get_db()

    patient = conn.execute("""
        SELECT *
        FROM unidentified_patients
        WHERE id = ?
    """, (
        temporary_id,
    )).fetchone()

    conn.close()

    return dict(patient) if patient else None


def get_all_unidentified_patients():
    conn = get_db()

    patients = conn.execute("""
        SELECT *
        FROM unidentified_patients
        ORDER BY created_at DESC
    """).fetchall()

    conn.close()

    return [dict(patient) for patient in patients]


def create_alert(
    patient_id,
    alert_type,
    message,
    severity="Normal",
    created_at=None
):
    conn = get_db()

    conn.execute("""
        INSERT INTO alerts (
            patient_id,
            alert_type,
            message,
            severity,
            is_read,
            created_at
        )
        VALUES (?, ?, ?, ?, 0, ?)
    """, (
        patient_id,
        alert_type,
        message,
        severity,
        created_at
    ))

    conn.commit()
    conn.close()


def get_alerts(unread_only=False):
    conn = get_db()

    if unread_only:
        alerts = conn.execute("""
            SELECT *
            FROM alerts
            WHERE is_read = 0
            ORDER BY created_at DESC
        """).fetchall()
    else:
        alerts = conn.execute("""
            SELECT *
            FROM alerts
            ORDER BY created_at DESC
        """).fetchall()

    conn.close()

    return [dict(alert) for alert in alerts]


def mark_alert_read(alert_id):
    conn = get_db()

    cursor = conn.execute("""
        UPDATE alerts
        SET is_read = 1
        WHERE id = ?
    """, (
        alert_id,
    ))

    conn.commit()
    conn.close()

    return cursor.rowcount > 0