from datetime import datetime, timezone


def calculate_sla_status(sla_deadline):
    if sla_deadline is None:
        return {
            "sla_status": "NOT_SET",
            "remaining_minutes": None
        }

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    remaining_seconds = (
        sla_deadline - now
    ).total_seconds()

    if remaining_seconds <= 0:
        return {
            "sla_status": "BREACHED",
            "remaining_minutes": 0
        }

    if remaining_seconds <= 3600:
        return {
            "sla_status": "AT_RISK",
            "remaining_minutes": int(
                remaining_seconds / 60
            )
        }

    return {
        "sla_status": "ON_TRACK",
        "remaining_minutes": int(
            remaining_seconds / 60
        )
    }