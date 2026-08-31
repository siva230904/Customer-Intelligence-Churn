from pydantic import BaseModel
from datetime import date

class Create_customer(BaseModel):
    telecom_partner: str
    gender: str
    age: int
    state: str
    city: str
    pincode: int
    date_of_registration: date
    num_dependents: int
    estimated_salary: int
    calls_made: int
    sms_sent: int
    data_used: int
    churn: bool