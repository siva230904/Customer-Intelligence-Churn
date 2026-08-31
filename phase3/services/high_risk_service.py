from sqlalchemy import text
from sqlalchemy.orm import Session


def get_high_risk_customers(
    db: Session,
    limit: int = 50,
    min_tenure: int | None = None,
    max_tenure: int | None = None
):

    # ========================================================
    # BASE QUERY
    # ========================================================

    query_string = """
        SELECT
            customer_id,
            tenure,
            monthly_charges,
            contract AS contract_type,
            risk_reason

        FROM v_high_risk_customers

        WHERE 1 = 1
    """


    # ========================================================
    # PARAMETERS
    # ========================================================

    params = {}


    # ========================================================
    # MIN TENURE
    # ========================================================

    if min_tenure is not None:

        query_string += """
            AND tenure >= :min_tenure
        """

        params["min_tenure"] = min_tenure


    # ========================================================
    # MAX TENURE
    # ========================================================

    if max_tenure is not None:

        query_string += """
            AND tenure <= :max_tenure
        """

        params["max_tenure"] = max_tenure


    # ========================================================
    # RANKING
    # ========================================================

    query_string += """
        ORDER BY monthly_charges DESC
    """


    # ========================================================
    # LIMIT
    # ========================================================

    query_string += """
        LIMIT :limit
    """

    params["limit"] = limit


    # ========================================================
    # EXECUTE QUERY
    # ========================================================

    query = text(query_string)

    results = (
        db.execute(
            query,
            params
        )
        .mappings()
        .all()
    )


    # ========================================================
    # RETURN RESULTS
    # ========================================================

    return [

        {
            "customer_id": row["customer_id"],
            "tenure": row["tenure"],
            "monthly_charges": float(
                row["monthly_charges"]
            ),
            "contract_type": row["contract_type"],
            "risk_reason": row["risk_reason"]
        }

        for row in results
    ]