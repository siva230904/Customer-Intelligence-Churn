import pandas as pd
import numpy as np
import re
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class CustomerCleaner:

    def __init__(self, df):
        self.df = df.copy()

        logging.info("CustomerCleaner initialized.")
        logging.info(f"Input DataFrame Shape: {self.df.shape}")

    def standardize_column_names(self):
        logging.info("Standardizing column names...")

        new_columns = []

        for col in self.df.columns:
            col = re.sub(r'(?<!^)([A-Z])', r'_\1', col)
            col = col.replace(" ", "_")
            col = col.lower()
            new_columns.append(col)

        self.df.columns = new_columns

        logging.info("Column names converted to snake_case.")

    def fix_total_charges(self):
        logging.info("Cleaning total_charges column...")

        try:
            blanks = (self.df["total_charges"] == "").sum()

            logging.info(f"Blank strings found: {blanks}")

            self.df["total_charges"] = self.df["total_charges"].replace("", np.nan)

            self.df["total_charges"] = pd.to_numeric(
                self.df["total_charges"],
                errors="coerce"
            )

            nulls = self.df["total_charges"].isna().sum()

            logging.info(
                f"Conversion completed. Total null values in total_charges: {nulls}"
            )

        except Exception:
            logging.exception("Unexpected error while cleaning total_charges.")
            raise

    def normalize_binary_columns(self):
        logging.info("Normalizing binary columns...")

        binary_cols = [
            "partner",
            "dependents",
            "phone_service",
            "paperless_billing",
            "churn"
        ]

        for col in binary_cols:
            logging.info(f"Processing column: {col}")

            self.df[col] = self.df[col].map({
                "Yes": 1,
                "No": 0
            })

        logging.info("Binary columns normalized.")

    def handle_nulls(self):
        logging.info("Handling null values...")

        before = self.df["total_charges"].isna().sum()

        logging.info(f"Nulls before filling: {before}")

        self.df["total_charges"] = self.df["total_charges"].fillna(
            self.df["monthly_charges"]
        )

        after = self.df["total_charges"].isna().sum()

        logging.info(f"Nulls after filling: {after}")

    def clean(self):
        logging.info("Starting data cleaning pipeline...")

        self.standardize_column_names()
        self.fix_total_charges()
        self.normalize_binary_columns()
        self.handle_nulls()

        logging.info("Data cleaning pipeline completed successfully.")

        return self.df