"""
Loads the active trained model and produces attrition risk predictions
for employees, with basic feature-importance-based explanation.
"""
import json
import os
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd

from app.ml.train import NUMERIC_FEATURES, CATEGORICAL_FEATURES, MODEL_DIR

_ACTIVE_MODEL = None
_ACTIVE_VERSION = None


def _load_active_model():
    global _ACTIVE_MODEL, _ACTIVE_VERSION
    active_path = os.path.join(MODEL_DIR, "active_model.json")
    if not os.path.exists(active_path):
        raise FileNotFoundError(
            "No trained attrition model found. Train one first via app/ml/train.py"
        )
    with open(active_path) as f:
        info = json.load(f)
    _ACTIVE_MODEL = joblib.load(info["file_path"])
    _ACTIVE_VERSION = info["version"]
    return _ACTIVE_MODEL, _ACTIVE_VERSION


def get_model():
    if _ACTIVE_MODEL is None:
        return _load_active_model()
    return _ACTIVE_MODEL, _ACTIVE_VERSION


def risk_level_from_score(score: float) -> str:
    if score >= 0.75:
        return "Critical"
    if score >= 0.5:
        return "High"
    if score >= 0.25:
        return "Medium"
    return "Low"


def predict_employee(employee_features: Dict) -> Dict:
    """
    employee_features: dict with keys matching NUMERIC_FEATURES + CATEGORICAL_FEATURES
    (department instead of department_id - pass department name)
    """
    model, version = get_model()

    row = {k: employee_features.get(k) for k in NUMERIC_FEATURES + CATEGORICAL_FEATURES}
    df = pd.DataFrame([row])

    proba = model.predict_proba(df)[0]
    # class 1 = attrition risk
    classes = list(model.named_steps["classifier"].classes_)
    risk_idx = classes.index(1) if 1 in classes else -1
    score = float(proba[risk_idx])

    top_factors = _explain(model, df)

    return {
        "risk_score": round(score, 4),
        "risk_level": risk_level_from_score(score),
        "top_factors": top_factors,
        "model_version": version,
    }


def predict_batch(employees_df: pd.DataFrame) -> List[Dict]:
    model, version = get_model()
    df = employees_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    proba = model.predict_proba(df)
    classes = list(model.named_steps["classifier"].classes_)
    risk_idx = classes.index(1) if 1 in classes else -1

    results = []
    for i, score in enumerate(proba[:, risk_idx]):
        results.append({
            "risk_score": round(float(score), 4),
            "risk_level": risk_level_from_score(float(score)),
            "model_version": version,
        })
    return results


def _explain(model, df: pd.DataFrame, top_n: int = 3) -> List[str]:
    """Lightweight explanation using tree-based feature_importances_ when available."""
    try:
        clf = model.named_steps["classifier"]
        preprocessor = model.named_steps["preprocessor"]
        feature_names = preprocessor.get_feature_names_out()
        importances = getattr(clf, "feature_importances_", None)
        if importances is None:
            return []
        order = np.argsort(importances)[::-1][:top_n]
        return [feature_names[i].split("__")[-1] for i in order]
    except Exception:
        return []
