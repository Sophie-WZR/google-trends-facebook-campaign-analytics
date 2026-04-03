# Google Trends + Facebook Ad Campaign Analytics

An end-to-end analytics project that combines Facebook ad campaign performance data with Google Trends demand signals to explore whether external market context aligns with campaign efficiency over time.

The project includes Python data-cleaning and KPI-engineering workflows, audience-cluster analysis, exploratory demand-alignment notebooks, SQLite and SQL analysis layers, and a React dashboard designed as a lightweight solutions-style demo.

## Overview

This project started with a Kaggle Facebook ads dataset and expanded into a small end-to-end analytics pipeline:

1. Clean and validate campaign data
2. Engineer marketing KPIs
3. Summarize audience-cluster performance
4. Explore demographic differences across age and gender
5. Pull Google Trends signals for manually selected market themes
6. Merge internal performance data with external demand context
7. Analyze whether campaign efficiency appears to move with market interest over time

## Project Goals

- Clean and validate a real-world Facebook campaign dataset
- Build audience-cluster summaries from Facebook audience-code combinations
- Engineer campaign KPIs such as CTR, conversion rate, CPC, CPA, and ROAS
- Pull Google Trends time series for manually selected demand themes
- Merge external demand signals with campaign performance at daily and demographic levels
- Explore whether campaign efficiency appears to move with external demand context

## Data Sources

- Facebook ad campaign dataset from Kaggle
- Google Trends data fetched with `pytrends`

## Tech Stack

- Python
- pandas
- NumPy
- Jupyter Notebook
- React
- Vite
- SQLite
- SQL

## Repository Workflow

1. Load and inspect the raw Facebook dataset
2. Clean campaign data and engineer KPIs
3. Build audience-cluster summaries
4. Perform internal EDA on campaign performance
5. Define a small manual Google Trends theme mapping
6. Fetch Google Trends time series
7. Merge external demand context with campaign performance
8. Analyze overall and segmented demand alignment
9. Load outputs into SQLite for query-based analysis

## Key Files

### Python Scripts

- [src/load_campaign_data.py](src/load_campaign_data.py)
  Basic raw-data loading and inspection

- [src/clean_campaign_data.py](src/clean_campaign_data.py)
  Cleaning pipeline for the Facebook dataset

- [src/analyze_audience_clusters.py](src/analyze_audience_clusters.py)
  Audience-cluster aggregation and best/worst cluster ranking

- [src/fetch_trends.py](src/fetch_trends.py)
  Google Trends fetching for manually selected demand themes

- [src/merge_trends.py](src/merge_trends.py)
  Merges Google Trends signals with campaign performance

- [src/load_to_sqlite.py](src/load_to_sqlite.py)
  Loads processed outputs into a SQLite database

### Notebooks

- [notebooks/01_eda.ipynb](notebooks/01_eda.ipynb)
  Internal campaign EDA before external signal integration

- [notebooks/02_analysis.ipynb](notebooks/02_analysis.ipynb)
  Google Trends integration and demand-alignment analysis

### SQL

- [sql/analysis_queries.sql](sql/analysis_queries.sql)
  Example SQL analysis queries for the SQLite database

## Processed Outputs

- [data/processed/campaign_data_cleaned.csv](data/processed/campaign_data_cleaned.csv)
- [data/processed/audience_cluster_summary.csv](data/processed/audience_cluster_summary.csv)
- [data/processed/audience_cluster_best.csv](data/processed/audience_cluster_best.csv)
- [data/processed/audience_cluster_worst.csv](data/processed/audience_cluster_worst.csv)
- [data/raw/google_trends.csv](data/raw/google_trends.csv)
- [data/processed/campaign_trends_daily_merged.csv](data/processed/campaign_trends_daily_merged.csv)
- [data/processed/campaign_trends_segmented_merged.csv](data/processed/campaign_trends_segmented_merged.csv)
- [dashboard/public/data/dashboard_data.json](dashboard/public/data/dashboard_data.json)

## Methodology

## Data Cleaning and Modeling Choices

### Facebook Campaign Data

- Standardized column names to lowercase
- Parsed campaign dates with `dayfirst=True`
- Filled missing `total_conversion` and `approved_conversion` with `0`
- Removed duplicate rows
- Filtered out impossible negative values
- Flagged anomalies such as:
  - `click_anomaly`: `clicks > impressions`
  - `conversion_anomaly`: `approved_conversion > clicks`
- Engineered KPI columns:
  - `ctr`
  - `conversion_rate`
  - `cpc`
  - `cpa`
  - `revenue`
  - `roas`

### Audience Features

The `interest1`, `interest2`, and `interest3` columns were treated as Facebook audience codes rather than interpretable ordinal variables.

Instead of forcing unsupported semantic labels onto those codes, the project creates:

