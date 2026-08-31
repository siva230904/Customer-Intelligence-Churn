import csv
import shutil
from pathlib import Path
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine, text


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LANDING_DIR = BASE_DIR / "data" / "landing"
RAW_DIR = BASE_DIR / "data" / "raw"
REJECTED_DIR = BASE_DIR / "data" / "rejected"
LOG_DIR = BASE_DIR / "data" / "logs"


# ============================================================
# CREATE DIRECTORIES IF THEY DON'T EXIST
# ============================================================

LANDING_DIR.mkdir(
    parents=True,
    exist_ok=True
)

RAW_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REJECTED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = (
    "mysql+pymysql://root:root@localhost/custchurn"
)


# ============================================================
# EXPECTED CSV COLUMNS
# ============================================================

EXPECTED_COLS = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn"
]


# ============================================================
# CREATE DATABASE ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ============================================================
# 1. DETECT FILES
# ============================================================

def detect_files():

    files = list(
        LANDING_DIR.glob("*.csv")
    )

    return files


# ============================================================
# 2. VALIDATE SCHEMA
# ============================================================

def validate_schema(filepath):

    try:

        with open(
            filepath,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as f:

            header = next(
                csv.reader(f)
            )


        # ----------------------------------------------------
        # Exact column/order comparison
        # ----------------------------------------------------

        is_valid = (
            header == EXPECTED_COLS
        )


        return is_valid, header


    except Exception as e:

        return False, str(e)


# ============================================================
# 3. LOAD TO STAGING
# ============================================================

def load_to_staging(
    filepath,
    engine
):

    df = pd.read_csv(filepath)


    # --------------------------------------------------------
    # Full reload of staging
    # --------------------------------------------------------

    df.to_sql(
        "stg_customer_raw",
        engine,
        if_exists="replace",
        index=False
    )


    return len(df)


# ============================================================
# 4. LOG INGESTION
# ============================================================

def log_ingestion(
    filename,
    status,
    rows,
    reason
):

    query = text("""
        INSERT INTO ingestion_log
        (
            filename,
            table_name,
            status,
            load_time,
            row_count,
            reason
        )
        VALUES
        (
            :filename,
            :table_name,
            :status,
            :load_time,
            :row_count,
            :reason
        )
    """)

    with engine.begin() as connection:

        connection.execute(
            query,
            {
                "filename": filename,
                "table_name": "stg_customer_raw",
                "status": status,
                "load_time": datetime.now(),
                "row_count": rows,
                "reason": reason
            }
        )


# ============================================================
# 5. PROCESS LANDING
# ============================================================

def process_landing():

    files = detect_files()


    # --------------------------------------------------------
    # No files
    # --------------------------------------------------------

    if not files:

        print(
            "No CSV files found in landing directory."
        )

        return


    # --------------------------------------------------------
    # Process each file
    # --------------------------------------------------------

    for filepath in files:

        filename = filepath.name

        print(
            f"\nProcessing: {filename}"
        )


        # ====================================================
        # VALIDATE
        # ====================================================

        is_valid, header = validate_schema(
            filepath
        )


        # ====================================================
        # REJECT INVALID FILE
        # ====================================================

        if not is_valid:

            reason = (
                "Column mismatch. "
                f"Expected: {EXPECTED_COLS}. "
                f"Received: {header}"
            )


            print(
                "REJECTED:",
                reason
            )


            # ------------------------------------------------
            # Move invalid file to rejected
            # ------------------------------------------------

            rejected_path = (
                REJECTED_DIR / filename
            )

            shutil.move(
                str(filepath),
                str(rejected_path)
            )


            # ------------------------------------------------
            # Log rejection
            # ------------------------------------------------

            log_ingestion(
                filename=filename,
                status="REJECTED",
                rows=0,
                reason=reason
            )


            continue


        # ====================================================
        # LOAD VALID FILE
        # ====================================================

        try:

            rows = load_to_staging(
                filepath,
                engine
            )


            # ------------------------------------------------
            # Copy validated file to raw
            # ------------------------------------------------

            raw_path = (
                RAW_DIR / filename
            )

            shutil.copy2(
                str(filepath),
                str(raw_path)
            )


            # ------------------------------------------------
            # Log successful load
            # ------------------------------------------------

            log_ingestion(
                filename=filename,
                status="LOADED",
                rows=rows,
                reason="Schema validation passed"
            )


            print(
                f"LOADED: {filename} "
                f"({rows} rows)"
            )


        except Exception as e:

            # ------------------------------------------------
            # Log load failure
            # ------------------------------------------------

            log_ingestion(
                filename=filename,
                status="REJECTED",
                rows=0,
                reason=f"Load failed: {str(e)}"
            )


            print(
                f"LOAD FAILED: {filename}"
            )

            print(e)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    process_landing()