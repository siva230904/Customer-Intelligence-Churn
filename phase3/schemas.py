from pydantic import BaseModel


# ============================================================
# API1 — Customer Response
# ============================================================

class CustomerResponse(BaseModel):

    customer_id: str
    tenure: int
    contract_type: str
    internet_service: str
    monthly_charges: float
    churn: int


# ============================================================
# API2 — Contract Churn
# ============================================================

class ContractChurn(BaseModel):

    contract_type: str
    churn_rate: float


# ============================================================
# API2 — Internet Service Churn
# ============================================================

class InternetServiceChurn(BaseModel):

    internet_service: str
    churn_rate: float


# ============================================================
# API2 — Churn Summary
# ============================================================

class ChurnSummary(BaseModel):

    total_customers: int

    churned: int

    churn_rate: float

    by_contract: list[ContractChurn]

    by_internet_service: list[InternetServiceChurn]

# ============================================================
# API3 — HIGH-RISK CUSTOMER
# ============================================================

class HighRiskCustomer(BaseModel):

    customer_id: str

    tenure: int

    monthly_charges: float

    contract_type: str

    risk_reason: str

# ============================================================
# API4 — CUSTOMER FEATURES
# ============================================================

class CustomerFeatures(BaseModel):

    customer_id: str

    service_count: int

    tenure_bucket: str

    high_charge_flag: int

    is_long_term_customer: int

    has_streaming_bundle: int

    auto_pay_flag: int

    monthly_charges: float

    total_charges: float

# ============================================================
# API5 — PREDICTION REQUEST
# ============================================================

class ChurnPredictionRequest(BaseModel):

    tenure: int

    monthly_charges: float

    contract_type: str

    service_count: int


# ============================================================
# API5 — PREDICTION RESPONSE
# ============================================================

class ChurnPredictionResponse(BaseModel):

    customer_id: str

    risk_score: float

    prediction: str

    note: str

# ============================================================
# API6 — ERROR RESPONSE
# ============================================================

class ErrorResponse(BaseModel):

    detail: str

    status_code: int