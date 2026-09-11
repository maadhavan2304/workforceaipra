"""
Attrition Prediction Model Training Pipeline.

Trains a scikit-learn classifier on employee HR data to predict attrition
probability. Designed to work with data pulled from the `employees` table,
or an uploaded CSV following the same schema (e.g. IBM HR Analytics style).

Run standalone:
    python -m app.ml.train --csv path/to/data.csv
"""
import argparse
import json
import os
from datetime import datetime

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

MODEL_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
os.makedirs(MODEL_DIR, exist_ok=True)

NUMERIC_FEATURES = [
    "age", "monthly_income", "years_at_company", "years_in_current_role",
    "job_satisfaction", "work_life_balance", "performance_rating",
    "distance_from_home", "num_companies_worked", "total_working_years",
]
CATEGORICAL_FEATURES = ["gender", "overtime", "department"]
TARGET = "attrition"  # expects 0/1 or Yes/No, normalized below


def build_pipeline(algorithm: str = "random_forest") -> Pipeline:
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown="ignore")

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )

    if algorithm == "gradient_boosting":
        clf = GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=42)
    elif algorithm == "logistic_regression":
        clf = LogisticRegression(max_iter=1000, class_weight="balanced")
    else:
        clf = RandomForestClassifier(
            n_estimators=300, max_depth=8, class_weight="balanced", random_state=42
        )

    return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", clf)])


def normalize_target(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return series.astype(int)
    mapped = series.astype(str).str.strip().str.lower().map(
        {"yes": 1, "no": 0, "true": 1, "false": 0, "1": 1, "0": 0}
    )
    return mapped.astype("Int64")


def train(csv_path: str, algorithm: str = "random_forest", version: str = None):
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    missing = [c for c in NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET] if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    df[TARGET] = normalize_target(df[TARGET])
    df = df.dropna(subset=[TARGET])

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = build_pipeline(algorithm)
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 4),
    }

    version = version or datetime.utcnow().strftime("v%Y%m%d%H%M%S")
    model_path = os.path.join(MODEL_DIR, f"attrition_model_{version}.joblib")
    joblib.dump(pipeline, model_path)

    meta = {
        "version": version,
        "algorithm": algorithm,
        "trained_on_rows": len(df),
        "metrics": metrics,
        "file_path": model_path,
        "trained_at": datetime.utcnow().isoformat(),
    }
    with open(os.path.join(MODEL_DIR, f"attrition_model_{version}.meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    # Track latest active version
    with open(os.path.join(MODEL_DIR, "active_model.json"), "w") as f:
        json.dump({"version": version, "file_path": model_path}, f)

    return meta


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to training CSV")
    parser.add_argument("--algorithm", default="random_forest",
                         choices=["random_forest", "gradient_boosting", "logistic_regression"])
    args = parser.parse_args()

    result = train(args.csv, args.algorithm)
    print(json.dumps(result, indent=2))
