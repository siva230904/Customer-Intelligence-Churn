import pandas as pd

from sqlalchemy import create_engine, text


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = (
    "mysql+pymysql://root:root@localhost/custchurn"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ============================================================
# CP4 FEATURE DEFINITIONS
# ============================================================

SERVICE_COLUMNS = [
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_t_v",
    "streaming_movies"
]


TENURE_BINS = [
    0,
    12,
    24,
    48,
    72
]


TENURE_LABELS = [
    "0-12",
    "12-24",
    "24-48",
    "48-72"
]


FEATURE_COLUMNS = [
    "tenure_bucket",
    "high_charge_flag",
    "service_count",
    "is_long_term_customer",
    "has_streaming_bundle",
    "auto_pay_flag"
]


# ============================================================
# BUILD FEATURES
# ============================================================

def build_features(engine):

    print("\n========================================")
    print("DE4 — BUILD FEATURES")
    print("========================================")


    # ========================================================
    # 1. READ CLEANED DATA
    # ========================================================

    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )

    print(
        f"Cleaned rows: {len(df)}"
    )


    # ========================================================
    # 2. CHECK REQUIRED INPUT COLUMNS
    # ========================================================

    required_input_columns = [
        "customer_id",
        "tenure",
        "monthly_charges",
        "payment_method",
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_t_v",
        "streaming_movies"
    ]


    missing_columns = [
        column
        for column in required_input_columns
        if column not in df.columns
    ]


    if missing_columns:

        raise ValueError(
            "Missing required columns in "
            f"cleaned_customers: {missing_columns}"
        )


    print(
        "Input column check: PASS"
    )


    # ========================================================
    # 3. NORMALIZE SERVICE COLUMNS
    #
    # Original values can be:
    #
    # Yes
    # No
    # No internet service
    #
    # Convert them to:
    #
    # Yes                  -> 1
    # No                   -> 0
    # No internet service  -> 0
    # ========================================================

    print("\nService column conversion:")


    for column in SERVICE_COLUMNS:

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
            .str.lower()
            .map({
                "yes": 1,
                "no": 0,
                "no internet service": 0
            })
        )


        null_count = (
            df[column]
            .isna()
            .sum()
        )


        if null_count == 0:

            print(
                f"PASS — {column}: "
                f"converted to 0/1"
            )

        else:

            print(
                f"FAIL — {column}: "
                f"{null_count} invalid values"
            )

            raise ValueError(
                f"{column} contains unexpected "
                "values"
            )


    # ========================================================
    # 4. FEATURE 1 — TENURE BUCKET
    #
    # CP4:
    #
    # pd.cut()
    # bins = [0,12,24,48,72]
    # ========================================================

    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=TENURE_BINS,
        labels=TENURE_LABELS,
        include_lowest=True
    )


    # ========================================================
    # 5. FEATURE 2 — HIGH CHARGE FLAG
    #
    # CP4:
    #
    # 1 if monthly_charges > MEDIAN
    # 0 otherwise
    #
    # IMPORTANT:
    # This is MEDIAN, not average.
    # ========================================================

    median_monthly_charges = (
        df["monthly_charges"]
        .median()
    )


    print(
        f"\nMedian monthly charges: "
        f"{median_monthly_charges}"
    )


    df["high_charge_flag"] = (
        df["monthly_charges"]
        > median_monthly_charges
    ).astype(int)


    # ========================================================
    # 6. FEATURE 3 — SERVICE COUNT
    #
    # Count how many of the six service columns equal 1.
    # ========================================================

    df["service_count"] = (
        df[SERVICE_COLUMNS]
        .sum(axis=1)
        .astype(int)
    )


    # ========================================================
    # 7. FEATURE 4 — IS LONG-TERM CUSTOMER
    #
    # tenure >= 24 -> 1
    # otherwise    -> 0
    # ========================================================

    df["is_long_term_customer"] = (
        df["tenure"] >= 24
    ).astype(int)


    # ========================================================
    # 8. FEATURE 5 — HAS STREAMING BUNDLE
    #
    # streaming_t_v = 1
    # AND
    # streaming_movies = 1
    # ========================================================

    df["has_streaming_bundle"] = (
        (
            df["streaming_t_v"] == 1
        )
        &
        (
            df["streaming_movies"] == 1
        )
    ).astype(int)


    # ========================================================
    # 9. FEATURE 6 — AUTO PAY FLAG
    #
    # 1 if payment_method contains "automatic"
    # 0 otherwise
    # ========================================================

    df["auto_pay_flag"] = (
        df["payment_method"]
        .astype(str)
        .str.contains(
            "automatic",
            case=False,
            na=False
        )
        .astype(int)
    )


    # ========================================================
    # 10. CONVERT TENURE BUCKET TO STRING
    # ========================================================

    df["tenure_bucket"] = (
        df["tenure_bucket"]
        .astype(str)
    )


    # ========================================================
    # 11. DISPLAY CREATED FEATURES
    # ========================================================

    print("\nFeatures created:")


    for feature in FEATURE_COLUMNS:

        print(
            f"  ✓ {feature}"
        )


    # ========================================================
    # 12. CHECK FEATURE NULLS
    # ========================================================

    print("\nFeature NULL check:")


    for feature in FEATURE_COLUMNS:

        null_count = (
            df[feature]
            .isna()
            .sum()
        )


        if null_count == 0:

            print(
                f"PASS — {feature}: "
                f"NULL count = 0"
            )

        else:

            print(
                f"FAIL — {feature}: "
                f"NULL count = {null_count}"
            )

            raise ValueError(
                f"{feature} contains NULL values"
            )


    # ========================================================
    # 13. WRITE TO MYSQL
    #
    # Full reload is intentional for this batch pipeline.
    # ========================================================

    df.to_sql(
        "customer_ml_features",
        engine,
        if_exists="replace",
        index=False
    )


    print(
        "\ncustomer_ml_features populated successfully."
    )


    return df


