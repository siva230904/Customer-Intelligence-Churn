import pandas as pd
from sqlalchemy import create_engine, text


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_USER = "root"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "custchurn"

DATABASE_URL = (
    f"mysql+pymysql://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}"
    f"/{DB_NAME}"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def create_db_engine():

    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )


# ============================================================
# LOAD CUSTOMER ML FEATURES
# ============================================================

def load_ml_features(engine):

    query = text("""
        SELECT *
        FROM customer_ml_features
    """)

    return pd.read_sql(
        query,
        engine
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n========================================")
    print("ML1 — DEFINE ML PROBLEM")
    print("========================================")

    engine = create_db_engine()

    # --------------------------------------------------------
    # 1. Load data
    # --------------------------------------------------------

    df = load_ml_features(engine)

    print("\nLoaded customer_ml_features")

    print(
        f"Rows    : {df.shape[0]}"
    )

    print(
        f"Columns : {df.shape[1]}"
    )


    # --------------------------------------------------------
    # 2. Display actual columns
    # --------------------------------------------------------

    print("\n========================================")
    print("INPUT COLUMNS")
    print("========================================")

    for column in df.columns:
        print(f"- {column}")


    # ========================================================
    # 3. DEFINE TARGET
    # ========================================================

    TARGET = "churn"

    if TARGET not in df.columns:

        raise ValueError(
            "churn column does not exist."
        )

    print("\nTarget:")
    print("churn")


    # ========================================================
    # 4. DEFINE IDENTIFIER TO DROP
    # ========================================================

    ID_COLUMN = "customer_id"

    if ID_COLUMN not in df.columns:

        raise ValueError(
            "customer_id column does not exist."
        )

    print("\nIdentifier to drop:")
    print("customer_id")


    # ========================================================
    # 5. DEFINE CATEGORICAL FEATURES
    # ========================================================

    categorical_columns = [

        "gender",

        "multiple_lines",

        "internet_service",

        "contract",

        "payment_method",

        "tenure_bucket"
    ]


    # Verify they exist

    missing_categorical = [

        col
        for col in categorical_columns
        if col not in df.columns
    ]

    if missing_categorical:

        raise ValueError(
            f"Missing categorical columns: "
            f"{missing_categorical}"
        )


    print("\n========================================")
    print("CATEGORICAL FEATURES")
    print("========================================")

    for col in categorical_columns:

        print(f"- {col}")


    # ========================================================
    # 6. NUMERIC FEATURES
    # ========================================================

    numeric_columns = [

        "senior_citizen",

        "partner",

        "dependents",

        "tenure",

        "phone_service",

        "online_security",

        "online_backup",

        "device_protection",

        "tech_support",

        "streaming_t_v",

        "streaming_movies",

        "paperless_billing",

        "monthly_charges",

        "total_charges",

        "high_charge_flag",

        "service_count",

        "is_long_term_customer",

        "has_streaming_bundle",

        "auto_pay_flag"
    ]


    # Keep only columns that exist

    numeric_columns = [

        col
        for col in numeric_columns
        if col in df.columns
    ]


    print("\n========================================")
    print("NUMERIC FEATURES")
    print("========================================")

    for col in numeric_columns:

        print(f"- {col}")


    # ========================================================
    # 7. GENDER
    # ========================================================
    #
    # gender is categorical in your table.
    #
    # Example:
    #
    # Male
    # Female
    #
    # get_dummies() will convert this into:
    #
    # gender_Female
    # gender_Male
    #
    # ========================================================


    # ========================================================
    # 8. BUILD INITIAL X
    # ========================================================

    feature_columns = (

        numeric_columns
        +
        categorical_columns
    )


    X = df[
        feature_columns
    ].copy()


    # ========================================================
    # 9. BUILD TARGET y
    # ========================================================

    y = df[
        TARGET
    ].copy()


    # ========================================================
    # 10. ONE-HOT ENCODING
    # ========================================================

    print("\n========================================")
    print("ONE-HOT ENCODING")
    print("========================================")

    print(
        "Encoding:",
        categorical_columns
    )


    X = pd.get_dummies(

        X,

        columns=categorical_columns,

        drop_first=False,

        dtype=int
    )


    # ========================================================
    # 11. CONVERT NUMERIC COLUMNS
    # ========================================================

    for col in numeric_columns:

        X[col] = pd.to_numeric(

            X[col],

            errors="coerce"
        )


    # ========================================================
    # 12. CONVERT TARGET
    # ========================================================

    y = pd.to_numeric(

        y,

        errors="coerce"
    )


    # ========================================================
    # 13. NULL CHECK
    # ========================================================

    print("\n========================================")
    print("NULL CHECK")
    print("========================================")

    x_nulls = X.isnull().sum().sum()

    y_nulls = y.isnull().sum()

    print(
        f"X NULL values: {x_nulls}"
    )

    print(
        f"y NULL values: {y_nulls}"
    )


    # ========================================================
    # 14. TARGET CHECK
    # ========================================================

    print("\n========================================")
    print("TARGET CHECK")
    print("========================================")

    print(
        y.value_counts()
    )


    invalid_target = (

        ~y.isin([0, 1])
    ).sum()

    print(
        f"Invalid target values: "
        f"{invalid_target}"
    )


    # ========================================================
    # 15. FINAL FEATURE SET
    # ========================================================

    print("\n========================================")
    print("FINAL FEATURE SET")
    print("========================================")

    for i, column in enumerate(
        X.columns,
        start=1
    ):

        print(
            f"{i:2}. {column}"
        )


    # ========================================================
    # 16. SHAPES
    # ========================================================

    print("\n========================================")
    print("SHAPES")
    print("========================================")

    print(
        f"X shape: {X.shape}"
    )

    print(
        f"y shape: {y.shape}"
    )


    # ========================================================
    # 17. CLASS BALANCE
    # ========================================================

    print("\n========================================")
    print("CLASS BALANCE")
    print("========================================")

    print("\nCounts:")

    print(
        y.value_counts()
    )


    print("\nProportions:")

    print(
        y.value_counts(
            normalize=True
        )
    )


    # ========================================================
    # 18. DISPLAY X
    # ========================================================

    print("\n========================================")
    print("X PREVIEW")
    print("========================================")

    print(
        X.head()
    )


    # ========================================================
    # 19. DISPLAY y
    # ========================================================

    print("\n========================================")
    print("Y PREVIEW")
    print("========================================")

    print(
        y.head()
    )


    # ========================================================
    # 20. FINAL VALIDATION
    # ========================================================

    print("\n========================================")
    print("FINAL VALIDATION")
    print("========================================")


    # customer_id must not be in X

    if "customer_id" in X.columns:

        raise ValueError(
            "FAIL — customer_id is present in X."
        )

    print(
        "PASS — customer_id removed"
    )


    # churn must not be in X

    if "churn" in X.columns:

        raise ValueError(
            "FAIL — churn is present in X."
        )

    print(
        "PASS — churn separated from X"
    )


    # X must not have NULLs

    if X.isnull().any().any():

        null_columns = (

            X.columns[
                X.isnull().any()
            ].tolist()
        )

        raise ValueError(
            f"FAIL — X contains NULLs: "
            f"{null_columns}"
        )

    print(
        "PASS — X contains no NULLs"
    )


    # y must not have NULLs

    if y.isnull().any():

        raise ValueError(
            "FAIL — y contains NULL values."
        )

    print(
        "PASS — y contains no NULLs"
    )


    # y must contain only 0 and 1

    if not y.isin([0, 1]).all():

        raise ValueError(
            "FAIL — y contains values "
            "other than 0 and 1."
        )

    print(
        "PASS — y contains only 0 and 1"
    )


    # X and y must have same number of rows

    if len(X) != len(y):

        raise ValueError(
            "FAIL — X and y row counts differ."
        )

    print(
        "PASS — X and y row counts match"
    )


    # ========================================================
    # 21. FINAL SUMMARY
    # ========================================================

    print("\n========================================")
    print("ML1 COMPLETE")
    print("========================================")

    print(
        f"Customers : {len(df)}"
    )

    print(
        f"Features  : {X.shape[1]}"
    )

    print(
        f"Target    : churn"
    )

    print(
        f"X shape   : {X.shape}"
    )

    print(
        f"y shape   : {y.shape}"
    )

    print("\nReady for ML2 training.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()