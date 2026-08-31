from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from auth import verify_api_key

from schemas import CustomerFeatures


router = APIRouter(
    prefix="/customer",
    tags=["Customer Features"],
    dependencies=[Depends(verify_api_key)]
)


@router.get(
    "/{customer_id}/features",
    response_model=CustomerFeatures
)
def get_customer_features(
    customer_id: str,
    db: Session = Depends(get_db)
):

    try:

        query = text("""
            SELECT
                customer_id,
                service_count,
                tenure_bucket,
                high_charge_flag,
                is_long_term_customer,
                has_streaming_bundle,
                auto_pay_flag,
                monthly_charges,
                total_charges

            FROM customer_ml_features

            WHERE customer_id = :customer_id
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
                detail=f"Customer '{customer_id}' features not found"
            )


        return CustomerFeatures(

            customer_id=result["customer_id"],

            service_count=result["service_count"],

            tenure_bucket=result["tenure_bucket"],

            high_charge_flag=result["high_charge_flag"],

            is_long_term_customer=(
                result["is_long_term_customer"]
            ),

            has_streaming_bundle=(
                result["has_streaming_bundle"]
            ),

            auto_pay_flag=result["auto_pay_flag"],

            monthly_charges=float(
                result["monthly_charges"]
            ),

            total_charges=float(
                result["total_charges"]
            )
        )


    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Database error while retrieving customer features"
        )