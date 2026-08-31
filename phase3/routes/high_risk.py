from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas import HighRiskCustomer
from services.high_risk_service import get_high_risk_customers


router = APIRouter(
    prefix="/customers",
    tags=["High Risk Customers"]
)


# ============================================================
# GET HIGH-RISK CUSTOMERS
# ============================================================

@router.get(
    "/high-risk",
    response_model=list[HighRiskCustomer]
)
def high_risk_customers(

    limit: int = Query(
        default=50,
        ge=1,
        le=500
    ),

    min_tenure: int | None = Query(
        default=None,
        ge=0
    ),

    max_tenure: int | None = Query(
        default=None,
        ge=0
    ),

    db: Session = Depends(get_db)
):

    return get_high_risk_customers(
        db=db,
        limit=limit,
        min_tenure=min_tenure,
        max_tenure=max_tenure
    )