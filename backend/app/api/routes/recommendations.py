from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.recommendations import RecommendationResponse
from app.services.recommendations import get_next_action

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/next", response_model=RecommendationResponse)
def read_next_recommendation(current_user: Annotated[User, Depends(get_current_user)], database: Annotated[Session, Depends(get_db)]) -> RecommendationResponse:
    return RecommendationResponse.model_validate(get_next_action(database, current_user.id).__dict__)
