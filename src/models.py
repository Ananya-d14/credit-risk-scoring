import numpy as np
from joblib import parallel_config
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV
from src.config import CONFIG


def get_cv():
    return StratifiedKFold(
        n_splits=CONFIG["cv_folds"], shuffle=True,
        random_state=CONFIG["random_state"],
    )


def get_model_configs():
    rs = CONFIG["random_state"]

    configs = {
        "Logistic Regression": {
            "model": LogisticRegression(max_iter=1000, random_state=rs, solver="saga"),
            "params": {
                "C": [0.001, 0.01, 0.1, 0.5, 1, 5, 10],
                "penalty": ["l1", "l2"],
                "class_weight": ["balanced", None],
            },
        },
        "Random Forest": {
            "model": RandomForestClassifier(random_state=rs),
            "params": {
                "n_estimators": [100, 200, 300],
                "max_depth": [3, 5, 7, 10, None],
                "min_samples_leaf": [5, 10, 20, 50],
                "min_samples_split": [10, 20, 50],
                "class_weight": ["balanced", "balanced_subsample"],
            },
        },
        "XGBoost": {
            "model": XGBClassifier(
                random_state=rs, eval_metric="logloss",
                use_label_encoder=False,
            ),
            "params": {
                "n_estimators": [100, 200, 300],
                "max_depth": [3, 5, 7],
                "learning_rate": [0.01, 0.05, 0.1],
                "scale_pos_weight": [1, 3, 5],
                "reg_alpha": [0, 0.1, 1],
                "reg_lambda": [1, 5, 10],
                "subsample": [0.7, 0.8, 1.0],
                "colsample_bytree": [0.7, 0.8, 1.0],
            },
        },
        "LightGBM": {
            "model": LGBMClassifier(random_state=rs, verbose=-1),
            "params": {
                "n_estimators": [100, 200, 300],
                "max_depth": [3, 5, 7, -1],
                "learning_rate": [0.01, 0.05, 0.1],
                "is_unbalance": [True],
                "num_leaves": [15, 31, 63],
                "reg_alpha": [0, 0.1, 1],
                "reg_lambda": [0, 1, 5],
                "subsample": [0.7, 0.8, 1.0],
                "colsample_bytree": [0.7, 0.8, 1.0],
            },
        },
    }
    return configs


def train_models(X_train, y_train, model_configs=None, n_iter=None):
    if model_configs is None:
        model_configs = get_model_configs()
    if n_iter is None:
        n_iter = CONFIG["n_iter_search"]

    cv = get_cv()
    results = {}

    for name, cfg in model_configs.items():
        print(f"\nTraining {name}...")
        actual_iter = min(n_iter, _param_space_size(cfg["params"]))
        search = RandomizedSearchCV(
            estimator=cfg["model"],
            param_distributions=cfg["params"],
            n_iter=actual_iter,
            cv=cv, scoring="roc_auc",
            random_state=CONFIG["random_state"],
            n_jobs=-1, verbose=0,
            return_train_score=True,
        )
        with parallel_config(backend="threading"):
            search.fit(X_train, y_train)
        results[name] = search
        print(f"  Best ROC-AUC: {search.best_score_:.4f}")
        print(f"  Best params: {search.best_params_}")

    return results


def _param_space_size(params):
    size = 1
    for v in params.values():
        size *= len(v)
    return size
