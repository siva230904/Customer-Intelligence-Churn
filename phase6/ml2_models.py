import os
import joblib
import pandas as pd

from sqlalchemy import create_engine

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:root@localhost/custchurn"
)

MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print()
    print("=" * 50)
    print("ML2 — LOAD DATA")
    print("=" * 50)

    engine = create_engine(DATABASE_URL)

    df = pd.read_sql(
        "SELECT * FROM customer_ml_features",
        engine
    )

    print(f"Rows loaded: {len(df)}")
    print(f"Columns loaded: {len(df.columns)}")

    return df


# ============================================================
# PREPARE FEATURES
# ============================================================

def prepare_features(df):

    print()
    print("=" * 50)
    print("PREPARE FEATURES")
    print("=" * 50)

    required_columns = [
        "tenure",
        "monthly_charges",
        "service_count",
        "contract",
        "churn"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # --------------------------------------------------------
    # Select only features that ML4 can provide
    # --------------------------------------------------------

    X = df[
        [
            "tenure",
            "monthly_charges",
            "service_count",
            "contract"
        ]
    ].copy()

    y = df["churn"].astype(int)

    # --------------------------------------------------------
    # Rename contract -> contract_type
    # --------------------------------------------------------

    X = X.rename(
        columns={
            "contract": "contract_type"
        }
    )

    # --------------------------------------------------------
    # One-hot encode contract_type
    # --------------------------------------------------------

    X = pd.get_dummies(
        X,
        columns=["contract_type"],
        drop_first=False,
        dtype=int
    )

    # --------------------------------------------------------
    # Make sure all three contract columns exist
    # --------------------------------------------------------

    expected_contract_columns = [
        "contract_type_Month-to-month",
        "contract_type_One year",
        "contract_type_Two year"
    ]

    for column in expected_contract_columns:

        if column not in X.columns:
            X[column] = 0

    # --------------------------------------------------------
    # Explicit feature order
    # --------------------------------------------------------

    feature_columns = [
        "tenure",
        "monthly_charges",
        "service_count",
        "contract_type_Month-to-month",
        "contract_type_One year",
        "contract_type_Two year"
    ]

    X = X[feature_columns]

    print()
    print("Final training features:")

    for column in X.columns:
        print(f"- {column}")

    print()
    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")

    print()
    print("Class balance:")
    print(
        y.value_counts(normalize=True)
    )

    return X, y


# ============================================================
# TRAIN AND EVALUATE MODEL
# ============================================================

def train_models(X, y):

    print()
    print("=" * 50)
    print("TRAIN / TEST SPLIT")
    print("=" * 50)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows: {len(X_test)}")

    # ========================================================
    # LOGISTIC REGRESSION
    # ========================================================

    print()
    print("=" * 50)
    print("LOGISTIC REGRESSION")
    print("=" * 50)

    logistic = LogisticRegression(
        max_iter=1000,
        random_state=42
    )

    logistic.fit(
        X_train,
        y_train
    )

    logistic_pred = logistic.predict(X_test)

    print()
    print(
        classification_report(
            y_test,
            logistic_pred,
            target_names=[
                "Active",
                "Churned"
            ]
        )
    )

    print("Confusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            logistic_pred
        )
    )

    logistic_cv = cross_val_score(
        logistic,
        X,
        y,
        cv=5,
        scoring="f1"
    )

    print()
    print(
        "5-Fold CV F1:",
        logistic_cv
    )

    print(
        "Mean CV F1:",
        logistic_cv.mean()
    )

    # ========================================================
    # DECISION TREE
    # ========================================================

    print()
    print("=" * 50)
    print("DECISION TREE")
    print("=" * 50)

    tree = DecisionTreeClassifier(
        max_depth=5,
        random_state=42
    )

    tree.fit(
        X_train,
        y_train
    )

    tree_pred = tree.predict(X_test)

    print()
    print(
        classification_report(
            y_test,
            tree_pred,
            target_names=[
                "Active",
                "Churned"
            ]
        )
    )

    print("Confusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            tree_pred
        )
    )

    tree_cv = cross_val_score(
        tree,
        X,
        y,
        cv=5,
        scoring="f1"
    )

    print()
    print(
        "5-Fold CV F1:",
        tree_cv
    )

    print(
        "Mean CV F1:",
        tree_cv.mean()
    )

    # ========================================================
    # COMPARISON TABLE
    # ========================================================

    comparison = pd.DataFrame(
        [
            {
                "Model": "Logistic Regression",
                "Accuracy": accuracy_score(
                    y_test,
                    logistic_pred
                ),
                "Precision (Churned)": precision_score(
                    y_test,
                    logistic_pred,
                    zero_division=0
                ),
                "Recall (Churned)": recall_score(
                    y_test,
                    logistic_pred,
                    zero_division=0
                ),
                "F1 (Churned)": f1_score(
                    y_test,
                    logistic_pred,
                    zero_division=0
                ),
                "CV F1": logistic_cv.mean()
            },
            {
                "Model": "Decision Tree",
                "Accuracy": accuracy_score(
                    y_test,
                    tree_pred
                ),
                "Precision (Churned)": precision_score(
                    y_test,
                    tree_pred,
                    zero_division=0
                ),
                "Recall (Churned)": recall_score(
                    y_test,
                    tree_pred,
                    zero_division=0
                ),
                "F1 (Churned)": f1_score(
                    y_test,
                    tree_pred,
                    zero_division=0
                ),
                "CV F1": tree_cv.mean()
            }
        ]
    )

    print()
    print("=" * 50)
    print("MODEL COMPARISON")
    print("=" * 50)

    print(
        comparison.to_string(
            index=False
        )
    )

    # ========================================================
    # SELECT BEST MODEL
    # ========================================================

    best_row = comparison.loc[
        comparison["F1 (Churned)"].idxmax()
    ]

    best_model_name = best_row["Model"]

    if best_model_name == "Decision Tree":

        best_model = tree

    else:

        best_model = logistic

    print()
    print("=" * 50)
    print("MODEL SELECTION")
    print("=" * 50)

    print(
        f"Best model: {best_model_name}"
    )

    print(
        f"Best F1: "
        f"{best_row['F1 (Churned)']:.4f}"
    )

    return (
        logistic,
        tree,
        best_model,
        best_model_name,
        X_train,
        X_test,
        y_train,
        y_test
    )


# ============================================================
# SAVE MODELS
# ============================================================

def save_models(logistic, tree):

    print()
    print("=" * 50)
    print("SAVE MODELS")
    print("=" * 50)

    logistic_path = os.path.join(
        MODEL_DIR,
        "logistic_churn.pkl"
    )

    tree_path = os.path.join(
        MODEL_DIR,
        "tree_churn.pkl"
    )

    joblib.dump(
        logistic,
        logistic_path
    )

    joblib.dump(
        tree,
        tree_path
    )

    print(
        f"Saved: {logistic_path}"
    )

    print(
        f"Saved: {tree_path}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 50)
    print("ML2 — BUILD AND COMPARE BASELINE MODELS")
    print("=" * 50)

    df = load_data()

    X, y = prepare_features(df)

    (
        logistic,
        tree,
        best_model,
        best_model_name,
        X_train,
        X_test,
        y_train,
        y_test
    ) = train_models(
        X,
        y
    )

    save_models(
        logistic,
        tree
    )

    print()
    print("=" * 50)
    print("ML2 COMPLETE")
    print("=" * 50)

    print(
        f"Selected model: {best_model_name}"
    )


if __name__ == "__main__":
    main()