from fastapi import APIRouter, HTTPException

from schemas import ChurnPredictionRequest

from services.prediction_service import (
    get_churn_prediction
)


router = APIRouter()


@router.post("/predict-churn")
def predict_churn_endpoint(
    request: ChurnPredictionRequest
):

    try:

        result = get_churn_prediction(
            tenure=request.tenure,
            monthly_charges=request.monthly_charges,
            contract_type=request.contract_type,
            service_count=request.service_count
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )