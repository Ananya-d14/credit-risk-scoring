import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from src.config import CONFIG


def split_data(X, y):
    """Stratified split — important bc of the 83/17 imbalance."""
    return train_test_split(
        X, y,
        test_size=CONFIG["test_size"],
        random_state=CONFIG["random_state"],
        stratify=y,
    )


def impute_missing(X_train, X_test, strategy="median"):
    # median instead of mean — more robust to the outliers in delinquency features
    # IMPORTANT: fit on train only to avoid data leakage
    imputer = SimpleImputer(strategy=strategy)
    X_train_imp = pd.DataFrame(
        imputer.fit_transform(X_train),
        columns=X_train.columns, index=X_train.index,
    )
    X_test_imp = pd.DataFrame(
        imputer.transform(X_test),
        columns=X_test.columns, index=X_test.index,
    )
    return X_train_imp, X_test_imp, imputer


def scale_features(X_train, X_test):
    scaler = StandardScaler()
    X_train_sc = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X_train.columns, index=X_train.index,
    )
    X_test_sc = pd.DataFrame(
        scaler.transform(X_test),
        columns=X_test.columns, index=X_test.index,
    )
    return X_train_sc, X_test_sc, scaler


def preprocess_pipeline(X, y):
    """Split -> impute -> scale. All fitting on train only."""
    X_train, X_test, y_train, y_test = split_data(X, y)
    X_train, X_test, imputer = impute_missing(X_train, X_test)
    X_train_sc, X_test_sc, scaler = scale_features(X_train, X_test)

    return {
        "X_train": X_train,
        "X_test": X_test,
        "X_train_scaled": X_train_sc,
        "X_test_scaled": X_test_sc,
        "y_train": y_train,
        "y_test": y_test,
        "imputer": imputer,
        "scaler": scaler,
    }
