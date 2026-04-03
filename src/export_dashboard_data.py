import json
from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CAMPAIGN_PATH = BASE_DIR / "data" / "processed" / "campaign_data_cleaned.csv"
DAILY_TRENDS_PATH = BASE_DIR / "data" / "processed" / "campaign_trends_daily_merged.csv"
SEGMENTED_TRENDS_PATH = BASE_DIR / "data" / "processed" / "campaign_trends_segmented_merged.csv"
BEST_CLUSTERS_PATH = BASE_DIR / "data" / "processed" / "audience_cluster_best.csv"
WORST_CLUSTERS_PATH = BASE_DIR / "data" / "processed" / "audience_cluster_worst.csv"
OUTPUT_PATH = BASE_DIR / "dashboard" / "public" / "data" / "dashboard_data.json"


def load_dataframes() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    campaign_df = pd.read_csv(CAMPAIGN_PATH, parse_dates=["date"])
    daily_df = pd.read_csv(DAILY_TRENDS_PATH, parse_dates=["date"])
    segmented_df = pd.read_csv(SEGMENTED_TRENDS_PATH, parse_dates=["date"])
    best_clusters_df = pd.read_csv(BEST_CLUSTERS_PATH)
    worst_clusters_df = pd.read_csv(WORST_CLUSTERS_PATH)
    return campaign_df, daily_df, segmented_df, best_clusters_df, worst_clusters_df


def build_overview(campaign_df: pd.DataFrame) -> dict:
    return {
        "date_start": campaign_df["date"].min().strftime("%Y-%m-%d"),
        "date_end": campaign_df["date"].max().strftime("%Y-%m-%d"),
        "rows": int(len(campaign_df)),
        "campaigns": int(campaign_df["campaign_id"].nunique(dropna=True)),
        "audience_clusters": int(campaign_df["audience_cluster_key"].nunique()),
        "total_spend": round(float(campaign_df["spent"].sum()), 2),
        "total_revenue": round(float(campaign_df["revenue"].sum()), 2),
        "avg_ctr": round(float(campaign_df["ctr"].mean()), 6),
        "avg_conversion_rate": round(float(campaign_df["conversion_rate"].mean()), 4),
        "avg_roas": round(float(campaign_df["roas"].mean()), 4),
    }


def build_daily_theme_series(daily_df: pd.DataFrame) -> dict:
    theme_series = {}
    for theme, group in daily_df.groupby("trend_keyword"):
        theme_series[theme] = [
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "search_interest": int(row["search_interest"]),
                "ctr": round(float(row["ctr"]), 6),
                "conversion_rate": round(float(row["conversion_rate"]), 4),
                "roas": round(float(row["roas"]), 4),
            }
            for _, row in group.sort_values("date").iterrows()
        ]
    return theme_series


def build_demand_bucket_summary(daily_df: pd.DataFrame) -> dict:
    ranked_df = daily_df.copy()
    ranked_df["demand_bucket"] = pd.qcut(
        ranked_df.groupby("trend_keyword")["search_interest"].rank(method="first"),
        q=3,
        labels=["low_demand", "mid_demand", "high_demand"],
    )

    bucket_df = (
        ranked_df.groupby(["trend_keyword", "demand_bucket"], as_index=False, observed=False)
        .agg(
            avg_search_interest=("search_interest", "mean"),
            avg_ctr=("ctr", "mean"),
            avg_conversion_rate=("conversion_rate", "mean"),
            avg_roas=("roas", "mean"),
        )
        .sort_values(["trend_keyword", "avg_search_interest"])
    )

    result: dict[str, list[dict]] = {}
    for theme, group in bucket_df.groupby("trend_keyword"):
        result[theme] = [
            {
                "demand_bucket": row["demand_bucket"],
                "avg_search_interest": round(float(row["avg_search_interest"]), 2),
                "avg_ctr": round(float(row["avg_ctr"]), 6),
                "avg_conversion_rate": round(float(row["avg_conversion_rate"]), 4),
                "avg_roas": round(float(row["avg_roas"]), 4),
            }
            for _, row in group.iterrows()
        ]
    return result


