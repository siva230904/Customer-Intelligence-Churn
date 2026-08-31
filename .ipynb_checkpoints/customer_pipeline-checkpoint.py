import os
import logging
from datetime import datetime

import pandas as pd

from customer_cleaner import CustomerCleaner


# ----------------------------------------------------
# Logging Configuration
# ----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ----------------------------------------------------
# Load Data
# ----------------------------------------------------
def load_data(filepath):
    """
    Reads the CSV file and logs the row count.
    """
    try:
        logging.info("Loading data...")

        df = pd.read_csv(filepath)

        logging.info(f"Successfully loaded {len(df)} rows.")

        return df

    except Exception as e:
        logging.error(f"Error loading data: {e}")
        raise


# ----------------------------------------------------
# Feature Engineering
# ----------------------------------------------------
def build_features(df):
    """
    Builds all engineered features.
    """

    try:
        logging.info("Building features...")

        # -----------------------------
        # Feature 1 - tenure_bucket
        # -----------------------------
        df["tenure_bucket"] = pd.cut(
            df["tenure"],
            bins=[0, 12, 24, 48, 72],
            labels=["0-12", "13-24", "25-48", "49-72"],
            include_lowest=True
        )

        # -----------------------------
        # Feature 2 - high_charge_flag
        # -----------------------------
        median_charge = df["monthly_charges"].median()

        df["high_charge_flag"] = (
            df["monthly_charges"] > median_charge
        ).astype(int)

        # -----------------------------
        # Convert service columns
        # -----------------------------
        service_cols = [
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_t_v",
            "streaming_movies"
        ]

        mapping = {
            "Yes": 1,
            "No": 0,
            "No internet service": 0,
            1: 1,
            0: 0
        }

        for col in service_cols:
            df[col] = df[col].map(mapping)

        # -----------------------------
        # Feature 3 - service_count
        # -----------------------------
        df["service_count"] = df[service_cols].sum(axis=1)

        # -----------------------------
        # Feature 4
        # -----------------------------
        df["is_long_term_customer"] = (
            df["tenure"] >= 24
        ).astype(int)

        # -----------------------------
        # Feature 5
        # -----------------------------
        df["has_streaming_bundle"] = (
            (df["streaming_t_v"] == 1) &
            (df["streaming_movies"] == 1)
        ).astype(int)

        # -----------------------------
        # Feature 6
        # -----------------------------
        df["auto_pay_flag"] = (
            df["payment_method"]
            .str.contains("automatic", na=False)
            .astype(int)
        )

        logging.info("Feature engineering completed.")

        return df

    except Exception as e:
        logging.error(f"Feature engineering failed: {e}")
        raise


# ----------------------------------------------------
# Save Outputs
# ----------------------------------------------------
def save_outputs(clean_df, feature_df, output_dir):
    """
    Saves cleaned and feature engineered datasets.
    """

    try:

        logging.info("Performing data quality checks...")

        # -----------------------------
        # Data Quality Checks
        # -----------------------------
        assert clean_df["monthly_charges"].isna().sum() == 0, \
            "monthly_charges contains null values."

        assert set(clean_df["churn"].unique()).issubset({0, 1}), \
            "Churn column contains invalid values."

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        clean_path = os.path.join(
            output_dir,
            f"customer_cleaned_{timestamp}.csv"
        )

        feature_path = os.path.join(
            output_dir,
            f"customer_features_{timestamp}.csv"
        )

        clean_df.to_csv(clean_path, index=False)
        feature_df.to_csv(feature_path, index=False)

        logging.info(f"Cleaned data saved to: {clean_path}")
        logging.info(f"Feature data saved to: {feature_path}")

    except Exception as e:
        logging.error(f"Saving outputs failed: {e}")
        raise


# ----------------------------------------------------
# Main Pipeline
# ----------------------------------------------------
def main():

    logging.info("=" * 50)
    logging.info("Customer Pipeline Started")
    logging.info("=" * 50)

    try:

        # Change filename if needed
        filepath = "customer.csv"

        output_dir = "outputs"

        # -----------------------------
        # Load
        # -----------------------------
        raw_df = load_data("customer_churn.csv")

        # -----------------------------
        # Clean
        # -----------------------------
        cleaner = CustomerCleaner(raw_df)

        # Replace clean_data() with your cleaning method
        clean_df = cleaner.clean()

        logging.info(
            f"Cleaning completed. Rows after cleaning: {len(clean_df)}"
        )

        # -----------------------------
        # Feature Engineering
        # -----------------------------
        feature_df = build_features(clean_df.copy())

        logging.info(
            f"Feature engineering completed. Rows: {len(feature_df)}"
        )

        # -----------------------------
        # Save
        # -----------------------------
        save_outputs(
            clean_df,
            feature_df,
            output_dir
        )

        logging.info("=" * 50)
        logging.info("Pipeline completed successfully.")
        logging.info("=" * 50)

    except Exception as e:

        logging.exception("Pipeline failed.")

        raise


# ----------------------------------------------------
# Run
# ----------------------------------------------------
if __name__ == "__main__":
    main()