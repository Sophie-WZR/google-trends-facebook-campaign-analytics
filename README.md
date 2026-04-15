# Google Trends + Facebook Ad Campaign Analytics

An end-to-end analytics project that combines Facebook ad performance data with Google Trends signals to evaluate how external market demand relates to campaign efficiency.

## What This Project Does

This project builds a small analytics pipeline to connect internal campaign performance with external demand signals:

- Clean and validate Facebook campaign data
- Engineer core marketing KPIs (CTR, conversion rate, CPC, CPA, ROAS)
- Aggregate audience-cluster performance
- Integrate Google Trends as a market-level demand signal
- Analyze whether campaign efficiency moves with external demand over time

## Data

- Facebook ad campaign dataset (Kaggle)
- Google Trends data (via `pytrends`)

## Tech Stack

Python, pandas, NumPy, SQL, SQLite, Jupyter, React (Vite)

## Pipeline

1. Clean campaign data and engineer KPIs  
2. Build audience-cluster summaries  
3. Perform internal EDA (demographics, ROAS distribution)  
4. Fetch Google Trends time series for selected themes  
5. Merge demand signals with campaign performance  
6. Analyze alignment at daily and segmented levels  
7. Store outputs in SQLite for query-based analysis  

## Key Findings

**Internal performance**
- Conversion differences are driven more by post-click efficiency than CTR
- Audience performance is heterogeneous but not dominated by a few clusters
- Demographic differences are large enough to justify segmentation

**Demand alignment**
- External demand does not align uniformly across themes
- Fitness-related demand shows the strongest positive alignment with ROAS
- Some demographic segments are more sensitive to demand shifts than others

## Business Interpretation

- Underperforming audience clusters suggest clear budget reallocation opportunities  
- Demand-sensitive themes can improve conversion efficiency even without higher CTR  
- Campaign performance should be analyzed jointly with external market context, not in isolation  

## Method Notes

- Audience codes are treated as categorical clusters rather than semantic variables  
- Google Trends is used as a market-level signal, not user-level intent  
- Demand themes are manually defined and exploratory  
- Revenue is simulated, so ROAS is relative rather than financial  

## Limitations

- Short time window (14 days)  
- No direct mapping between Trends data and Facebook audiences  
- Results are correlational, not causal  

## Dashboard

A lightweight React demo is included in `/dashboard` to present results as a product-style walkthrough.

## Run

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
