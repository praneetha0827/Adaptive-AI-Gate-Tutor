from app.models.curriculum import CurriculumStatus, Prerequisite


def test_curriculum_status_values_are_stable() -> None:
    assert [status.value for status in CurriculumStatus] == ["draft", "published", "retired"]


def test_prerequisite_has_two_distinct_endpoints() -> None:
    constraints = {constraint.name for constraint in Prerequisite.__table__.constraints}
    assert "ck_prerequisite_not_self" in constraints
    assert "uq_prerequisite_edge" in constraints
