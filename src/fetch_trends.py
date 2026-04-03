from pathlib import Path

import pandas as pd
from pytrends.request import TrendReq


BASE_DIR = Path(__file__).resolve().parent.parent
MAPPING_PATH = BASE_DIR / "data" / "reference" / "trend_keyword_mapping.csv"
OUTPUT_PATH = BASE_DIR / "data" / "raw" / "google_trends.csv"


def load_keyword_mapping(path: Path) -> pd.DataFrame:
    """Load the manually curated trend keyword mapping table."""
    mapping_df = pd.read_csv(path)
    mapping_df["include_in_fetch"] = mapping_df["include_in_fetch"].astype(str).str.lower().eq("true")
    return mapping_df


def fetch_google_trends(keywords: list[str], timeframe: str, geo: str = "US") -> pd.DataFrame:
    """Fetch Google Trends interest-over-time data for a set of keywords."""
    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
    trends_df = pytrends.interest_over_time()

    if "isPartial" in trends_df.columns:
        trends_df = trends_df.drop(columns=["isPartial"])

    return trends_df.reset_index()


def fetch_single_keyword_series(keyword: str, timeframe: str, geo: str = "US") -> pd.DataFrame:
    """Fetch a single keyword as its own normalized time series."""
    keyword_df = fetch_google_trends([keyword], timeframe=timeframe, geo=geo)
    keyword_df = keyword_df.rename(columns={keyword: "search_interest"})
    keyword_df["trend_keyword"] = keyword
    return keyword_df[["date", "trend_keyword", "search_interest"]]


def main() -> None:
    mapping_df = load_keyword_mapping(MAPPING_PATH)
    keyword_list = mapping_df.loc[mapping_df["include_in_fetch"], "trend_keyword"].dropna().tolist()

    if not keyword_list:
        raise ValueError("No trend keywords are marked for fetching in the mapping table.")

    # Keep the window aligned to the campaign data period to support date-level merges.
    timeframe = "2017-08-17 2017-08-30"
    trends_df = pd.concat(
        [fetch_single_keyword_series(keyword, timeframe=timeframe, geo="US") for keyword in keyword_list],
        ignore_index=True,
    )
    trends_df["date"] = pd.to_datetime(trends_df["date"])
    trends_df = trends_df.sort_values(["trend_keyword", "date"]).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    trends_df.to_csv(OUTPUT_PATH, index=False)

    print("Trend keywords fetched:")
    print(mapping_df.loc[mapping_df["include_in_fetch"], ["theme_id", "trend_keyword"]].to_string(index=False))
    print("\nGoogle Trends sample:")
    print(trends_df.head(12).to_string(index=False))
    print(f"\nSaved Google Trends data to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
