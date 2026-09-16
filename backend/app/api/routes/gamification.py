from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.gamification import progression_summary

router = APIRouter(prefix="/progression", tags=["progression"])


class ProgressionResponse(BaseModel):
    total_xp: int
    level: int
    xp_to_next_level: int
    streak_days: int


@router.get("/summary", response_model=ProgressionResponse)
def read_progression(current_user: Annotated[User, Depends(get_current_user)], database: Annotated[Session, Depends(get_db)]) -> ProgressionResponse:
    return progression_summary(database, current_user.id)
