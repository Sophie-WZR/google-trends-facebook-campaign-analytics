-- 1. Overall market-demand alignment by trend theme
SELECT
    trend_keyword,
    ROUND(AVG(search_interest), 2) AS avg_search_interest,
    ROUND(AVG(ctr), 6) AS avg_ctr,
    ROUND(AVG(conversion_rate), 4) AS avg_conversion_rate,
    ROUND(AVG(roas), 4) AS avg_roas
FROM campaign_trends_daily
GROUP BY trend_keyword
ORDER BY avg_search_interest DESC;


-- 2. Demand bucket performance comparison at the daily overall level
WITH demand_ranked AS (
    SELECT
        *,
        NTILE(3) OVER (PARTITION BY trend_keyword ORDER BY search_interest) AS demand_bucket_num
    FROM campaign_trends_daily
),
demand_labeled AS (
    SELECT
        *,
        CASE demand_bucket_num
            WHEN 1 THEN 'low_demand'
            WHEN 2 THEN 'mid_demand'
            ELSE 'high_demand'
        END AS demand_bucket
    FROM demand_ranked
)
SELECT
    trend_keyword,
    demand_bucket,
    ROUND(AVG(search_interest), 2) AS avg_search_interest,
    ROUND(AVG(ctr), 6) AS avg_ctr,
    ROUND(AVG(conversion_rate), 4) AS avg_conversion_rate,
    ROUND(AVG(roas), 4) AS avg_roas
FROM demand_labeled
GROUP BY trend_keyword, demand_bucket
ORDER BY trend_keyword, avg_search_interest;


-- 3. Age and gender segment performance under external demand context
SELECT
    age,
    gender,
    ROUND(AVG(ctr), 6) AS avg_ctr,
    ROUND(AVG(conversion_rate), 4) AS avg_conversion_rate,
    ROUND(AVG(roas), 4) AS avg_roas,
    ROUND(SUM(spent), 2) AS total_spent,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM campaign_trends_segmented
GROUP BY age, gender
ORDER BY avg_roas DESC;


-- 4. Segment-level demand sensitivity using simple ROAS spread between high and low search-interest days
WITH segment_ranked AS (
    SELECT
        *,
        NTILE(3) OVER (PARTITION BY trend_keyword, age, gender ORDER BY search_interest) AS demand_bucket_num
    FROM campaign_trends_segmented
),
segment_labeled AS (
    SELECT
        *,
        CASE demand_bucket_num
            WHEN 1 THEN 'low_demand'
            WHEN 2 THEN 'mid_demand'
            ELSE 'high_demand'
        END AS demand_bucket
    FROM segment_ranked
),
segment_summary AS (
    SELECT
        trend_keyword,
        age,
        gender,
        demand_bucket,
        AVG(roas) AS avg_roas,
        SUM(spent) AS total_spent
    FROM segment_labeled
    GROUP BY trend_keyword, age, gender, demand_bucket
)
SELECT
    high.trend_keyword,
    high.age,
    high.gender,
    ROUND(low.avg_roas, 4) AS low_demand_roas,
    ROUND(high.avg_roas, 4) AS high_demand_roas,
    ROUND(high.avg_roas - low.avg_roas, 4) AS roas_lift_high_minus_low
FROM segment_summary AS high
JOIN segment_summary AS low
    ON high.trend_keyword = low.trend_keyword
   AND high.age = low.age
   AND high.gender = low.gender
WHERE high.demand_bucket = 'high_demand'
  AND low.demand_bucket = 'low_demand'
ORDER BY roas_lift_high_minus_low DESC;


-- 5. Audience clusters with meaningful spend but weak returns
SELECT
    audience_cluster_label,
    audience_cluster_key,
    ads,
    ROUND(spent, 2) AS spent,
    approved_conversion,
    ROUND(revenue, 2) AS revenue,
    ROUND(roas, 4) AS roas,
    ROUND(cpa, 2) AS cpa
FROM audience_cluster_summary
WHERE eligible_for_ranking = 1
ORDER BY roas ASC, spent DESC
LIMIT 15;