- `audience_cluster_key`
- `audience_cluster_label`
- `audience_cluster_frequency`

This keeps the audience logic faithful to the available data.

### Google Trends Integration

Google Trends is not used as a direct measure of segment-level search behavior.

Instead, it is used as an external market-demand context layer:

- Manually selected themes are defined in [data/reference/trend_keyword_mapping.csv](data/reference/trend_keyword_mapping.csv)
- Each theme is fetched independently to preserve a clean within-theme time series
- Google Trends is merged to Facebook performance by `date`

This means the project evaluates alignment between market-level search interest and campaign performance over time, not user-level search intent.

## Analysis Outputs

The project produces two main analysis layers:

### 1. Internal Facebook Performance Analysis

- audience-cluster concentration and stability
- best and worst audience clusters by ROAS
- KPI distribution checks
- age and gender performance differences
- daily spend, conversion, and ROAS trend checks

### 2. External Demand Alignment Analysis

- theme-level Google Trends time series
- daily campaign performance merged with theme-level demand signals
- segmented `date x age x gender` demand-alignment analysis
- exploratory correlation and demand-bucket comparisons

## Dashboard Demo

The repository also includes a lightweight React demo in [dashboard](dashboard) that packages the project into a solutions-style webpage.

The dashboard is designed to feel closer to a client-facing product walkthrough than a static BI export. It highlights:

- headline KPIs for spend, revenue, CTR, and ROAS
- theme-level market-demand context vs. daily campaign efficiency
- demand-bucket comparisons within each Google Trends theme
- segment-level ROAS alignment with external demand signals
- best and worst audience clusters from the internal Facebook-only analysis
- demographic performance guardrails and methodology notes

## Key Findings

### Internal Facebook EDA

- Conversions are somewhat concentrated, but not dominated by only a handful of audience clusters.
- Best-performing clusters appear to outperform mainly through stronger post-click conversion efficiency rather than dramatically higher CTR.
- Age and gender differences are large enough to justify segmentation in later analysis.
- The campaign time series is short but stable enough for exploratory alignment with an external demand signal.

### Google Trends Analysis

- External demand signals do not align with campaign performance in the same way across all themes.
- Fitness shows the clearest positive alignment with conversion efficiency and ROAS during this short time window.
- Some age and gender segments appear more positively aligned with external demand shifts than others.
- These results should be interpreted as exploratory alignment, not proof of causal impact.

## Example Business Interpretation

- Some audience clusters consistently underperform despite measurable spend, which suggests budget reallocation opportunities.
- Demand-sensitive themes may create stronger conversion efficiency even when click-through rate does not improve.
- Demographic segments do not respond uniformly to external market context, which supports more segmented campaign planning.

## Limitations

- The time window is short: only 14 days
- Google Trends is measured at the overall market level, not at the Facebook audience level
- Demand themes are manually selected exploratory topics, not exact mappings from Facebook audience codes
- Revenue is simulated from approved conversions, so ROAS is useful for relative comparison but not for real financial reporting

## How To Run

From the project root:

```bash
python src/load_campaign_data.py
python src/clean_campaign_data.py
python src/analyze_audience_clusters.py
python src/fetch_trends.py
python src/merge_trends.py
python src/load_to_sqlite.py
python src/export_dashboard_data.py
```

Then open the notebooks:

- `notebooks/01_eda.ipynb`
- `notebooks/02_analysis.ipynb`

To run the React dashboard:

```bash
cd dashboard
npm install
npm run dev
```

Then open the local Vite URL shown in your terminal.

## Suggested Presentation Flow

If you are presenting this project in a portfolio, interview, or case-study format, a strong narrative is:

1. Start with Facebook campaign cleaning and KPI engineering
2. Show which audience clusters and demographic groups perform best and worst
3. Explain why external demand context might matter
4. Introduce Google Trends as a market-level signal layer
5. Show which themes and segments appear most aligned with demand shifts
6. Close with limitations and next-step recommendations

## SQLite Tables

Running [src/load_to_sqlite.py](src/load_to_sqlite.py) creates:

- `campaign_data_cleaned`
- `audience_cluster_summary`
- `campaign_trends_daily`
- `campaign_trends_segmented`

The database is saved to:

- [data/processed/campaign_trends.db](data/processed/campaign_trends.db)

## Portfolio / Resume Framing

- Built an end-to-end analytics pipeline combining Facebook ad performance data with Google Trends signals to explore how external market demand aligns with campaign efficiency.
- Developed data-cleaning, KPI-engineering, audience-cluster aggregation, and SQL analysis workflows using Python, pandas, NumPy, and SQLite.
- Designed exploratory analysis notebooks to evaluate demographic sensitivity, audience-cluster performance, and demand-signal alignment across CTR, conversion rate, and ROAS.
