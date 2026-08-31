import os
import sys
from pathlib import Path


# ============================================================
# WINDOWS / PYSPARK CONFIGURATION
# ============================================================

python_path = sys.executable

os.environ["PYSPARK_PYTHON"] = python_path
os.environ["PYSPARK_DRIVER_PYTHON"] = python_path

# Your existing Hadoop location
HADOOP_HOME = r"C:\hadoop"

os.environ["HADOOP_HOME"] = HADOOP_HOME
os.environ["hadoop.home.dir"] = HADOOP_HOME

os.environ["PATH"] = (
    r"C:\hadoop\bin;"
    + os.environ["PATH"]
)


# ============================================================
# IMPORTS
# ============================================================

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType
)

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = (
    BASE_DIR
    / "data"
    / "landing"
    / "customer_churn.csv"
)

PARQUET_PATH = (
    BASE_DIR
    / "data"
    / "spark_output"
    / "contract_summary"
)


# ============================================================
# CREATE SPARK SESSION
# ============================================================

def create_spark_session():

    print("\n========================================")
    print("CREATE SPARK SESSION")
    print("========================================")

    print(f"Python: {python_path}")
    print(f"HADOOP_HOME: {HADOOP_HOME}")

    spark = (
        SparkSession.builder
        .appName("CustomerChurnDE5")
        .master("local[2]")
        .config(
            "spark.driver.memory",
            "4g"
        )
        .getOrCreate()
    )

    print("SparkSession created successfully.")

    return spark


# ============================================================
# MANUAL SCHEMA
# ============================================================

def get_schema():

    return StructType([

        StructField(
            "customerID",
            StringType(),
            True
        ),

        StructField(
            "gender",
            StringType(),
            True
        ),

        StructField(
            "SeniorCitizen",
            IntegerType(),
            True
        ),

        StructField(
            "Partner",
            StringType(),
            True
        ),

        StructField(
            "Dependents",
            StringType(),
            True
        ),

        StructField(
            "tenure",
            IntegerType(),
            True
        ),

        StructField(
            "PhoneService",
            StringType(),
            True
        ),

        StructField(
            "MultipleLines",
            StringType(),
            True
        ),

        StructField(
            "InternetService",
            StringType(),
            True
        ),

        StructField(
            "OnlineSecurity",
            StringType(),
            True
        ),

        StructField(
            "OnlineBackup",
            StringType(),
            True
        ),

        StructField(
            "DeviceProtection",
            StringType(),
            True
        ),

        StructField(
            "TechSupport",
            StringType(),
            True
        ),

        StructField(
            "StreamingTV",
            StringType(),
            True
        ),

        StructField(
            "StreamingMovies",
            StringType(),
            True
        ),

        StructField(
            "Contract",
            StringType(),
            True
        ),

        StructField(
            "PaperlessBilling",
            StringType(),
            True
        ),

        StructField(
            "PaymentMethod",
            StringType(),
            True
        ),

        StructField(
            "MonthlyCharges",
            DoubleType(),
            True
        ),

        # Keep this String initially
        # because the CSV contains blanks.
        StructField(
            "TotalCharges",
            StringType(),
            True
        ),

        StructField(
            "Churn",
            StringType(),
            True
        )
    ])


# ============================================================
# READ CSV
# ============================================================

def read_customer_csv(spark):

    print("\n========================================")
    print("READ CUSTOMER CSV")
    print("========================================")

    schema = get_schema()

    df = (
        spark.read
        .option(
            "header",
            True
        )
        .schema(schema)
        .csv(
            str(CSV_PATH)
        )
    )

    print("\nSpark Schema:")

    df.printSchema()

    row_count = df.count()

    print(
        f"\nRows loaded: {row_count}"
    )

    if row_count == 7043:

        print(
            "PASS — 7043 rows loaded."
        )

    else:

        print(
            f"WARNING — expected 7043 "
            f"but found {row_count}"
        )

    return df


# ============================================================
# CLEAN TOTAL CHARGES
# ============================================================

