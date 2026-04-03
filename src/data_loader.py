import pandas as pd
from src.config import CONFIG, PROJECT_ROOT


def load_raw_data():
    """Load the credit scoring dataset, drop ID column."""
    data_path = PROJECT_ROOT / CONFIG["data_path"]
    df = pd.read_excel(data_path)

    assert CONFIG["target_column"] in df.columns, f"Target '{CONFIG['target_column']}' not found"
    assert CONFIG["id_column"] in df.columns, f"ID col '{CONFIG['id_column']}' not found"

    df = df.drop(columns=[CONFIG["id_column"]])
    return df


def get_feature_target(df):
    target = CONFIG["target_column"]
    y = df[target]
    X = df.drop(columns=[target])
    return X, y
