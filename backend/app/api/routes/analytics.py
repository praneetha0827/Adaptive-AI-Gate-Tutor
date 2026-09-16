from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsOverview
from app.services.analytics import analytics_overview

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def read_analytics_overview(current_user: Annotated[User, Depends(get_current_user)], database: Annotated[Session, Depends(get_db)]) -> AnalyticsOverview:
    return AnalyticsOverview.model_validate(analytics_overview(database, current_user.id))