def build_age_gender_summary(campaign_df: pd.DataFrame) -> list[dict]:
    summary_df = (
        campaign_df.groupby(["age", "gender"], as_index=False)
        .agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spent=("spent", "sum"),
            approved_conversion=("approved_conversion", "sum"),
            revenue=("revenue", "sum"),
            ctr=("ctr", "mean"),
            conversion_rate=("conversion_rate", "mean"),
            roas=("roas", "mean"),
        )
        .sort_values(["age", "gender"])
    )
    return summary_df.round(
        {
            "spent": 2,
            "revenue": 2,
            "ctr": 6,
            "conversion_rate": 4,
            "roas": 4,
        }
    ).to_dict(orient="records")


def build_segment_sensitivity(segmented_df: pd.DataFrame) -> dict:
    corr_df = (
        segmented_df.groupby(["trend_keyword", "age", "gender"])[
            ["search_interest", "ctr", "conversion_rate", "roas"]
        ]
        .corr()
        .reset_index()
    )
    corr_df = corr_df.loc[
        corr_df["level_3"] == "search_interest",
        ["trend_keyword", "age", "gender", "ctr", "conversion_rate", "roas"],
    ].rename(
        columns={
            "ctr": "corr_with_ctr",
            "conversion_rate": "corr_with_conversion_rate",
            "roas": "corr_with_roas",
        }
    )

    context_df = segmented_df.groupby(["trend_keyword", "age", "gender"], as_index=False).agg(
        total_spent=("spent", "sum"),
        total_clicks=("clicks", "sum"),
        total_conversions=("approved_conversion", "sum"),
        n_days=("date", "nunique"),
    )

    sensitivity_df = corr_df.merge(context_df, on=["trend_keyword", "age", "gender"], how="left")
    sensitivity_df = sensitivity_df.loc[
        (sensitivity_df["total_spent"] >= 4000) & (sensitivity_df["n_days"] >= 12)
    ].copy()

    result = {}
    for theme, group in sensitivity_df.groupby("trend_keyword"):
        top_positive = group.sort_values("corr_with_roas", ascending=False).head(5)
        top_negative = group.sort_values("corr_with_roas", ascending=True).head(5)
        result[theme] = {
            "top_positive": top_positive.round(
                {
                    "corr_with_ctr": 3,
                    "corr_with_conversion_rate": 3,
                    "corr_with_roas": 3,
                    "total_spent": 2,
                }
            ).to_dict(orient="records"),
            "top_negative": top_negative.round(
                {
                    "corr_with_ctr": 3,
                    "corr_with_conversion_rate": 3,
                    "corr_with_roas": 3,
                    "total_spent": 2,
                }
            ).to_dict(orient="records"),
        }
    return result


def build_cluster_cards(best_clusters_df: pd.DataFrame, worst_clusters_df: pd.DataFrame) -> dict:
    card_columns = [
        "audience_cluster_label",
        "audience_cluster_key",
        "ads",
        "spent",
        "approved_conversion",
        "roas",
        "cpa",
        "age_modes",
        "gender_modes",
    ]

    def clean_records(df: pd.DataFrame) -> list[dict]:
        records = df[card_columns].head(5).replace({np.nan: None}).round({"spent": 2, "roas": 3, "cpa": 2})
        return records.to_dict(orient="records")

    return {
        "best": clean_records(best_clusters_df),
        "worst": clean_records(worst_clusters_df),
    }


def main() -> None:
    campaign_df, daily_df, segmented_df, best_clusters_df, worst_clusters_df = load_dataframes()

    payload = {
        "overview": build_overview(campaign_df),
        "themes": sorted(daily_df["trend_keyword"].unique().tolist()),
        "dailyThemeSeries": build_daily_theme_series(daily_df),
        "demandBucketSummary": build_demand_bucket_summary(daily_df),
        "ageGenderSummary": build_age_gender_summary(campaign_df),
        "segmentSensitivity": build_segment_sensitivity(segmented_df),
        "clusterCards": build_cluster_cards(best_clusters_df, worst_clusters_df),
        "methodology": {
            "scope_note": "Google Trends is used as an overall market-demand context signal, not as a user-level measure of what a Facebook audience segment searched for.",
            "limitation_note": "Trend alignment findings are exploratory because the observation window covers only 14 days and themes are manually selected market-context topics.",
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=True, indent=2))
    print(f"Saved dashboard data to: {OUTPUT_PATH.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
