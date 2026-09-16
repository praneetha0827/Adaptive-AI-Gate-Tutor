from app.models.learning import Question, QuestionType
from app.services.assessment import is_correct_answer


def test_msq_scoring_ignores_option_order_and_whitespace() -> None:
    question = Question(question_type=QuestionType.MSQ, correct_answer="A, C", source="curated_practice", prompt="", explanation="", concept="", skill_tested="", difficulty=1, subtopic_id="subtopic")
    assert is_correct_answer(question, "c, a")
from app.models.learning import Question, QuestionType
from app.services.assessment import is_correct_answer


def test_msq_scoring_ignores_answer_order_and_case() -> None:
    question = Question(question_type=QuestionType.MSQ, correct_answer="A, C")

    assert is_correct_answer(question, "c, a")


def test_msq_scoring_rejects_an_extra_option() -> None:
    question = Question(question_type=QuestionType.MSQ, correct_answer="A, C")

    assert not is_correct_answer(question, "A, B, C")
