from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.assignments import AssignTopicRequest, AssignTopicResponse
from app.services.assignments import assign_topic

router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("/assign", response_model=AssignTopicResponse, status_code=status.HTTP_201_CREATED)
def assign_manual_topic(payload: AssignTopicRequest, current_user: Annotated[User, Depends(get_current_user)], database: Annotated[Session, Depends(get_db)]) -> AssignTopicResponse:
    try:
        assignment_status, reason, prerequisite_id = assign_topic(database, current_user.id, payload.subtopic_id)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return AssignTopicResponse(status=assignment_status, subtopic_id=payload.subtopic_id, reason=reason, prerequisite_subtopic_id=prerequisite_id)
