import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
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


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    engine = create_engine(
        DATABASE_URL
    )

    df = pd.read_sql(
        "SELECT * FROM customer_ml_features",
        engine
    )

    return df


# ============================================================
# PREPARE FEATURES
# ============================================================

def prepare_features(df):

    X = df[
        [
            "tenure",
            "monthly_charges",
            "service_count",
            "contract"
        ]
    ].copy()

    y = df["churn"].astype(int)

    X = X.rename(
        columns={
            "contract": "contract_type"
        }
    )

    X = pd.get_dummies(
        X,
        columns=["contract_type"],
        drop_first=False,
        dtype=int
    )

    expected_contract_columns = [
        "contract_type_Month-to-month",
        "contract_type_One year",
        "contract_type_Two year"
    ]

    for column in expected_contract_columns:

        if column not in X.columns:
            X[column] = 0

    feature_columns = [
        "tenure",
        "monthly_charges",
        "service_count",
        "contract_type_Month-to-month",
        "contract_type_One year",
        "contract_type_Two year"
    ]

    X = X[feature_columns]

    return X, y


# ============================================================
# LOAD MODELS
# ============================================================

def load_models():

    logistic = joblib.load(
        os.path.join(
            MODEL_DIR,
            "logistic_churn.pkl"
        )
    )

    tree = joblib.load(
        os.path.join(
            MODEL_DIR,
            "tree_churn.pkl"
        )
    )

    return logistic, tree


# ============================================================
# SELECT BEST MODEL
# ============================================================

def select_best_model(
    logistic,
    tree,
    X_train,
    X_test,
    y_train,
    y_test
):

    logistic_pred = logistic.predict(
        X_test
    )

    tree_pred = tree.predict(
        X_test
    )

    logistic_f1 = f1_score(
        y_test,
        logistic_pred,
        zero_division=0
    )

    tree_f1 = f1_score(
        y_test,
        tree_pred,
        zero_division=0
    )

    print()
    print("=" * 50)
    print("MODEL SELECTION")
    print("=" * 50)

    print(
        f"Logistic Regression F1: "
        f"{logistic_f1:.4f}"
    )

    print(
        f"Decision Tree F1: "
        f"{tree_f1:.4f}"
    )

    if tree_f1 >= logistic_f1:

        best_model = tree
        best_name = "Decision Tree"

    else:

        best_model = logistic
        best_name = "Logistic Regression"

    print()
    print(
        f"Best model: {best_name}"
    )

    return best_model, best_name


# ============================================================
# LOGISTIC INTERPRETATION
# ============================================================

def interpret_logistic(model, feature_names):

    coefficients = pd.Series(
        model.coef_[0],
        index=feature_names
    )

    coefficients = coefficients.sort_values(
        key=abs,
        ascending=False
    )

    print()
    print("=" * 50)
    print("LOGISTIC REGRESSION INTERPRETATION")
    print("=" * 50)

    print()
    print("Feature coefficients:")

    print(
        coefficients
    )

    print()
    print("Top 3 features:")

    print(
        coefficients.head(3)
    )

    top10 = coefficients.head(10)

    plt.figure(
        figsize=(10, 6)
    )

    top10.sort_values().plot(
        kind="barh"
    )

    plt.title(
        "Top 10 Logistic Regression Coefficients"
    )

    plt.xlabel(
        "Coefficient"
    )

    plt.tight_layout()

    plt.savefig(
        "logistic_top10_coefficients.png"
    )

    plt.close()

    print()
    print(
        "Chart saved to: "
        "logistic_top10_coefficients.png"
    )

    return coefficients


# ============================================================
# TREE INTERPRETATION
# ============================================================

