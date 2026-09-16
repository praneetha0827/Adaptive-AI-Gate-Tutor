from app.schemas.user import UserResponse


def test_current_user_response_exposes_onboarding_state() -> None:
    response = UserResponse(
        id="user-id",
        email="learner@example.com",
        is_active=True,
        onboarding_completed=True,
    )

    assert response.onboarding_completed is True