def clean_total_charges(df):

    print("\n========================================")
    print("CLEAN TOTAL CHARGES")
    print("========================================")

    # Convert blank/whitespace values to NULL
    df = df.withColumn(
        "TotalCharges",
        F.when(
            F.trim(
                F.col("TotalCharges")
            ) == "",
            None
        )
        .otherwise(
            F.col("TotalCharges")
        )
    )

    # Convert String -> Double
    df = df.withColumn(
        "TotalCharges",
        F.col("TotalCharges")
        .cast(DoubleType())
    )

    null_count = (
        df
        .filter(
            F.col("TotalCharges").isNull()
        )
        .count()
    )

    print(
        f"TotalCharges NULL count: "
        f"{null_count}"
    )

    print(
        "TotalCharges converted "
        "to DoubleType."
    )

    return df


# ============================================================
# ENCODE CHURN
# ============================================================

def encode_churn(df):

    print("\n========================================")
    print("ENCODE CHURN")
    print("========================================")

    df = df.withColumn(
        "churn_encoded",
        F.when(
            F.col("Churn") == "Yes",
            1
        )
        .otherwise(0)
    )

    print(
        "Created churn_encoded column."
    )

    return df


# ============================================================
# CONTRACT CHURN SUMMARY
# ============================================================

def contract_churn_summary(df):

    print("\n========================================")
    print("CONTRACT CHURN SUMMARY")
    print("========================================")

    summary = (
        df
        .groupBy(
            "Contract"
        )
        .agg(

            F.count("*")
            .alias(
                "customer_count"
            ),

            F.avg(
                "churn_encoded"
            )
            .alias(
                "churn_rate"
            )
        )
        .orderBy(
            F.col(
                "churn_rate"
            ).desc()
        )
    )

    summary.show(
        truncate=False
    )

    return summary


# ============================================================
# INTERNET SERVICE SUMMARY
# ============================================================

def internet_service_summary(df):

    print("\n========================================")
    print("INTERNET SERVICE SUMMARY")
    print("========================================")

    summary = (
        df
        .groupBy(
            "InternetService"
        )
        .agg(

            F.avg(
                "MonthlyCharges"
            )
            .alias(
                "avg_monthly_charges"
            ),

            F.avg(
                "churn_encoded"
            )
            .alias(
                "churn_rate"
            )
        )
        .orderBy(
            F.col(
                "churn_rate"
            ).desc()
        )
    )

    summary.show(
        truncate=False
    )

    return summary


# ============================================================
# WRITE PARQUET USING PANDAS
# ============================================================

def write_contract_parquet_pandas(
    spark_summary
):

    print("\n========================================")
    print("WRITE PARQUET")
    print("========================================")

    print(
        "Using Pandas + PyArrow for Parquet "
        "because Windows Hadoop file permissions "
        "are being skipped."
    )

    # --------------------------------------------------------
    # Convert the SMALL aggregated Spark DataFrame
    # to Pandas.
    #
    # IMPORTANT:
    # We are NOT converting the original 7043-row
    # customer DataFrame.
    #
    # Only the tiny contract summary is converted.
    # --------------------------------------------------------

    pandas_df = (
        spark_summary
        .toPandas()
    )

    print("\nPandas DataFrame:")

    print(
        pandas_df
    )

    print(
        f"\nRows to write: "
        f"{len(pandas_df)}"
    )

    # Remove old output directory
    # so the result is a clean full reload.

    if PARQUET_PATH.exists():

        import shutil

        shutil.rmtree(
            PARQUET_PATH
        )

    PARQUET_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Write Parquet using PyArrow.
    #
    # partition_cols=["Contract"]
    # creates folders such as:
    #
    # Contract=Month-to-month/
    # Contract=One year/
    # Contract=Two year/
    # --------------------------------------------------------

    pandas_df.to_parquet(
        PARQUET_PATH,
        engine="pyarrow",
        partition_cols=[
            "Contract"
        ],
        index=False
    )

    print(
        "\nPASS — Parquet written "
        "using Pandas + PyArrow."
    )

    print(
        f"Output directory:\n"
        f"{PARQUET_PATH}"
    )


