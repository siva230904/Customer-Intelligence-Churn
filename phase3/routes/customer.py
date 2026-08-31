from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from auth import verify_api_key
from schemas import CustomerResponse


router = APIRouter(
    prefix="/customer",
    tags=["Customer"],
    dependencies=[Depends(verify_api_key)]
)


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse
)
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db)
):

    try:

        query = text("""
            SELECT
                c.customer_id,
                fca.tenure,
                dc.contract_name AS contract_type,
                s.InternetService AS internet_service,
                fca.monthly_charges,
                fca.churn

            FROM customers AS c

            JOIN fact_customer_account AS fca
                ON c.customer_id = fca.customer_id

            JOIN dim_contract AS dc
                ON fca.contract_id = dc.contract_id

            JOIN stg_customer_raw AS s
                ON c.customer_id = s.customerID

            WHERE c.customer_id = :customer_id
        """)

        result = (
            db.execute(
                query,
                {"customer_id": customer_id}
            )
            .mappings()
            .first()
        )

        if result is None:

            raise HTTPException(
                status_code=404,
                detail=f"Customer '{customer_id}' not found"
            )

        return CustomerResponse(
            customer_id=result["customer_id"],
            tenure=result["tenure"],
            contract_type=result["contract_type"],
            internet_service=result["internet_service"],
            monthly_charges=float(
                result["monthly_charges"]
            ),
            churn=result["churn"]
        )

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Database error while retrieving customer"
        )