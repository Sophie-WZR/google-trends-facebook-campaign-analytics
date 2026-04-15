# Google Trends + Facebook Ad Campaign Analytics

An end-to-end analytics project combining Facebook ad performance data with Google Trends signals to evaluate how external market demand relates to campaign efficiency.

## Data & Tools

- Facebook ad campaign dataset (Kaggle)  
- Google Trends data (`pytrends`)  

Python, pandas, NumPy, SQL, SQLite, Jupyter, React (Vite)

## Pipeline

1. Clean campaign data and engineer KPIs (CTR, conversion rate, CPC, CPA, ROAS)  
2. Build audience-cluster summaries from Facebook audience codes  
3. Perform internal EDA (demographics, ROAS distribution)  
4. Fetch Google Trends time series for selected demand themes  
5. Merge demand signals with campaign performance  
6. Analyze alignment at daily and segmented (`date × age × gender`) levels  
7. Store outputs in SQLite for query-based analysis  

## Key Findings

**Internal performance**
- Conversion differences are driven more by post-click efficiency than CTR  
- Audience performance is heterogeneous but not dominated by a few clusters  
- Demographic differences are large enough to justify segmentation  

**Demand alignment**
- External demand does not align uniformly across themes  
- Fitness-related demand shows the strongest positive alignment with ROAS in this sample  
- Some demographic segments appear more sensitive to demand shifts than others  

## Business Interpretation

- Underperforming audience clusters suggest clear budget reallocation opportunities  
- Demand-sensitive themes can improve conversion efficiency even without higher CTR  
- Campaign performance should be evaluated alongside external market context, not in isolation  

## Method Notes

- Audience codes are treated as categorical clusters rather than semantic variables  
- Google Trends is used as a market-level demand signal, not user-level intent  
- Demand themes are manually defined and exploratory  

## Limitations

- Short time window (14 days)  
- No direct mapping between Trends data and Facebook audiences  
- Results are correlational, not causal  

## Dashboard

A React dashboard in `/dashboard` presents the analysis as a lightweight product-style demo.

## Run

```bash
python src/load_campaign_data.py
python src/clean_campaign_data.py
python src/analyze_audience_clusters.py
python src/fetch_trends.py
python src/merge_trends.py
python src/load_to_sqlite.py
python src/export_dashboard_data.py

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
