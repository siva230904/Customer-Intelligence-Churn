from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from database import get_db
from auth import verify_api_key

from schemas import ChurnSummary

from services.churn_service import get_churn_summary


router = APIRouter(
    prefix="/churn",
    tags=["Churn"],
    dependencies=[Depends(verify_api_key)]
)


@router.get(
    "/summary",
    response_model=ChurnSummary
)
def churn_summary(
    db: Session = Depends(get_db)
):

    try:

        return get_churn_summary(db)

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Database error while retrieving churn summary"
        )