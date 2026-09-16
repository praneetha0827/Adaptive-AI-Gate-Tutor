from app.schemas.assessment import CreateQuizRequest, QuizResultResponse


def test_quiz_request_requires_question_count_in_range() -> None:
    request = CreateQuizRequest(subtopic_ids=["subtopic"], question_count=5)
    assert request.question_count == 5


def test_quiz_request_rejects_empty_subtopic_list() -> None:
    try:
        CreateQuizRequest(subtopic_ids=[], question_count=5)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected empty subtopic IDs to be rejected")


def test_quiz_result_includes_answer_review() -> None:
    result = QuizResultResponse(
        score_percent=100,
        correct_count=1,
        question_count=1,
        mistakes_created=0,
        reviews=[{"prompt": "Question", "submitted_answer": "A", "correct_answer": "A", "explanation": "Because.", "is_correct": True}],
    )

    assert result.reviews[0].is_correct is True
