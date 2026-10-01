from datetime import datetime, timedelta

from app.api.tickets import predict_priority, get_resolution_suggestion
from app.services.sla_service import calculate_sla_status
from app.services.duplicate_service import calculate_similarity


def test_critical_priority():
    result = predict_priority(
        "Production system down for all users"
    )

    assert result == "CRITICAL"


def test_high_priority():
    result = predict_priority(
        "Database connection failed"
    )

    assert result == "HIGH"


def test_medium_priority():
    result = predict_priority(
        "Application is slow and experiencing timeout"
    )

    assert result == "MEDIUM"


def test_low_priority():
    result = predict_priority(
        "Request for general information"
    )

    assert result == "LOW"


def test_database_resolution_suggestion():
    result = get_resolution_suggestion("Database")

    assert "database server health" in result.lower()


def test_sla_not_set():
    result = calculate_sla_status(None)

    assert result["sla_status"] == "NOT_SET"
    assert result["remaining_minutes"] is None


def test_sla_on_track():
    future_deadline = datetime.utcnow() + timedelta(hours=2)

    result = calculate_sla_status(future_deadline)

    assert result["sla_status"] == "ON_TRACK"
    assert result["remaining_minutes"] > 0


def test_duplicate_similarity():
    text1 = "Production database connection failed"
    text2 = "Production database connection failure"

    similarity = calculate_similarity(text1, text2)

    assert similarity >= 0.30