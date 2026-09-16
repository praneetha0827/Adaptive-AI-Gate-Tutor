from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.curriculum import CurriculumVersionResponse, SubjectResponse
from app.services.curriculum import list_published_versions, list_subjects

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


@router.get("/versions", response_model=list[CurriculumVersionResponse])
def read_published_versions(database: Annotated[Session, Depends(get_db)]) -> list[CurriculumVersionResponse]:
    return list_published_versions(database)


@router.get("/subjects", response_model=list[SubjectResponse])
def read_subjects(
    curriculum_version_id: Annotated[str, Query(min_length=1)],
    database: Annotated[Session, Depends(get_db)],
) -> list[SubjectResponse]:
    subjects = list_subjects(database, curriculum_version_id)
    if not subjects:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curriculum version has no subjects")
    return subjects

