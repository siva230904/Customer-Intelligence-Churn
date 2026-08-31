import os
import joblib
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "tree_churn.pkl"
)


# ============================================================
# LOAD MODEL ONCE
# ============================================================

print("Loading churn model...")

model = joblib.load(
    MODEL_PATH
)

print(
    "Decision Tree model loaded successfully."
)


# ============================================================
# MODEL FEATURES
# ============================================================

EXPECTED_FEATURES = [
    "tenure",
    "monthly_charges",
    "service_count",
    "contract_type_Month-to-month",
    "contract_type_One year",
    "contract_type_Two year"
]


# ============================================================
# PREPROCESS INPUT
# ============================================================

def preprocess_input(
    tenure,
    monthly_charges,
    contract_type,
    service_count
):

    # --------------------------------------------------------
    # Create one-row DataFrame
    # --------------------------------------------------------

    df = pd.DataFrame(
        [
            {
                "tenure": tenure,
                "monthly_charges": monthly_charges,
                "service_count": service_count,
                "contract_type": contract_type
            }
        ]
    )

    # --------------------------------------------------------
    # One-hot encode contract type
    # --------------------------------------------------------

    df = pd.get_dummies(
        df,
        columns=["contract_type"],
        drop_first=False,
        dtype=int
    )

    # --------------------------------------------------------
    # Add missing contract columns
    # --------------------------------------------------------

    for column in [
        "contract_type_Month-to-month",
        "contract_type_One year",
        "contract_type_Two year"
    ]:

        if column not in df.columns:

            df[column] = 0

    # --------------------------------------------------------
    # Exact feature order
    # --------------------------------------------------------

    df = df[
        EXPECTED_FEATURES
    ]

    return df


# ============================================================
# PREDICT CHURN
# ============================================================

def predict_churn(
    tenure,
    monthly_charges,
    contract_type,
    service_count
):

    # --------------------------------------------------------
    # Prepare input
    # --------------------------------------------------------

    X = preprocess_input(
        tenure,
        monthly_charges,
        contract_type,
        service_count
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = model.predict(
        X
    )[0]

    # --------------------------------------------------------
    # Probability
    # --------------------------------------------------------

    probabilities = model.predict_proba(
        X
    )[0]

    risk_score = float(
        probabilities[1]
    )

    # --------------------------------------------------------
    # Prediction label
    # --------------------------------------------------------

    if prediction == 1:

        prediction_label = (
            "Likely to churn"
        )

    else:

        prediction_label = (
            "Unlikely to churn"
        )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = float(
        max(probabilities)
    )

    return {
        "risk_score": round(
            risk_score,
            4
        ),
        "prediction": prediction_label,
        "confidence": round(
            confidence,
            4
        )
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 50)
    print("ML4 — MODEL PREDICTION TEST")
    print("=" * 50)

    # --------------------------------------------------------
    # TEST 1
    # --------------------------------------------------------

    print()
    print(
        "Test 1 — Month-to-month / short tenure"
    )

    result1 = predict_churn(
        tenure=3,
        monthly_charges=90.0,
        contract_type="Month-to-month",
        service_count=2
    )

    print(result1)

    # --------------------------------------------------------
    # TEST 2
    # --------------------------------------------------------

    print()
    print(
        "Test 2 — Two year / long tenure"
    )

    result2 = predict_churn(
        tenure=60,
        monthly_charges=50.0,
        contract_type="Two year",
        service_count=4
    )

    print(result2)

    # --------------------------------------------------------
    # TEST 3
    # --------------------------------------------------------

    print()
    print(
        "Test 3 — One year / medium tenure"
    )

    result3 = predict_churn(
        tenure=24,
        monthly_charges=70.0,
        contract_type="One year",
        service_count=3
    )

    print(result3)

    print()
    print("=" * 50)
    print("ML4 LOCAL TEST COMPLETE")
    print("=" * 50)