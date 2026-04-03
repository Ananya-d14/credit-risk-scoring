"""
Run this script once (locally) after running notebooks 01-03.
It trains the model (or loads a pre-trained one) and saves all
artifacts needed by the FastAPI app to the models/ folder.

Usage:
    python save_artifacts.py
"""
import sys, os, json
sys.path.insert(0, '.')

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from src.data_loader import load_raw_data, get_feature_target
from src.preprocessing import split_data, impute_missing
from src.feature_engineering import create_interaction_features
from src.config import CONFIG

os.makedirs('models', exist_ok=True)

# ── 1. Load & split data ──────────────────────────────────────────────────────
print("Loading data...")
df = load_raw_data()
X, y = get_feature_target(df)

X_train, X_test, y_train, y_test = split_data(X, y)
print(f"  Train: {X_train.shape}  Test: {X_test.shape}")

# ── 2. Impute missing values ──────────────────────────────────────────────────
print("Imputing missing values...")
X_train_imp, X_test_imp, imputer = impute_missing(X_train, X_test)

# ── 3. Add interaction features ───────────────────────────────────────────────
print("Creating interaction features...")
X_train_full = create_interaction_features(X_train_imp)
X_test_full  = create_interaction_features(X_test_imp)
print(f"  Final feature count: {X_train_full.shape[1]}")

# ── 4. Load or train model ────────────────────────────────────────────────────
pretrained_path = 'data/processed/model_xgboost.joblib'

if os.path.exists(pretrained_path):
    print(f"Loading pre-trained XGBoost from {pretrained_path} ...")
    model = joblib.load(pretrained_path)
else:
    print("No pre-trained model found. Training XGBoost from scratch ...")
    print("  (this takes ~1-2 minutes)")
    from xgboost import XGBClassifier
    from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold

    param_grid = {
        "n_estimators":      [200, 300, 500],
        "max_depth":         [3, 4, 5],
        "learning_rate":     [0.05, 0.1],
        "scale_pos_weight":  [3, 5],
        "subsample":         [0.8, 0.9],
        "colsample_bytree":  [0.8, 0.9],
        "reg_alpha":         [0, 0.1],
        "reg_lambda":        [1, 5],
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True,
                         random_state=CONFIG["random_state"])
    search = RandomizedSearchCV(
        XGBClassifier(random_state=CONFIG["random_state"],
                      eval_metric="logloss", n_jobs=-1),
        param_distributions=param_grid,
        n_iter=20,
        cv=cv,
        scoring="roc_auc",
        random_state=CONFIG["random_state"],
        n_jobs=-1,
        verbose=1,
    )
    search.fit(X_train_full, y_train)
    model = search.best_estimator_
    print(f"  Best CV ROC-AUC: {search.best_score_:.4f}")
    print(f"  Best params: {search.best_params_}")

# ── 5. Evaluate ───────────────────────────────────────────────────────────────
preds = model.predict_proba(X_test_full)[:, 1]
auc   = roc_auc_score(y_test, preds)
print(f"\nTest ROC-AUC: {auc:.4f}")

# ── 6. Save artifacts ─────────────────────────────────────────────────────────
print("\nSaving artifacts to models/ ...")
joblib.dump(imputer, 'models/imputer.joblib')
joblib.dump(model,   'models/model.joblib')

json.dump(list(X_train.columns),     open('models/raw_feature_names.json', 'w'))
json.dump(list(X_train_full.columns), open('models/feature_names.json', 'w'))

print("Done. Files saved:")
for f in os.listdir('models'):
    size_kb = os.path.getsize(f'models/{f}') / 1024
    print(f"  models/{f}  ({size_kb:.0f} KB)")
