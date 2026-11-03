def quality_report(df, key=None):
    return {
        "rows": int(len(df)),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_keys": int(df.duplicated(subset=[key]).sum()) if key and key in df else 0,
        "missing_cells": int(df.isna().sum().sum()),
        "missing_by_column": {str(k): int(v) for k, v in df.isna().sum().items()},
    }
