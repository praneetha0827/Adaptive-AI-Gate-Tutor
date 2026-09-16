from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.providers.factory import get_tutor_provider
from app.providers.openai import AIProviderError
from app.schemas.tutor import SendTutorMessageRequest, StartTutorSessionRequest, TutorSessionResponse, TutorTurn
from app.services.tutor import continue_session, create_session
from app.services.recommendations import get_next_action
from app.services.assignments import get_unmet_prerequisite

router = APIRouter(prefix="/tutor", tags=["tutor"])


@router.post("/sessions", response_model=TutorSessionResponse, status_code=status.HTTP_201_CREATED)
def start_tutor_session(payload: StartTutorSessionRequest, current_user: Annotated[User, Depends(get_current_user)], database: Annotated[Session, Depends(get_db)]) -> TutorSessionResponse:
    try:
        prerequisite = get_unmet_prerequisite(database, current_user.id, payload.subtopic_id)
        if prerequisite is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Study the prerequisite {prerequisite.title} first")
        session, turn = create_session(database, current_user.id, payload.subtopic_id, get_tutor_provider())
        return TutorSessionResponse(session_id=session.id, turn=turn)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except AIProviderError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.post("/sessions/{session_id}/messages", response_model=TutorTurn)
def send_tutor_message(session_id: str, payload: SendTutorMessageRequest, current_user: Annotated[User, Depends(get_current_user)], database: Annotated[Session, Depends(get_db)]) -> TutorTurn:
    try:
        return continue_session(database, current_user.id, session_id, payload.message, get_tutor_provider())
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except AIProviderError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.post("/recommended-session", response_model=TutorSessionResponse, status_code=status.HTTP_201_CREATED)
def start_recommended_tutor_session(current_user: Annotated[User, Depends(get_current_user)], database: Annotated[Session, Depends(get_db)]) -> TutorSessionResponse:
    recommendation = get_next_action(database, current_user.id)
    if recommendation.subtopic_id is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Complete a diagnostic assessment before starting a recommended lesson")
    try:
        session, turn = create_session(database, current_user.id, recommendation.subtopic_id, get_tutor_provider())
        return TutorSessionResponse(session_id=session.id, turn=turn)
    except AIProviderError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
