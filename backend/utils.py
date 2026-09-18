from datetime import datetime
import uuid


def generate_patient_id() -> str:
    return "MED-" + uuid.uuid4().hex[:8].upper()


def generate_unknown_patient_id() -> str:
    return "UNK-" + uuid.uuid4().hex[:8].upper()


def get_current_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def format_risk_score(score) -> str:
    try:
        return f"{float(score):.1f}%"
    except (TypeError, ValueError):
        return "0.0%"


def normalize_text(value) -> str:
    if value is None:
        return ""

    return " ".join(str(value).strip().split())


def split_risk_factors(value) -> list[str]:
    if not value:
        return []

    if isinstance(value, list):
        return value

    return [
        factor.strip()
        for factor in str(value).split(",")
        if factor.strip()
    ]


def is_valid_status(status: str) -> bool:
    allowed_statuses = [
        "Waiting",
        "In Treatment",
        "Admitted",
        "Discharged"
    ]

    return status in allowed_statuses


def is_valid_urgency(urgency: str) -> bool:
    allowed_urgencies = [
        "Critical",
        "Urgent",
        "Non-urgent"
    ]

    return urgency in allowed_urgencies