# ============================================================
# READ PARQUET USING PANDAS
# ============================================================

def read_parquet_back_pandas():

    print("\n========================================")
    print("READ PARQUET BACK")
    print("========================================")

    df = pd.read_parquet(
        PARQUET_PATH,
        engine="pyarrow"
    )

    print(
        "\nParquet schema:"
    )

    print(
        df.dtypes
    )

    print(
        "\nParquet data:"
    )

    print(
        df
    )

    print(
        f"\nParquet row count: "
        f"{len(df)}"
    )

    return df


# ============================================================
# VALIDATE ROUND TRIP
# ============================================================

def validate_round_trip(
    spark_summary,
    parquet_df
):

    print("\n========================================")
    print("PARQUET ROUND-TRIP VALIDATION")
    print("========================================")

    spark_count = (
        spark_summary.count()
    )

    parquet_count = (
        len(parquet_df)
    )

    print(
        f"Spark summary rows: "
        f"{spark_count}"
    )

    print(
        f"Parquet rows: "
        f"{parquet_count}"
    )

    if spark_count == parquet_count:

        print(
            "PASS — Row counts match."
        )

    else:

        raise AssertionError(
            "FAIL — Row counts do not match."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n========================================")
    print("DE5 — PYSPARK CUSTOMER PIPELINE")
    print("========================================")

    spark = None

    try:

        # ----------------------------------------------------
        # 1. SparkSession
        # ----------------------------------------------------

        spark = (
            create_spark_session()
        )


        # ----------------------------------------------------
        # 2. Read CSV with manual schema
        # ----------------------------------------------------

        df = (
            read_customer_csv(
                spark
            )
        )


        # ----------------------------------------------------
        # 3. Clean TotalCharges
        # ----------------------------------------------------

        df = (
            clean_total_charges(
                df
            )
        )


        # ----------------------------------------------------
        # 4. Encode Churn
        # ----------------------------------------------------

        df = (
            encode_churn(
                df
            )
        )


        # ----------------------------------------------------
        # 5. Show final schema
        # ----------------------------------------------------

        print("\n========================================")
        print("FINAL SPARK SCHEMA")
        print("========================================")

        df.printSchema()


        # ----------------------------------------------------
        # 6. Contract churn
        # ----------------------------------------------------

        contract_summary = (
            contract_churn_summary(
                df
            )
        )


        # ----------------------------------------------------
        # 7. Internet service analysis
        # ----------------------------------------------------

        internet_summary = (
            internet_service_summary(
                df
            )
        )

        # Keep variable intentionally
        _ = internet_summary


        # ----------------------------------------------------
        # 8. Write Parquet
        #
        # Spark did the processing.
        # Pandas handles only the tiny final summary.
        # ----------------------------------------------------

        write_contract_parquet_pandas(
            contract_summary
        )


        # ----------------------------------------------------
        # 9. Read Parquet back
        # ----------------------------------------------------

        parquet_df = (
            read_parquet_back_pandas()
        )


        # ----------------------------------------------------
        # 10. Validate
        # ----------------------------------------------------

        validate_round_trip(
            contract_summary,
            parquet_df
        )


        # ----------------------------------------------------
        # COMPLETE
        # ----------------------------------------------------

        print("\n========================================")
        print("DE5 COMPLETE")
        print("========================================")

        print(
            "\nPySpark processing: SUCCESS"
        )

        print(
            "Parquet writing: "
            "Pandas + PyArrow"
        )

        print(
            f"Output:\n{PARQUET_PATH}"
        )


    except Exception as e:

        print("\n========================================")
        print("DE5 FAILED")
        print("========================================")

        print(
            f"{type(e).__name__}: {e}"
        )

        raise


    finally:

        if spark is not None:

            spark.stop()

            print(
                "\nSparkSession stopped."
            )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()