# ============================================================
# VALIDATE ROW COUNT
# ============================================================

def validate_row_count(engine):

    print("\n========================================")
    print("ROW COUNT VALIDATION")
    print("========================================")


    with engine.connect() as connection:

        cleaned_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM cleaned_customers
            """)
        ).scalar()


        feature_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM customer_ml_features
            """)
        ).scalar()


    print(
        f"cleaned_customers: "
        f"{cleaned_count}"
    )


    print(
        f"customer_ml_features: "
        f"{feature_count}"
    )


    if cleaned_count == feature_count:

        print(
            f"PASS — row counts match: "
            f"{feature_count}"
        )

    else:

        print(
            "FAIL — row counts do not match"
        )

        raise AssertionError(
            "customer_ml_features row count "
            "does not match cleaned_customers"
        )


# ============================================================
# VALIDATE FEATURE SCHEMA
# ============================================================

def validate_features(engine):

    print("\n========================================")
    print("FEATURE SCHEMA VALIDATION")
    print("========================================")


    # ========================================================
    # CHECK THAT ALL SIX FEATURES EXIST
    # ========================================================

    with engine.connect() as connection:

        result = connection.execute(
            text("""
                DESCRIBE customer_ml_features
            """)
        )


        actual_columns = {
            row[0]
            for row in result
        }


    missing_features = [
        feature
        for feature in FEATURE_COLUMNS
        if feature not in actual_columns
    ]


    if missing_features:

        print(
            "FAIL — Missing feature columns:",
            missing_features
        )

        raise AssertionError(
            f"Missing feature columns: "
            f"{missing_features}"
        )


    print(
        "PASS — all 6 feature columns exist"
    )


    # ========================================================
    # CHECK NULLS IN MYSQL
    # ========================================================

    print("\nFeature NULL validation:")


    with engine.connect() as connection:

        for feature in FEATURE_COLUMNS:

            null_count = connection.execute(
                text(
                    f"""
                    SELECT COUNT(*)
                    FROM customer_ml_features
                    WHERE `{feature}` IS NULL
                    """
                )
            ).scalar()


            if null_count == 0:

                print(
                    f"PASS — {feature}: "
                    f"NULL count = 0"
                )

            else:

                print(
                    f"FAIL — {feature}: "
                    f"NULL count = {null_count}"
                )

                raise AssertionError(
                    f"{feature} contains "
                    "NULL values"
                )


# ============================================================
# VALIDATE FEATURE VALUES
# ============================================================

