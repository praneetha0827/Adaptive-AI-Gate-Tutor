from app.services.gamification import level_for_xp


def test_level_progression_is_deterministic() -> None:
    assert level_for_xp(0) == 1
    assert level_for_xp(100) == 2
