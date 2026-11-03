from pathlib import Path
import json
import pandas as pd
from .database import write_frames

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load_all_data():
    required = [DATA / "crm_data.csv", DATA / "operations_data.json", DATA / "sales_targets.csv", DATA / "account_mapping.csv"]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Required sample data file(s) missing: " + ", ".join(missing) + ". Run: python scripts/generate_sample_data.py")

    crm = pd.read_csv(required[0])
    with open(required[1], "r", encoding="utf-8") as f:
        operations = pd.DataFrame(json.load(f))
    targets = pd.read_csv(required[2])
    mapping = pd.read_csv(required[3])
    return {"crm": crm, "operations": operations, "targets": targets, "mapping": mapping}


def refresh_database():
    """Reload the local synthetic source files and save a SQLite snapshot."""
    frames = load_all_data()
    write_frames(frames)
    return frames
