from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CAMPAIGN_PATH = BASE_DIR / "data" / "processed" / "campaign_data_cleaned.csv"
TRENDS_PATH = BASE_DIR / "data" / "raw" / "google_trends.csv"
MAPPING_PATH = BASE_DIR / "data" / "reference" / "trend_keyword_mapping.csv"
DAILY_OUTPUT_PATH = BASE_DIR / "data" / "processed" / "campaign_trends_daily_merged.csv"
SEGMENTED_OUTPUT_PATH = BASE_DIR / "data" / "processed" / "campaign_trends_segmented_merged.csv"


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


def reshape_trends(trends_df: pd.DataFrame) -> pd.DataFrame:
    """Convert Google Trends output into a date-keyword long table."""
    trends_df = trends_df.copy()
    trends_df["date"] = pd.to_datetime(trends_df["date"])

    if {"trend_keyword", "search_interest"}.issubset(trends_df.columns):
        return trends_df[["date", "trend_keyword", "search_interest"]].copy()

    return trends_df.melt(
        id_vars="date",
        var_name="trend_keyword",
        value_name="search_interest",
    )


def aggregate_campaign_metrics(df: pd.DataFrame, group_columns: list[str]) -> pd.DataFrame:
    """Aggregate campaign metrics to a requested grain and compute KPI columns."""
    aggregated = (
        df.groupby(group_columns, dropna=False)
        .agg(
            ads=("ad_id", "count"),
            unique_campaigns=("campaign_id", "nunique"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spent=("spent", "sum"),
            total_conversion=("total_conversion", "sum"),
            approved_conversion=("approved_conversion", "sum"),
            revenue=("revenue", "sum"),
        )
        .reset_index()
    )

    aggregated["ctr"] = safe_rate_divide(
        aggregated["clicks"].to_numpy(dtype=float),
        aggregated["impressions"].to_numpy(dtype=float),
    )
    aggregated["conversion_rate"] = safe_rate_divide(
        aggregated["approved_conversion"].to_numpy(dtype=float),
        aggregated["clicks"].to_numpy(dtype=float),
    )
    aggregated["cpc"] = safe_cost_divide(
        aggregated["spent"].to_numpy(dtype=float),
        aggregated["clicks"].to_numpy(dtype=float),
    )
    aggregated["cpa"] = safe_cost_divide(
        aggregated["spent"].to_numpy(dtype=float),
        aggregated["approved_conversion"].to_numpy(dtype=float),
    )
    aggregated["roas"] = safe_cost_divide(
        aggregated["revenue"].to_numpy(dtype=float),
        aggregated["spent"].to_numpy(dtype=float),
    )

    return aggregated


def merge_with_trends(campaign_df: pd.DataFrame, trends_long_df: pd.DataFrame) -> pd.DataFrame:
    """Cross audience performance at a given date grain with each external trend theme."""
    return campaign_df.merge(trends_long_df, on="date", how="left")


def main() -> None:
    campaign_df = pd.read_csv(CAMPAIGN_PATH, parse_dates=["date"])
    trends_df = pd.read_csv(TRENDS_PATH, parse_dates=["date"])
    mapping_df = pd.read_csv(MAPPING_PATH)

    valid_keywords = mapping_df.loc[
        mapping_df["include_in_fetch"].astype(str).str.lower().eq("true"),
        "trend_keyword",
    ].tolist()

    trends_long_df = reshape_trends(trends_df)
    trends_long_df = trends_long_df.loc[trends_long_df["trend_keyword"].isin(valid_keywords)].copy()

    daily_campaign_df = aggregate_campaign_metrics(campaign_df, ["date"])
    daily_campaign_df["segment_level"] = "overall"

    segmented_campaign_df = aggregate_campaign_metrics(campaign_df, ["date", "age", "gender"])
    segmented_campaign_df["segment_level"] = "age_gender"

    daily_merged_df = merge_with_trends(daily_campaign_df, trends_long_df)
    segmented_merged_df = merge_with_trends(segmented_campaign_df, trends_long_df)

    DAILY_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    daily_merged_df.to_csv(DAILY_OUTPUT_PATH, index=False)
    segmented_merged_df.to_csv(SEGMENTED_OUTPUT_PATH, index=False)

    print(f"Daily merged shape: {daily_merged_df.shape}")
    print(f"Segmented merged shape: {segmented_merged_df.shape}")
    print("\nDaily merged sample:")
    print(daily_merged_df.head(10).to_string(index=False))
    print(f"\nSaved daily merged data to: {DAILY_OUTPUT_PATH}")
    print(f"Saved segmented merged data to: {SEGMENTED_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
