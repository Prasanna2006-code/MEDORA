from datetime import datetime

from models import get_all_patients


# ============================================================
# PRIORITY CONFIGURATION
# ============================================================

URGENCY_PRIORITY = {
    "Critical": 1,
    "Urgent": 2,
    "Non-urgent": 3
}


# ============================================================
# GET PATIENT PRIORITY
# ============================================================

def get_priority_value(urgency):

    return URGENCY_PRIORITY.get(
        urgency,
        4
    )


# ============================================================
# CALCULATE WAITING TIME
# ============================================================

def calculate_waiting_minutes(created_at):

    if not created_at:
        return 0

    try:

        created_time = datetime.fromisoformat(
            created_at
        )

        now = datetime.now()

        difference = now - created_time

        return max(
            int(difference.total_seconds() / 60),
            0
        )

    except (ValueError, TypeError):

        return 0


# ============================================================
# BUILD PRIORITY QUEUE
# ============================================================

def build_priority_queue():

    patients = get_all_patients()

    queue = []

    for patient in patients:

        urgency = patient.get(
            "urgency",
            "Non-urgent"
        )

        risk_score = float(
            patient.get(
                "risk_score",
                0
            ) or 0
        )

        waiting_minutes = calculate_waiting_minutes(
            patient.get("created_at")
        )

        priority = get_priority_value(
            urgency
        )

        queue.append({
            "patient_id": patient.get("id"),
            "name": patient.get("name"),
            "age": patient.get("age"),
            "sex": patient.get("sex"),

            "urgency": urgency,
            "risk_score": risk_score,

            "risk_factors": patient.get(
                "risk_factors",
                ""
            ),

            "status": patient.get(
                "status",
                "Waiting"
            ),

            "arrival_mode": patient.get(
                "arrival_mode"
            ),

            "waiting_minutes": waiting_minutes,

            "priority": priority,

            "created_at": patient.get(
                "created_at"
            ),

            "updated_at": patient.get(
                "updated_at"
            )
        })


    # --------------------------------------------------------
    # SORT QUEUE
    # --------------------------------------------------------

    queue.sort(
        key=lambda patient: (
            patient["priority"],
            -patient["risk_score"],
            -patient["waiting_minutes"]
        )
    )


    # --------------------------------------------------------
    # ADD QUEUE POSITION
    # --------------------------------------------------------

    for index, patient in enumerate(
        queue,
        start=1
    ):

        patient["queue_position"] = index


    return queue


# ============================================================
# QUEUE SUMMARY
# ============================================================

def get_queue_summary():

    queue = build_priority_queue()

    critical = 0
    urgent = 0
    non_urgent = 0

    waiting = 0
    in_treatment = 0

    for patient in queue:

        if patient["urgency"] == "Critical":
            critical += 1

        elif patient["urgency"] == "Urgent":
            urgent += 1

        elif patient["urgency"] == "Non-urgent":
            non_urgent += 1


        if patient["status"] == "Waiting":
            waiting += 1

        elif patient["status"] == "In Treatment":
            in_treatment += 1


    return {
        "total": len(queue),

        "critical": critical,
        "urgent": urgent,
        "non_urgent": non_urgent,

        "waiting": waiting,
        "in_treatment": in_treatment
    }
