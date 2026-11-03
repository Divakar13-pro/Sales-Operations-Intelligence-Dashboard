from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parents[1] / "database" / "dashboard.db"


def write_frames(frames):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        for name, frame in frames.items():
            frame.to_sql(name, conn, if_exists="replace", index=False)
    return str(DB_PATH)
