from sqlalchemy import text
from sqlalchemy.orm import Session


def get_churn_summary(db: Session):

    # ========================================================
    # TOTAL CUSTOMERS + CHURNED
    # ========================================================

    summary_query = text("""
        SELECT
            COUNT(*) AS total_customers,
            SUM(churn) AS churned
        FROM fact_customer_account
    """)

    summary_result = (
        db.execute(summary_query)
        .mappings()
        .first()
    )

    total_customers = summary_result["total_customers"]

    churned = summary_result["churned"] or 0


    # ========================================================
    # CHURN RATE
    # ========================================================

    if total_customers > 0:
        churn_rate = churned / total_customers
    else:
        churn_rate = 0.0


    # ========================================================
    # CONTRACT CHURN
    # ========================================================

    contract_query = text("""
        SELECT
            dc.contract_name AS contract_type,
            AVG(fca.churn) AS churn_rate

        FROM fact_customer_account AS fca

        JOIN dim_contract AS dc
            ON fca.contract_id = dc.contract_id

        GROUP BY dc.contract_name

        ORDER BY churn_rate DESC
    """)

    contract_results = (
        db.execute(contract_query)
        .mappings()
        .all()
    )


    by_contract = [

        {
            "contract_type": row["contract_type"],
            "churn_rate": round(
                float(row["churn_rate"]),
                4
            )
        }

        for row in contract_results
    ]


    # ========================================================
    # INTERNET SERVICE CHURN
    # ========================================================

    internet_query = text("""
        SELECT
            s.InternetService AS internet_service,
            AVG(fca.churn) AS churn_rate

        FROM fact_customer_account AS fca

        JOIN stg_customer_raw AS s
            ON fca.customer_id = s.customerID

        GROUP BY s.InternetService

        ORDER BY churn_rate DESC
    """)

    internet_results = (
        db.execute(internet_query)
        .mappings()
        .all()
    )


    by_internet_service = [

        {
            "internet_service": row["internet_service"],
            "churn_rate": round(
                float(row["churn_rate"]),
                4
            )
        }

        for row in internet_results
    ]


    return {
        "total_customers": total_customers,
        "churned": churned,
        "churn_rate": round(churn_rate, 4),
        "by_contract": by_contract,
        "by_internet_service": by_internet_service
    }