def interpret_tree(model, feature_names):

    importances = pd.Series(
        model.feature_importances_,
        index=feature_names
    )

    importances = importances.sort_values(
        ascending=False
    )

    print()
    print("=" * 50)
    print("DECISION TREE INTERPRETATION")
    print("=" * 50)

    print()
    print("Feature importances:")

    print(
        importances
    )

    print()
    print("Top 3 features:")

    print(
        importances.head(3)
    )

    top10 = importances.head(10)

    plt.figure(
        figsize=(10, 6)
    )

    top10.sort_values().plot(
        kind="barh"
    )

    plt.title(
        "Top 10 Decision Tree Feature Importances"
    )

    plt.xlabel(
        "Importance"
    )

    plt.tight_layout()

    plt.savefig(
        "tree_top10_importances.png"
    )

    plt.close()

    print()
    print(
        "Chart saved to: "
        "tree_top10_importances.png"
    )

    return importances


# ============================================================
# TOP 20 RISK CUSTOMERS
# ============================================================

def find_top_risk_customers(
    model,
    X_test,
    y_test,
    original_df
):

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    results = original_df.loc[
        X_test.index,
        ["customer_id"]
    ].copy()

    results["actual_churn"] = y_test

    results["risk_score"] = probabilities

    results = results.sort_values(
        "risk_score",
        ascending=False
    )

    top20 = results.head(20)

    print()
    print("=" * 50)
    print("TOP 20 HIGHEST-RISK CUSTOMERS")
    print("=" * 50)

    print(
        top20.to_string(
            index=False
        )
    )

    top20.to_csv(
        "top20_risk_customers.csv",
        index=False
    )

    print()
    print(
        "Saved to: top20_risk_customers.csv"
    )

    return top20


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 50)
    print("ML3 — INTERPRET MODEL BEHAVIOUR")
    print("=" * 50)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    df = load_data()

    print(
        f"Customer rows: {len(df)}"
    )

    # --------------------------------------------------------
    # Prepare
    # --------------------------------------------------------

    X, y = prepare_features(
        df
    )

    # --------------------------------------------------------
    # Split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    print(
        f"Training rows: {len(X_train)}"
    )

    print(
        f"Testing rows: {len(X_test)}"
    )

    # --------------------------------------------------------
    # Load models
    # --------------------------------------------------------

    logistic, tree = load_models()

    # --------------------------------------------------------
    # Select best
    # --------------------------------------------------------

    best_model, best_name = select_best_model(
        logistic,
        tree,
        X_train,
        X_test,
        y_train,
        y_test
    )

    # --------------------------------------------------------
    # Interpretation
    # --------------------------------------------------------

    if best_name == "Decision Tree":

        importances = interpret_tree(
            best_model,
            X.columns
        )

    else:

        importances = interpret_logistic(
            best_model,
            X.columns
        )

    # --------------------------------------------------------
    # Best model report
    # --------------------------------------------------------

    predictions = best_model.predict(
        X_test
    )

    print()
    print("=" * 50)
    print("BEST MODEL REPORT")
    print("=" * 50)

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "Active",
                "Churned"
            ]
        )
    )

    # --------------------------------------------------------
    # Top risk customers
    # --------------------------------------------------------

    find_top_risk_customers(
        best_model,
        X_test,
        y_test,
        df
    )

    # --------------------------------------------------------
    # Business interpretation
    # --------------------------------------------------------

    print()
    print("=" * 50)
    print("BUSINESS INTERPRETATION")
    print("=" * 50)

    top3 = list(
        importances.head(3).index
    )

    print()

    print(
        f"1. The model's strongest signals are "
        f"{', '.join(top3)}."
    )

    print(
        "2. Customers with combinations of these "
        "characteristics receive higher churn risk scores."
    )

    print(
        "3. Shorter tenure and month-to-month contracts "
        "can indicate customers who are easier to lose."
    )

    print(
        "4. The retention team can use these predictions "
        "to prioritize customers for intervention."
    )

    print(
        "5. Predictions should support business judgment "
        "rather than replace it."
    )

    print()
    print("=" * 50)
    print("ML3 COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()