def validate_feature_values(engine):

    print("\n========================================")
    print("FEATURE VALUE VALIDATION")
    print("========================================")


    with engine.connect() as connection:

        # ----------------------------------------------------
        # high_charge_flag
        # ----------------------------------------------------

        invalid_high_charge = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM customer_ml_features
                WHERE high_charge_flag
                      NOT IN (0, 1)
            """)
        ).scalar()


        if invalid_high_charge == 0:

            print(
                "PASS — high_charge_flag "
                "contains only 0/1"
            )

        else:

            raise AssertionError(
                "Invalid high_charge_flag values"
            )


        # ----------------------------------------------------
        # service_count
        # ----------------------------------------------------

        invalid_service_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM customer_ml_features
                WHERE service_count < 0
                   OR service_count > 6
            """)
        ).scalar()


        if invalid_service_count == 0:

            print(
                "PASS — service_count range is 0-6"
            )

        else:

            raise AssertionError(
                "Invalid service_count values"
            )


        # ----------------------------------------------------
        # is_long_term_customer
        # ----------------------------------------------------

        invalid_long_term = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM customer_ml_features
                WHERE is_long_term_customer
                      NOT IN (0, 1)
            """)
        ).scalar()


        if invalid_long_term == 0:

            print(
                "PASS — is_long_term_customer "
                "contains only 0/1"
            )

        else:

            raise AssertionError(
                "Invalid is_long_term_customer values"
            )


        # ----------------------------------------------------
        # has_streaming_bundle
        # ----------------------------------------------------

        invalid_streaming = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM customer_ml_features
                WHERE has_streaming_bundle
                      NOT IN (0, 1)
            """)
        ).scalar()


        if invalid_streaming == 0:

            print(
                "PASS — has_streaming_bundle "
                "contains only 0/1"
            )

        else:

            raise AssertionError(
                "Invalid has_streaming_bundle values"
            )


        # ----------------------------------------------------
        # auto_pay_flag
        # ----------------------------------------------------

        invalid_auto_pay = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM customer_ml_features
                WHERE auto_pay_flag
                      NOT IN (0, 1)
            """)
        ).scalar()


        if invalid_auto_pay == 0:

            print(
                "PASS — auto_pay_flag "
                "contains only 0/1"
            )

        else:

            raise AssertionError(
                "Invalid auto_pay_flag values"
            )


# ============================================================
# SPOT CHECK
# ============================================================

def spot_check(engine):

    print("\n========================================")
    print("FEATURE SPOT CHECK")
    print("========================================")


    query = text("""
        SELECT
            customer_id,
            tenure,
            tenure_bucket,
            monthly_charges,
            high_charge_flag,
            service_count,
            is_long_term_customer,
            has_streaming_bundle,
            auto_pay_flag

        FROM customer_ml_features

        LIMIT 3
    """)


    with engine.connect() as connection:

        results = (
            connection.execute(query)
            .mappings()
            .all()
        )


    for row in results:

        print(
            "\n----------------------------------------"
        )


        print(
            "Customer ID:",
            row["customer_id"]
        )


        print(
            "Tenure:",
            row["tenure"]
        )


        print(
            "Tenure bucket:",
            row["tenure_bucket"]
        )


        print(
            "Monthly charges:",
            row["monthly_charges"]
        )


        print(
            "High charge flag:",
            row["high_charge_flag"]
        )


        print(
            "Service count:",
            row["service_count"]
        )


        print(
            "Long-term customer:",
            row["is_long_term_customer"]
        )


        print(
            "Streaming bundle:",
            row["has_streaming_bundle"]
        )


        print(
            "Auto pay:",
            row["auto_pay_flag"]
        )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # STEP 1 — Build feature table
    # --------------------------------------------------------

    build_features(
        engine
    )


    # --------------------------------------------------------
    # STEP 2 — Validate row count
    # --------------------------------------------------------

    validate_row_count(
        engine
    )


    # --------------------------------------------------------
    # STEP 3 — Validate schema + NULLs
    # --------------------------------------------------------

    validate_features(
        engine
    )


    # --------------------------------------------------------
    # STEP 4 — Validate feature values
    # --------------------------------------------------------

    validate_feature_values(
        engine
    )


    # --------------------------------------------------------
    # STEP 5 — Spot check
    # --------------------------------------------------------

    spot_check(
        engine
    )


    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print("\n========================================")
    print("DE4 COMPLETE")
    print("========================================")


# ============================================================
# RUN SCRIPT
# ============================================================

if __name__ == "__main__":

    main()