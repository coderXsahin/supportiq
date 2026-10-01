def predict_priority(text: str) -> str:
    text = text.lower()

    critical_keywords = [
        "complete outage",
        "system down",
        "production down",
        "all users",
        "data loss",
        "security breach"
    ]

    high_keywords = [
        "urgent",
        "cannot access",
        "not working",
        "failed",
        "failure",
        "error",
        "unavailable",
        "down"
    ]

    medium_keywords = [
        "slow",
        "timeout",
        "intermittent",
        "degraded"
    ]

    for keyword in critical_keywords:
        if keyword in text:
            return "CRITICAL"

    for keyword in high_keywords:
        if keyword in text:
            return "HIGH"

    for keyword in medium_keywords:
        if keyword in text:
            return "MEDIUM"

    return "LOW"