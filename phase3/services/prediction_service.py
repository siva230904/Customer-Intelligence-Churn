from predict import predict_churn


def get_churn_prediction(
    tenure: int,
    monthly_charges: float,
    contract_type: str,
    service_count: int
):
    return predict_churn(
        tenure=tenure,
        monthly_charges=monthly_charges,
        contract_type=contract_type,
        service_count=service_count
    )