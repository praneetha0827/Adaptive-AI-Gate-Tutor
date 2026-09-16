from app.schemas.tutor import TutorTurn


def test_tutor_turn_requires_valid_stage_and_difficulty() -> None:
    turn = TutorTurn(stage="interactive_question", explanation="Try tracing the first recursive call.", question="What happens next?", difficulty=2)
    assert turn.stage == "interactive_question"


def test_tutor_turn_rejects_invalid_difficulty() -> None:
    try:
        TutorTurn(stage="explain", explanation="Text", difficulty=6)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected invalid difficulty to be rejected")
