"""Train Random Forest and XGBoost regressors for SOH.

Both are tree ensembles, so we don't need to scale features. The
hyperparameters here are reasonable defaults — not heavily tuned. Tuning
is in the future-work list.
"""
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestRegressor

# XGBoost is optional — if not installed, the rest of the pipeline still runs.
try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


def train_random_forest(X_train, y_train):
    """Random Forest regressor with conservative defaults.

    n_estimators=200: enough trees for stable predictions, still fast.
    max_depth=12: keeps the trees from memorising on a small dataset.
    min_samples_leaf=3: smooths predictions, reduces variance.
    """
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def train_xgboost(X_train, y_train):
    """Gradient-boosted trees.

    Compared to RF, XGBoost typically gets a small improvement on tabular
    regression in exchange for more sensitivity to hyperparameters.
    """
    if not XGBOOST_AVAILABLE:
        raise ImportError(
            "xgboost is not installed. Either run `pip install xgboost`, "
            "or skip XGBoost — the rest of the pipeline still works without it."
        )
    model = XGBRegressor(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def save_model(model, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_model(path):
    return joblib.load(path)
