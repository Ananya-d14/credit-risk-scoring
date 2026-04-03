import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def load_config():
    config_path = PROJECT_ROOT / "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

# load once at import time so notebooks can just do `from src.config import CONFIG`
CONFIG = load_config()
