from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = BASE_DIR / "data" / "processed" / "campaign_data_cleaned.csv"
SUMMARY_OUTPUT_PATH = BASE_DIR / "data" / "processed" / "audience_cluster_summary.csv"
BEST_OUTPUT_PATH = BASE_DIR / "data" / "processed" / "audience_cluster_best.csv"
WORST_OUTPUT_PATH = BASE_DIR / "data" / "processed" / "audience_cluster_worst.csv"

MIN_CLUSTER_ROWS = 3
MIN_CLUSTER_SPEND = 10.0
TOP_N = 10


def safe_rate_divide(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    """Divide arrays for rate metrics while returning 0 when the denominator is 0 or missing."""
    return np.divide(
        numerator,
        denominator,
        out=np.zeros(len(numerator), dtype=float),
        where=(denominator != 0) & ~np.isnan(denominator),
    )


def safe_cost_divide(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    """Divide arrays for cost metrics while returning NaN when the denominator is 0 or missing."""
    return np.divide(
        numerator,
        denominator,
        out=np.full(len(numerator), np.nan, dtype=float),
        where=(denominator != 0) & ~np.isnan(denominator),
    )


def load_cleaned_data(path: Path) -> pd.DataFrame:
    """Load the cleaned campaign dataset."""
    return pd.read_csv(path)


def build_cluster_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate campaign performance to the audience-cluster level."""
    summary = (
        df.groupby(["audience_cluster_key", "audience_cluster_label"], dropna=False)
        .agg(
            ads=("ad_id", "count"),
            unique_campaigns=("campaign_id", "nunique"),
            date_first=("date", "min"),
            date_last=("date", "max"),
            age_modes=("age", lambda values: ", ".join(sorted(pd.Series(values).dropna().astype(str).unique()))),
            gender_modes=("gender", lambda values: ", ".join(sorted(pd.Series(values).dropna().astype(str).unique()))),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spent=("spent", "sum"),
            total_conversion=("total_conversion", "sum"),
            approved_conversion=("approved_conversion", "sum"),
            revenue=("revenue", "sum"),
            click_anomalies=("click_anomaly", "sum"),
            conversion_anomalies=("conversion_anomaly", "sum"),
        )
        .reset_index()
    )

    summary["ctr"] = safe_rate_divide(
        summary["clicks"].to_numpy(dtype=float),
        summary["impressions"].to_numpy(dtype=float),
    )
    summary["conversion_rate"] = safe_rate_divide(
        summary["approved_conversion"].to_numpy(dtype=float),
        summary["clicks"].to_numpy(dtype=float),
    )
    summary["cpc"] = safe_cost_divide(
        summary["spent"].to_numpy(dtype=float),
        summary["clicks"].to_numpy(dtype=float),
    )
    summary["cpa"] = safe_cost_divide(
        summary["spent"].to_numpy(dtype=float),
        summary["approved_conversion"].to_numpy(dtype=float),
    )
    summary["roas"] = safe_cost_divide(
        summary["revenue"].to_numpy(dtype=float),
        summary["spent"].to_numpy(dtype=float),
    )
    summary["eligible_for_ranking"] = (
        (summary["ads"] >= MIN_CLUSTER_ROWS) & (summary["spent"] >= MIN_CLUSTER_SPEND)
    )

    return summary.sort_values(["eligible_for_ranking", "roas", "spent"], ascending=[False, False, False])


def rank_clusters(summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return the best and worst eligible clusters based on ROAS."""
    eligible = summary.loc[summary["eligible_for_ranking"]].copy()

    best_clusters = eligible.sort_values(
        ["roas", "approved_conversion", "spent"],
        ascending=[False, False, False],
    ).head(TOP_N)

    worst_clusters = eligible.sort_values(
        ["roas", "spent", "approved_conversion"],
        ascending=[True, False, True],
    ).head(TOP_N)

    return best_clusters, worst_clusters


def print_summary(summary: pd.DataFrame, best_clusters: pd.DataFrame, worst_clusters: pd.DataFrame) -> None:
    """Print a concise validation summary for the cluster analysis output."""
    print(f"Cluster summary shape: {summary.shape}")
    print(f"Eligible clusters for ranking: {int(summary['eligible_for_ranking'].sum())}")
    print(
        f"Ranking rule: at least {MIN_CLUSTER_ROWS} ads and total spend >= {MIN_CLUSTER_SPEND:.2f}"
    )

    display_columns = [
        "audience_cluster_key",
        "audience_cluster_label",
        "ads",
        "spent",
        "approved_conversion",
        "revenue",
        "roas",
        "ctr",
        "conversion_rate",
        "cpc",
        "cpa",
    ]

    print("\nTop clusters by ROAS:")
    print(best_clusters[display_columns].to_string(index=False))
    print("\nBottom clusters by ROAS:")
    print(worst_clusters[display_columns].to_string(index=False))


def main() -> None:
    cleaned_df = load_cleaned_data(INPUT_PATH)
    summary = build_cluster_summary(cleaned_df)
    best_clusters, worst_clusters = rank_clusters(summary)

    SUMMARY_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY_OUTPUT_PATH, index=False)
    best_clusters.to_csv(BEST_OUTPUT_PATH, index=False)
    worst_clusters.to_csv(WORST_OUTPUT_PATH, index=False)

    print_summary(summary, best_clusters, worst_clusters)
    print(f"\nSaved summary to: {SUMMARY_OUTPUT_PATH}")
    print(f"Saved best clusters to: {BEST_OUTPUT_PATH}")
    print(f"Saved worst clusters to: {WORST_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
