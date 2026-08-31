from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.orm import declarative_base


Base = declarative_base()


# ============================================================
# CUSTOMERS
# ============================================================

class Customer(Base):

    __tablename__ = "customers"

    customer_id = Column(
        String(50),
        primary_key=True
    )

    gender = Column(
        String(20)
    )

    senior_citizen = Column(
        Integer
    )

    partner = Column(
        Integer
    )

    dependents = Column(
        Integer
    )

    contract_id = Column(
        Integer
    )

    payment_id = Column(
        Integer
    )


# ============================================================
# FACT CUSTOMER ACCOUNT
# ============================================================

class FactCustomerAccount(Base):

    __tablename__ = "fact_customer_account"

    customer_id = Column(
        String(50),
        primary_key=True
    )

    contract_id = Column(
        Integer
    )

    payment_id = Column(
        Integer
    )

    tenure = Column(
        Integer
    )

    monthly_charges = Column(
        Float
    )

    total_charges = Column(
        Float
    )

    churn = Column(
        Integer
    )


# ============================================================
# DIM CONTRACT
# ============================================================

class DimContract(Base):

    __tablename__ = "dim_contract"

    contract_id = Column(
        Integer,
        primary_key=True
    )

    contract_name = Column(
        String(50)
    )