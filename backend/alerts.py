from datetime import datetime

from models import (
    create_alert,
    get_alerts,
    mark_alert_read
)


def create_critical_alert(
    patient_id,
    risk_score,
    risk_factors
):
    message = (
        f"Critical triage detected. "
        f"Risk score: {risk_score}%. "
        f"Risk factors: {', '.join(risk_factors)}"
    )

    create_alert(
        patient_id=patient_id,
        alert_type="Critical Triage",
        message=message,
        severity="Critical",
        created_at=datetime.now().isoformat(
            timespec="seconds"
        )
    )


def create_urgency_change_alert(
    patient_id,
    old_urgency,
    new_urgency
):
    message = (
        f"Patient urgency changed from "
        f"{old_urgency} to {new_urgency}."
    )

    severity = (
        "Critical"
        if new_urgency == "Critical"
        else "Warning"
    )

    create_alert(
        patient_id=patient_id,
        alert_type="Urgency Change",
        message=message,
        severity=severity,
        created_at=datetime.now().isoformat(
            timespec="seconds"
        )
    )


def get_all_alerts():
    return get_alerts(unread_only=False)


def get_unread_alerts():
    return get_alerts(unread_only=True)


def read_alert(alert_id):
    return mark_alert_read(alert_id)