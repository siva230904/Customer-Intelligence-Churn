import os
import sys
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine, text

# ============================================================
# ADD PROJECT ROOT TO PYTHON PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ============================================================
# IMPORT PREDICTION FUNCTION
# ============================================================

from predict import predict_churn


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_URL = "mysql+pymysql://root:root@localhost:3306/custchurn"

engine = create_engine(DB_URL)


# ============================================================
# LOAD CUSTOMER FEATURES
# ============================================================

def load_customer_features(engine):

    query = """
        SELECT
            customer_id,
            tenure,
            monthly_charges,
            contract,
            service_count
        FROM customer_ml_features
    """

    df = pd.read_sql(query, engine)

    return df


# ============================================================
# SCORE ONE CUSTOMER
# ============================================================

def score_customer(row):

    try:

        result = predict_churn(
            tenure=int(row["tenure"]),
            monthly_charges=float(row["monthly_charges"]),
            contract_type=row["contract"],
            service_count=int(row["service_count"])
        )

        return pd.Series({
            "risk_score": float(result["risk_score"]),
            "prediction": result["prediction"],
            "confidence": float(result["confidence"])
        })

    except Exception as e:

        print(
            f"Prediction failed for customer "
            f"{row['customer_id']}: {e}"
        )

        return pd.Series({
            "risk_score": None,
            "prediction": None,
            "confidence": None
        })


# ============================================================
# BATCH SCORING
# ============================================================

def batch_score(df):

    print("\n========================================")
    print("SCORING CUSTOMERS")
    print("========================================")

    print(f"Customers to score: {len(df)}")

    predictions = df.apply(
        score_customer,
        axis=1
    )

    df = pd.concat(
        [
            df[["customer_id"]],
            predictions
        ],
        axis=1
    )

    df["scoring_date"] = datetime.today().strftime(
        "%Y-%m-%d"
    )

    return df


# ============================================================
# SAVE RESULTS TO SQL
# ============================================================

def save_to_database(df, engine):

    print("\n========================================")
    print("SAVING CUSTOMER RISK TABLE")
    print("========================================")

    df.to_sql(
        "customer_risk_table",
        engine,
        if_exists="replace",
        index=False
    )

    print(
        f"Saved {len(df)} rows "
        "to customer_risk_table"
    )


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(df):

    print("\n========================================")
    print("PREDICTION SUMMARY")
    print("========================================")

    counts = df["prediction"].value_counts()

    likely = counts.get(
        "Likely to churn",
        0
    )

    unlikely = counts.get(
        "Unlikely to churn",
        0
    )

    total = len(df)

    print(f"Total customers       : {total}")
    print(f"Likely to churn       : {likely}")
    print(f"Unlikely to churn     : {unlikely}")

    if total > 0:

        predicted_rate = likely / total

        print(
            f"Predicted churn rate  : "
            f"{predicted_rate:.2%}"
        )


# ============================================================
# TOP 10 HIGH-RISK CUSTOMERS
# ============================================================

def print_top_risk_customers(df):

    print("\n========================================")
    print("TOP 10 HIGHEST-RISK CUSTOMERS")
    print("========================================")

    top10 = (
        df
        .sort_values(
            "risk_score",
            ascending=False
        )
        .head(10)
    )

    print(
        top10[
            [
                "customer_id",
                "risk_score",
                "prediction",
                "confidence",
                "scoring_date"
            ]
        ].to_string(index=False)
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n========================================")
    print("ML5 — BATCH CUSTOMER SCORING")
    print("========================================")

    try:

        # ----------------------------------------
        # 1. Load features
        # ----------------------------------------

        df = load_customer_features(engine)

        print(
            f"Loaded customer features: "
            f"{len(df)} rows"
        )

        # ----------------------------------------
        # 2. Basic validation
        # ----------------------------------------

        required_columns = [
            "customer_id",
            "tenure",
            "monthly_charges",
            "contract",
            "service_count"
        ]

        missing = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing:

            raise ValueError(
                f"Missing required columns: {missing}"
            )

        # ----------------------------------------
        # 3. Batch score
        # ----------------------------------------

        risk_df = batch_score(df)

        # ----------------------------------------
        # 4. Check result count
        # ----------------------------------------

        if len(risk_df) != len(df):

            raise ValueError(
                "Scoring row count does not "
                "match input row count"
            )

        print(
            f"\nScoring row count check: PASS "
            f"({len(risk_df)} rows)"
        )

        # ----------------------------------------
        # 5. Save to SQL
        # ----------------------------------------

        save_to_database(
            risk_df,
            engine
        )

        # ----------------------------------------
        # 6. Summary
        # ----------------------------------------

        print_summary(risk_df)

        # ----------------------------------------
        # 7. Top 10
        # ----------------------------------------

        print_top_risk_customers(
            risk_df
        )

        # ----------------------------------------
        # 8. Final validation
        # ----------------------------------------

        null_count = (
            risk_df[
                [
                    "risk_score",
                    "prediction",
                    "confidence"
                ]
            ]
            .isnull()
            .sum()
            .sum()
        )

        if null_count == 0:

            print(
                "\nPrediction NULL check: PASS"
            )

        else:

            print(
                f"\nPrediction NULL check: "
                f"FAIL ({null_count} NULL values)"
            )

        print("\n========================================")
        print("ML5 COMPLETE")
        print("========================================")

    except Exception as e:

        print("\n========================================")
        print("ML5 FAILED")
        print("========================================")

        print(type(e).__name__)
        print(e)

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()