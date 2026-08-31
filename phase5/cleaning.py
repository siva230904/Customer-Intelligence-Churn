import pandas as pd

from sqlalchemy import create_engine, text
from customer_cleaner import CustomerCleaner

# IMPORTANT:
# Replace this import with the actual location of your
# CP2 CustomerCleaner.
#
# Example:
# from phase1.customer_cleaner import CustomerCleaner


DATABASE_URL = (
    "mysql+pymysql://root:root@localhost/custchurn"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

def clean_staging(engine):

    print("\n========================================")
    print("DE3 — CLEAN STAGING")
    print("========================================")


    # ========================================================
    # READ STAGING
    # ========================================================

    df = pd.read_sql(
        "SELECT * FROM stg_customer_raw",
        engine
    )

    print(
        f"Staging rows: {len(df)}"
    )


    # ========================================================
    # RUN EXISTING CUSTOMER CLEANER
    # ========================================================

    cleaner = CustomerCleaner(df)

    cleaned_df = cleaner.clean()
    # ========================================================
    # STANDARDIZE CUSTOMER ID
    # ========================================================

    if "customer_i_d" in cleaned_df.columns:

        cleaned_df = cleaned_df.rename(
            columns={
                "customer_i_d": "customer_id"
            }
        )

    print(
        f"Cleaned rows: {len(cleaned_df)}"
    )


    # ========================================================
    # WRITE CLEANED DATA
    # ========================================================

    cleaned_df.to_sql(
        "cleaned_customers",
        engine,
        if_exists="replace",
        index=False
    )


    # ========================================================
    # ROW COUNT CHECK
    # ========================================================

    staging_count = len(df)

    cleaned_count = len(cleaned_df)


    print("\nRow Count Check")

    if cleaned_count == staging_count:

        print(
            f"PASS — staging={staging_count}, "
            f"cleaned={cleaned_count}"
        )

    else:

        print(
            f"FAIL — staging={staging_count}, "
            f"cleaned={cleaned_count}"
        )

        raise AssertionError(
            "Cleaned row count does not match staging row count"
        )


    return cleaned_df

def run_quality_checks(
    cleaned_df
):

    print("\n========================================")
    print("DATA QUALITY REPORT")
    print("========================================")


    # ========================================================
    # CHECK 1 — CUSTOMER ID NULL
    # ========================================================

    null_customer_id = (
        cleaned_df["customer_id"]
        .isna()
        .sum()
    )

    if null_customer_id == 0:

        print(
            f"PASS — customer_id NULL count = "
            f"{null_customer_id}"
        )

    else:

        print(
            f"FAIL — customer_id NULL count = "
            f"{null_customer_id}"
        )

        raise AssertionError(
            "customer_id contains NULL values"
        )


    # ========================================================
    # CHECK 2 — MONTHLY CHARGES NULL
    # ========================================================

    null_monthly_charges = (
        cleaned_df["monthly_charges"]
        .isna()
        .sum()
    )

    if null_monthly_charges == 0:

        print(
            f"PASS — monthly_charges NULL count = "
            f"{null_monthly_charges}"
        )

    else:

        print(
            f"FAIL — monthly_charges NULL count = "
            f"{null_monthly_charges}"
        )

        raise AssertionError(
            "monthly_charges contains NULL values"
        )


    # ========================================================
    # CHECK 3 — CHURN VALUES
    # ========================================================

    invalid_churn = (
        ~cleaned_df["churn"]
        .isin([0, 1])
    ).sum()


    if invalid_churn == 0:

        print(
            f"PASS — invalid churn count = "
            f"{invalid_churn}"
        )

    else:

        print(
            f"FAIL — invalid churn count = "
            f"{invalid_churn}"
        )

        raise AssertionError(
            "churn contains values other than 0 or 1"
        )


    print("\nAll data-quality checks passed.")

def build_curated_tables(engine):

    print("\n========================================")
    print("BUILDING CURATED TABLES")
    print("========================================")


    with engine.begin() as connection:

        # ====================================================
        # 1. DIM CONTRACT
        # ====================================================

        connection.execute(
            text("""
                INSERT INTO dim_contract
                (
                    contract_name
                )

                SELECT DISTINCT
                    contract

                FROM cleaned_customers

                WHERE contract IS NOT NULL

                ON DUPLICATE KEY UPDATE
                    contract_name =
                        VALUES(contract_name)
            """)
        )

        print(
            "dim_contract populated"
        )


        # ====================================================
        # 2. DIM PAYMENT
        # ====================================================

        connection.execute(
            text("""
                INSERT INTO dim_payment
                (
                    payment_method
                )

                SELECT DISTINCT
                    payment_method

                FROM cleaned_customers

                WHERE payment_method IS NOT NULL

                ON DUPLICATE KEY UPDATE
                    payment_method =
                        VALUES(payment_method)
            """)
        )

        print(
            "dim_payment populated"
        )


        # ====================================================
        # 3. CUSTOMERS
        #
        # Only customer attributes belong here.
        # contract_id/payment_id do NOT belong here.
        # ====================================================

        connection.execute(
            text("""
                INSERT INTO customers
                (
                    customer_id,
                    gender,
                    senior_citizen,
                    partner,
                    dependents
                )

                SELECT
                    customer_id,
                    gender,
                    senior_citizen,
                    partner,
                    dependents

                FROM cleaned_customers

                ON DUPLICATE KEY UPDATE

                    gender =
                        VALUES(gender),

                    senior_citizen =
                        VALUES(senior_citizen),

                    partner =
                        VALUES(partner),

                    dependents =
                        VALUES(dependents)
            """)
        )

        print(
            "customers populated"
        )


        # ====================================================
        # 4. FACT CUSTOMER ACCOUNT
        #
        # Contract/payment foreign keys belong here.
        # ====================================================

        connection.execute(
            text("""
                INSERT INTO fact_customer_account
                (
                    customer_id,
                    contract_id,
                    payment_id,
                    tenure,
                    monthly_charges,
                    total_charges,
                    churn
                )

                SELECT
                    cc.customer_id,
                    dc.contract_id,
                    dp.payment_id,
                    cc.tenure,
                    cc.monthly_charges,
                    cc.total_charges,
                    cc.churn

                FROM cleaned_customers cc

                LEFT JOIN dim_contract dc
                    ON cc.contract =
                       dc.contract_name

                LEFT JOIN dim_payment dp
                    ON cc.payment_method =
                       dp.payment_method

                ON DUPLICATE KEY UPDATE

                    contract_id =
                        VALUES(contract_id),

                    payment_id =
                        VALUES(payment_id),

                    tenure =
                        VALUES(tenure),

                    monthly_charges =
                        VALUES(monthly_charges),

                    total_charges =
                        VALUES(total_charges),

                    churn =
                        VALUES(churn)
            """)
        )

        print(
            "fact_customer_account populated"
        )

def verify_curated_tables(engine):

    print("\n========================================")
    print("CURATED TABLE COUNTS")
    print("========================================")


    tables = [
        "dim_contract",
        "dim_payment",
        "customers",
        "fact_customer_account"
    ]


    with engine.connect() as connection:

        for table in tables:

            result = connection.execute(
                text(
                    f"SELECT COUNT(*) FROM {table}"
                )
            )

            count = result.scalar()

            print(
                f"{table}: {count}"
            )

def main():

    # --------------------------------------------------------
    # Step 1 — staging → cleaned
    # --------------------------------------------------------

    cleaned_df = clean_staging(
        engine
    )


    # --------------------------------------------------------
    # Step 2 — quality checks
    # --------------------------------------------------------

    run_quality_checks(
        cleaned_df
    )


    # --------------------------------------------------------
    # Step 3 — cleaned → curated
    # --------------------------------------------------------

    build_curated_tables(
        engine
    )


    # --------------------------------------------------------
    # Step 4 — verification
    # --------------------------------------------------------

    verify_curated_tables(
        engine
    )


    print("\n========================================")
    print("DE3 COMPLETE")
    print("========================================")


if __name__ == "__main__":

    main()
