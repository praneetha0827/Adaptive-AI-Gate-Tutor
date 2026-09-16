from app.services.mastery import calculate_updated_mastery, mastery_confidence


def test_correct_answer_increases_initial_mastery() -> None:
    assert calculate_updated_mastery(50, 0, True, 60_000) > 50


def test_incorrect_answer_decreases_initial_mastery() -> None:
    assert calculate_updated_mastery(50, 0, False, 60_000) < 50


def test_evidence_reduces_update_size() -> None:
    assert calculate_updated_mastery(50, 0, True, 60_000) > calculate_updated_mastery(50, 12, True, 60_000)


def test_mastery_confidence_uses_evidence_count() -> None:
    assert mastery_confidence(0) == "low"
    assert mastery_confidence(5) == "medium"
    assert mastery_confidence(12) == "high"
from app.services.mastery import calculate_updated_mastery


def test_first_mastery_update_uses_zero_evidence() -> None:
    assert calculate_updated_mastery(50.0, 0, True, 1_000) > 50.0
