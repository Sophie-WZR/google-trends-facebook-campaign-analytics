import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "processed" / "campaign_trends.db"

TABLE_SPECS = {
    "campaign_data_cleaned": BASE_DIR / "data" / "processed" / "campaign_data_cleaned.csv",
    "audience_cluster_summary": BASE_DIR / "data" / "processed" / "audience_cluster_summary.csv",
    "campaign_trends_daily": BASE_DIR / "data" / "processed" / "campaign_trends_daily_merged.csv",
    "campaign_trends_segmented": BASE_DIR / "data" / "processed" / "campaign_trends_segmented_merged.csv",
}


def load_csv_tables(connection: sqlite3.Connection) -> None:
    """Load processed CSV outputs into SQLite tables."""
    for table_name, csv_path in TABLE_SPECS.items():
        if not csv_path.exists():
            raise FileNotFoundError(f"Required input file not found: {csv_path}")

        dataframe = pd.read_csv(csv_path)
        dataframe.to_sql(table_name, connection, if_exists="replace", index=False)
        print(f"Loaded {table_name}: {dataframe.shape[0]:,} rows x {dataframe.shape[1]} columns")


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        load_csv_tables(connection)

    print(f"\nSaved SQLite database to: {DB_PATH.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
