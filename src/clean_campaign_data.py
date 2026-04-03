from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = BASE_DIR / "data" / "raw" / "facebook_ads.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "campaign_data_cleaned.csv"

DATE_COLUMNS = ["reporting_start", "reporting_end"]
NUMERIC_COLUMNS = [
    "ad_id",
    "campaign_id",
    "fb_campaign_id",
    "interest1",
    "interest2",
    "interest3",
    "impressions",
    "clicks",
    "spent",
    "total_conversion",
    "approved_conversion",
]
INTEGER_COLUMNS = [
    "ad_id",
    "campaign_id",
    "fb_campaign_id",
    "interest1",
    "interest2",
    "interest3",
    "impressions",
    "clicks",
    "total_conversion",
    "approved_conversion",
]
NON_NEGATIVE_COLUMNS = [
    "interest1",
    "interest2",
    "interest3",
    "impressions",
    "clicks",
    "spent",
    "total_conversion",
    "approved_conversion",
]


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Divide two series while returning 0 when the denominator is 0 or missing."""
    numerator_array = numerator.to_numpy(dtype=float, copy=False)
    denominator_array = denominator.to_numpy(dtype=float, copy=False)

    result = np.divide(
        numerator_array,
        denominator_array,
        out=np.zeros(len(numerator), dtype=float),
        where=(denominator_array != 0) & ~np.isnan(denominator_array),
    )
    return pd.Series(result, index=numerator.index)


def create_audience_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create audience-code features without assuming the codes are ordinal."""
    audience_cluster_key = (
        df["interest1"].astype("string")
        + "_"
        + df["interest2"].astype("string")
        + "_"
        + df["interest3"].astype("string")
    )

    cluster_frequency = audience_cluster_key.map(audience_cluster_key.value_counts()).astype("Int64")
    unique_clusters = audience_cluster_key.drop_duplicates().sort_values().reset_index(drop=True)
    cluster_label_map = {
        cluster: f"cluster_{index:03d}"
        for index, cluster in enumerate(unique_clusters, start=1)
    }
    audience_cluster_label = audience_cluster_key.map(cluster_label_map)

    return pd.DataFrame(
        {
            "audience_cluster_key": audience_cluster_key,
            "audience_cluster_label": audience_cluster_label,
            "audience_cluster_frequency": cluster_frequency,
            # Reserved for a future manually curated mapping to Google Trends topics.
            "trend_keyword": pd.Series(pd.NA, index=df.index, dtype="string"),
        },
        index=df.index,
    )


def load_raw_data(path: Path) -> pd.DataFrame:
    """Load the raw campaign dataset."""
    return pd.read_csv(path, dtype=str)


def repair_shifted_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Fix rows where missing IDs shift the remaining values into the wrong columns."""
    repaired = df.copy()
    shifted_mask = (
        repaired["campaign_id"].astype(str).str.fullmatch(r"\d{2}-\d{2}")
        & repaired["fb_campaign_id"].astype(str).isin(["M", "F"])
    )

    if shifted_mask.any():
        shifted_rows = repaired.loc[shifted_mask].copy()

        repaired.loc[shifted_mask, "approved_conversion"] = shifted_rows["spent"]
        repaired.loc[shifted_mask, "total_conversion"] = shifted_rows["clicks"]
        repaired.loc[shifted_mask, "spent"] = shifted_rows["impressions"]
        repaired.loc[shifted_mask, "clicks"] = shifted_rows["interest3"]
        repaired.loc[shifted_mask, "impressions"] = shifted_rows["interest2"]
        repaired.loc[shifted_mask, "interest3"] = shifted_rows["interest1"]
        repaired.loc[shifted_mask, "interest2"] = shifted_rows["age"]
        repaired.loc[shifted_mask, "interest1"] = shifted_rows["gender"]
        repaired.loc[shifted_mask, "gender"] = shifted_rows["fb_campaign_id"]
        repaired.loc[shifted_mask, "age"] = shifted_rows["campaign_id"]
        repaired.loc[shifted_mask, ["campaign_id", "fb_campaign_id"]] = np.nan

    return repaired


def clean_campaign_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply cleaning, validation, and feature engineering to campaign data."""
    cleaned = df.copy()
    cleaned.columns = cleaned.columns.str.lower().str.strip()
    cleaned = repair_shifted_rows(cleaned)

    for column in DATE_COLUMNS:
        cleaned[column] = pd.to_datetime(cleaned[column], dayfirst=True, errors="coerce")

    cleaned["date"] = cleaned["reporting_start"]

    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned["total_conversion"] = cleaned["total_conversion"].fillna(0)
    cleaned["approved_conversion"] = cleaned["approved_conversion"].fillna(0)

    for column in INTEGER_COLUMNS:
        cleaned[column] = cleaned[column].round().astype("Int64")

    cleaned = cleaned.drop_duplicates().copy()

    valid_rows = pd.Series(True, index=cleaned.index)
    for column in NON_NEGATIVE_COLUMNS:
        valid_rows &= cleaned[column].isna() | (cleaned[column] >= 0)
    cleaned = cleaned.loc[valid_rows].copy()

    cleaned["click_anomaly"] = cleaned["clicks"] > cleaned["impressions"]
    cleaned["conversion_anomaly"] = cleaned["approved_conversion"] > cleaned["clicks"]

    audience_features = create_audience_features(cleaned)
    cleaned["audience_cluster_key"] = audience_features["audience_cluster_key"]
    cleaned["audience_cluster_label"] = audience_features["audience_cluster_label"]
    cleaned["audience_cluster_frequency"] = audience_features["audience_cluster_frequency"]
    cleaned["trend_keyword"] = audience_features["trend_keyword"]

    cleaned["ctr"] = safe_divide(cleaned["clicks"], cleaned["impressions"])
    cleaned["conversion_rate"] = safe_divide(cleaned["approved_conversion"], cleaned["clicks"])
    cleaned["cpc"] = safe_divide(cleaned["spent"], cleaned["clicks"])
    cleaned["cpa"] = safe_divide(cleaned["spent"], cleaned["approved_conversion"])

    revenue_per_approved_conversion = 20.0
    cleaned["revenue"] = cleaned["approved_conversion"] * revenue_per_approved_conversion
    cleaned["roas"] = safe_divide(cleaned["revenue"], cleaned["spent"])

    return cleaned


def print_validation_summary(raw_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> None:
    """Print a lightweight validation report for the cleaned dataset."""
    print(f"Raw shape: {raw_df.shape}")
    print(f"Cleaned shape: {cleaned_df.shape}")
    print("\nMissing values summary:")
    print(cleaned_df.isna().sum())
    print("\nAnomaly counts:")
    print(f"click_anomaly: {int(cleaned_df['click_anomaly'].sum())}")
    print(f"conversion_anomaly: {int(cleaned_df['conversion_anomaly'].sum())}")
    print("\nSample rows:")
    print(cleaned_df.head(10).to_string(index=False))


def main() -> None:
    raw_df = load_raw_data(INPUT_PATH)
    cleaned_df = clean_campaign_data(raw_df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(OUTPUT_PATH, index=False)

    print_validation_summary(raw_df, cleaned_df)
    print(f"\nCleaned dataset saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
