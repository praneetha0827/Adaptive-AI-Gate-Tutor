import pytest
from pydantic import ValidationError

from app.schemas.learning import OnboardingRequest


def onboarding_payload(subject_confidence: dict[str, int]) -> dict[str, object]:
    return {
        "display_name": "Learner",
        "target_year": 2027,
        "daily_study_minutes": 120,
        "programming_experience": "beginner",
        "subject_confidence": subject_confidence,
    }


def test_onboarding_accepts_subject_confidence_by_curriculum_id() -> None:
    request = OnboardingRequest(**onboarding_payload({"subject-id": 3}))

    assert request.subject_confidence == {"subject-id": 3}


def test_onboarding_rejects_out_of_range_subject_confidence() -> None:
    with pytest.raises(ValidationError):
        OnboardingRequest(**onboarding_payload({"subject-id": 6}))
