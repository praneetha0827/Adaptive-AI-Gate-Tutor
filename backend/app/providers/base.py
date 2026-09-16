from typing import Protocol

from app.schemas.tutor import TutorTurn


class TutorProvider(Protocol):
    def generate_tutor_turn(self, context: dict[str, object], user_message: str) -> TutorTurn: ...

