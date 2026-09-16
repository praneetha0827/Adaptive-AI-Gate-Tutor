from app.schemas.assignments import AssignTopicRequest


def test_assignment_requires_a_subtopic() -> None:
    assert AssignTopicRequest(subtopic_id="subtopic").subtopic_id == "subtopic"
