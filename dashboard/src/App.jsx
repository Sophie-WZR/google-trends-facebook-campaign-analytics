import { useEffect, useMemo, useState } from "react";

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "NA";
  }
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  }).format(value);
}

function formatCompact(value) {
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

function formatSigned(value, digits = 3) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "NA";
  }
  const formatted = formatNumber(Math.abs(value), digits);
  return value > 0 ? `+${formatted}` : value < 0 ? `-${formatted}` : formatted;
}

function titleize(text) {
  return text
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function getRecommendation(roasLift, positiveSegment) {
  if (roasLift === null) {
    return "Use this theme as a context layer only until more stable demand-bucket coverage is available.";
  }
  if (roasLift > 0.05 && positiveSegment) {
    return `Prioritize ${positiveSegment.age} ${positiveSegment.gender} when ${titleize(
      positiveSegment.trend_keyword,
    )} demand strengthens, because the theme shows a positive ROAS lift and a credible aligned segment.`;
  }
  if (roasLift > 0) {
    return "Use this theme as a directional pacing signal, but keep budget changes modest because the segment-level evidence is still mixed.";
  }
  return "Treat this theme as weak or unstable demand context for now; do not use it as a standalone optimization trigger.";
}

function MetricCard({ label, value, helper }) {
  return (
    <div className="metric-card surface-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-helper">{helper}</div>
    </div>
  );
}

function StoryCard({ label, value, helper, tone = "neutral" }) {
  return (
    <div className={`story-card surface-card ${tone}`}>
      <div className="metric-label">{label}</div>
      <div className="story-value">{value}</div>
      <div className="metric-helper">{helper}</div>
    </div>
  );
}

function SectionIntro({ eyebrow, title, description }) {
  return (
    <div className="section-intro">
      <span className="eyebrow">{eyebrow}</span>
      <div className="section-intro-row">
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
    </div>
  );
}

function ArchitectureStrip({ overview, themeCount }) {
  const items = [
    "Facebook campaign data",
    "Python cleaning and KPI engineering",
    "Google Trends context layer",
    "SQLite and SQL analysis",
    "React demo interface",
  ];

  return (
    <section className="architecture-card surface-card">
      <div className="section-heading">
        <div className="hero-copy">
          <span className="eyebrow">Solution Flow</span>
          <h2>Retail Media Demand Intelligence Console</h2>
          <div className="hero-meta">
            <span className="meta-pill">North America context</span>
            <span className="meta-pill">React demo layer</span>
            <span className="meta-pill">Exploratory demand alignment</span>
          </div>
        </div>
        <p>
          A lightweight demo environment that turns raw campaign and market-context data into a
          decision-ready walkthrough for revenue and solutions conversations.
        </p>
      </div>
      <div className="hero-glance">
        <div className="glance-card">
          <span className="section-mini-label">Data window</span>
          <strong>{`${overview.date_start} to ${overview.date_end}`}</strong>
        </div>
        <div className="glance-card">
          <span className="section-mini-label">Campaign footprint</span>
          <strong>{`${formatCompact(overview.rows)} ads | ${overview.campaigns} campaigns`}</strong>
        </div>
        <div className="glance-card">
          <span className="section-mini-label">Demand themes</span>
          <strong>{`${themeCount} context topics`}</strong>
        </div>
      </div>
      <div className="architecture-strip">
        {items.map((item, index) => (
          <div key={item} className="architecture-node">
            <span>{`0${index + 1}`}</span>
            <strong>{item}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function MiniLineChart({ series }) {
  const values = series.map((point) => point.search_interest);
  const roasValues = series.map((point) => point.roas);
  const width = 520;
  const height = 220;
  const padding = 24;
  const chartHeight = height - padding * 2;

  const scalePoints = (items) => {
    const min = Math.min(...items);
    const max = Math.max(...items);
    return items.map((value, index) => {
      const x = padding + (index * (width - padding * 2)) / Math.max(items.length - 1, 1);
      const normalized = max === min ? 0.5 : (value - min) / (max - min);
      const y = height - padding - normalized * chartHeight;
      return [x, y];
    });
  };

  const interestScaled = scalePoints(values);
  const roasScaled = scalePoints(roasValues);
  const interestPoints = interestScaled.map((point) => point.join(",")).join(" ");
  const roasPoints = roasScaled.map((point) => point.join(",")).join(" ");
  const interestArea = [
    `${padding},${height - padding}`,
    ...interestScaled.map((point) => point.join(",")),
    `${width - padding},${height - padding}`,
  ].join(" ");
  const lastInterestPoint = interestScaled[interestScaled.length - 1];
  const lastRoasPoint = roasScaled[roasScaled.length - 1];
  const gridLines = Array.from({ length: 4 }, (_, index) => {
    const y = padding + (chartHeight / 3) * index;
    return y;
  });

  return (
    <div className="chart-card surface-card">
      <div className="chart-header">
        <div>
          <h3>Theme Trend vs ROAS</h3>
          <p>Daily market-demand context and campaign efficiency</p>
        </div>
        <div className="legend-inline">
          <span className="legend-item">
            <span className="legend-swatch legend-interest" />
            Search interest
          </span>
          <span className="legend-item">
            <span className="legend-swatch legend-roas" />
            ROAS
          </span>
        </div>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="svg-chart" role="img" aria-label="Trend line chart">
        <defs>
          <linearGradient id="interestAreaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#1d4ed8" stopOpacity="0.18" />
            <stop offset="100%" stopColor="#1d4ed8" stopOpacity="0.02" />
          </linearGradient>
          <linearGradient id="roasLineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#475569" />
            <stop offset="100%" stopColor="#64748b" />
          </linearGradient>
        </defs>
        {gridLines.map((y) => (
          <line
            key={y}
            x1={padding}
            x2={width - padding}
            y1={y}
            y2={y}
            className="chart-gridline"
          />
        ))}
        <polygon fill="url(#interestAreaGradient)" points={interestArea} />
        <polyline fill="none" stroke="#1d4ed8" strokeWidth="3.5" points={interestPoints} />
        <polyline fill="none" stroke="url(#roasLineGradient)" strokeWidth="3.5" points={roasPoints} />
        {lastInterestPoint ? (
          <circle cx={lastInterestPoint[0]} cy={lastInterestPoint[1]} r="5.5" className="point-interest" />
        ) : null}
        {lastRoasPoint ? (
          <circle cx={lastRoasPoint[0]} cy={lastRoasPoint[1]} r="5.5" className="point-roas" />
        ) : null}
      </svg>
      <div className="chart-footer">
        <span>{series[0]?.date}</span>
        <span>{series[series.length - 1]?.date}</span>
      </div>
    </div>
  );
}

function BucketBars({ rows }) {
  const maxRoas = Math.max(...rows.map((row) => row.avg_roas));

  return (
    <div className="chart-card surface-card">
      <div className="chart-header">
        <div>
          <h3>Demand Bucket Comparison</h3>
          <p>Relative demand buckets within the selected theme</p>
        </div>
      </div>
      <div className="bucket-list">
        {rows.map((row) => (
          <div key={row.demand_bucket} className="bucket-row">
            <div className="bucket-meta">
              <strong>{row.demand_bucket.replace("_", " ")}</strong>
              <span>Interest {formatNumber(row.avg_search_interest, 1)}</span>
            </div>
            <div className="bucket-bar-track">
              <div
                className="bucket-bar-fill"
                style={{ width: `${(row.avg_roas / maxRoas) * 100}%` }}
              />
            </div>
            <div className="bucket-kpis">
              <span className="bucket-badge">{titleize(row.demand_bucket)}</span>
              <span>ROAS {formatNumber(row.avg_roas, 3)}</span>
              <span>CVR {formatNumber(row.avg_conversion_rate, 4)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SensitivityTable({ title, rows }) {
  const maxAbs = Math.max(0.001, ...rows.map((row) => Math.abs(row.corr_with_roas)));

  return (
    <div className="table-card surface-card">
      <div className="chart-header">
        <div>
          <h3>{title}</h3>
          <p>Filtered to segments with meaningful spend and at least 12 days</p>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>Segment</th>
            <th>ROAS Corr.</th>
            <th>Signal</th>
            <th>Spend</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={`${row.age}-${row.gender}-${row.trend_keyword}`}>
              <td>{`${row.age} | ${row.gender}`}</td>
              <td>{formatSigned(row.corr_with_roas, 3)}</td>
              <td>
                <div className="signal-meter">
                  <div className="signal-meter-track" />
                  <div
                    className={`signal-meter-fill ${row.corr_with_roas >= 0 ? "positive" : "negative"}`}
                    style={{ width: `${(Math.abs(row.corr_with_roas) / maxAbs) * 100}%` }}
                  />
                </div>
              </td>
              <td>{formatNumber(row.total_spent, 2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ClusterList({ title, rows, tone }) {
  const getStatus = (row) => {
    if (tone === "positive") {
      return row.spent <= 20 ? "Promising" : "Scale";
    }
    return row.spent >= 100 ? "Pause" : "Review";
  };

  const getSummary = (row) => {
    if (tone === "positive") {
      return row.spent <= 20
        ? "High efficiency on light spend. Validate with controlled scaling."
        : "Strong relative ROAS. Consider careful budget expansion.";
    }
    return row.roas === 0
      ? "Spend occurred without meaningful return. Review targeting or deprioritize."
      : "Weak efficiency signal. Inspect audience fit before further spend.";
  };

  return (
    <div className={`cluster-card surface-card ${tone}`}>
      <div className="chart-header">
        <div>
          <h3>{title}</h3>
          <p>Eligible audience clusters from the Facebook-only analysis</p>
        </div>
      </div>
      <div className="cluster-list">
        {rows.map((row) => (
          <div key={row.audience_cluster_label} className={`candidate-tile ${tone}`}>
            <div className="candidate-header">
              <div>
                <strong>{row.audience_cluster_label}</strong>
                <div className="cluster-meta">{row.audience_cluster_key}</div>
              </div>
              <span className={`status-chip ${tone}`}>{getStatus(row)}</span>
            </div>
            <div className="cluster-meta">{row.age_modes} | {row.gender_modes}</div>
            <div className="candidate-metrics">
              <div>
                <span className="candidate-label">ROAS</span>
                <strong>{formatNumber(row.roas, 3)}</strong>
              </div>
              <div>
                <span className="candidate-label">Spend</span>
                <strong>{formatNumber(row.spent, 2)}</strong>
              </div>
            </div>
            <div className="candidate-summary">{getSummary(row)}</div>
            <div className="candidate-strength-track">
              <div
                className={`candidate-strength-fill ${tone}`}
                style={{
                  width: `${Math.min(
                    100,
                    tone === "positive" ? row.roas * 12 : Math.max(15, row.spent / 2),
                  )}%`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function DemographicTable({ rows }) {
  return (
    <div className="table-card wide surface-card">
      <div className="chart-header">
        <div>
          <h3>Age and Gender Performance</h3>
          <p>Internal Facebook performance before external theme interpretation</p>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>Age</th>
            <th>Gender</th>
            <th>CTR</th>
            <th>CVR</th>
            <th>ROAS</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={`${row.age}-${row.gender}`}>
              <td>{row.age}</td>
              <td>{row.gender}</td>
              <td>{formatNumber(row.ctr, 6)}</td>
              <td>{formatNumber(row.conversion_rate, 4)}</td>
              <td>{formatNumber(row.roas, 4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function InsightPanel({ theme, insight }) {
  return (
    <div className="methodology-card insight-panel surface-card">
      <h3>{`${theme} Theme Readout`}</h3>
      <ul className="insight-list">
        <li>{insight.bucketMessage}</li>
        <li>{insight.positiveMessage}</li>
        <li>{insight.negativeMessage}</li>
      </ul>
    </div>
  );
}

function ThemeSelector({ themes, selectedTheme, onSelect }) {
  return (
    <div className="selector-stack">
      {themes.map((theme) => (
        <button
          key={theme}
          type="button"
          className={`theme-pill ${theme === selectedTheme ? "active" : ""}`}
          onClick={() => onSelect(theme)}
        >
          {titleize(theme)}
        </button>
      ))}
    </div>
  );
}

function RecommendationCard({ theme, recommendation }) {
  return (
    <div className="recommendation-card surface-card">
      <div className="section-mini-label">Recommended action</div>
      <h3>{`${theme} playbook`}</h3>
      <p>{recommendation}</p>
    </div>
  );
}

export default function App() {
  const [data, setData] = useState(null);
  const [selectedTheme, setSelectedTheme] = useState("fitness");
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/dashboard_data.json`)
      .then((response) => response.json())
      .then((payload) => {
        setData(payload);
        if (payload.themes?.length && !payload.themes.includes(selectedTheme)) {
          setSelectedTheme(payload.themes[0]);
        }
      })
      .catch(() => {
        setError("Could not load dashboard data. Run `python src/export_dashboard_data.py` and try again.");
      });
  }, []);

  const selectedSeries = useMemo(
    () => data?.dailyThemeSeries?.[selectedTheme] ?? [],
    [data, selectedTheme],
  );
  const selectedBuckets = useMemo(
    () => data?.demandBucketSummary?.[selectedTheme] ?? [],
    [data, selectedTheme],
  );
  const selectedSensitivity = useMemo(
    () => data?.segmentSensitivity?.[selectedTheme] ?? { top_positive: [], top_negative: [] },
    [data, selectedTheme],
  );
  const selectedInsight = useMemo(() => {
    const lowBucket = selectedBuckets.find((row) => row.demand_bucket === "low_demand");
    const highBucket = selectedBuckets.find((row) => row.demand_bucket === "high_demand");
    const bestPositive = selectedSensitivity.top_positive[0];
    const worstNegative = selectedSensitivity.top_negative[0];
    const roasLift =
      lowBucket && highBucket ? highBucket.avg_roas - lowBucket.avg_roas : null;

    const bucketMessage =
      roasLift === null
        ? "Demand buckets are unavailable for this theme."
        : roasLift >= 0
          ? `High-demand days show a ${formatSigned(roasLift)} ROAS lift versus low-demand days.`
          : `High-demand days show a ${formatSigned(roasLift)} ROAS change versus low-demand days.`;

    const positiveMessage =
      bestPositive && bestPositive.corr_with_roas > 0
        ? `${bestPositive.age} ${bestPositive.gender} has the strongest positive ROAS alignment at ${formatSigned(bestPositive.corr_with_roas)}.`
        : "No segment shows a strong positive ROAS alignment after the spend and coverage filters.";

    const negativeMessage =
      worstNegative && worstNegative.corr_with_roas < 0
        ? `${worstNegative.age} ${worstNegative.gender} shows the weakest alignment at ${formatSigned(worstNegative.corr_with_roas)}.`
        : "No clearly negative segment-level ROAS alignment survives the filtering rules.";

    return {
      roasLift,
      bestPositive,
      worstNegative,
      bucketMessage,
      positiveMessage,
      negativeMessage,
      recommendation: getRecommendation(roasLift, bestPositive),
    };
  }, [selectedBuckets, selectedSensitivity]);

  if (!data) {
    if (error) {
      return <div className="loading">{error}</div>;
    }
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="page-shell">
      <ArchitectureStrip overview={data.overview} themeCount={data.themes.length} />
      <div className="app-grid">
        <aside className="control-rail">
          <div className="rail-card surface-card">
            <div className="section-mini-label">Demand theme</div>
            <h3>Choose a market context</h3>
            <p>Switch themes to simulate how a solutions team might walk a retailer through context-sensitive campaign decisions.</p>
            <ThemeSelector
              themes={data.themes}
              selectedTheme={selectedTheme}
              onSelect={setSelectedTheme}
            />
          </div>

          <RecommendationCard
            theme={titleize(selectedTheme)}
            recommendation={selectedInsight.recommendation}
          />

          <div className="rail-card surface-card">
            <div className="section-mini-label">Scope guardrail</div>
            <p>{data.methodology.scope_note}</p>
            <p>{data.methodology.limitation_note}</p>
          </div>
        </aside>

        <main className="dashboard-main">
          <SectionIntro
            eyebrow="Executive View"
            title="Campaign health and demand context"
            description="Start with top-line efficiency, then move into theme-level context and segment sensitivity. The layout is designed to mirror how a solutions engineer might guide a live customer demo."
          />

          <section className="metrics-grid">
            <MetricCard
              label="Total Spend"
              value={`$${formatCompact(data.overview.total_spend)}`}
              helper={`${data.overview.date_start} to ${data.overview.date_end}`}
            />
            <MetricCard
              label="Total Revenue"
              value={`$${formatCompact(data.overview.total_revenue)}`}
              helper="Simulated from approved conversions"
            />
            <MetricCard
              label="Average CTR"
              value={formatNumber(data.overview.avg_ctr, 6)}
              helper={`${formatCompact(data.overview.rows)} ad rows`}
            />
            <MetricCard
              label="Average ROAS"
              value={formatNumber(data.overview.avg_roas, 4)}
              helper={`${formatCompact(data.overview.audience_clusters)} audience clusters`}
            />
          </section>

          <section className="three-column">
            <StoryCard
              label="Selected Theme"
              value={titleize(selectedTheme)}
              helper="Manual market-context topic for exploratory demand analysis"
              tone="teal"
            />
            <StoryCard
              label="High vs Low Demand ROAS"
              value={selectedInsight.roasLift === null ? "NA" : formatSigned(selectedInsight.roasLift, 3)}
              helper="Difference between high-demand and low-demand bucket averages"
              tone={selectedInsight.roasLift >= 0 ? "green" : "orange"}
            />
            <StoryCard
              label="Strongest Segment Signal"
              value={
                selectedInsight.bestPositive && selectedInsight.bestPositive.corr_with_roas > 0
                  ? `${selectedInsight.bestPositive.age} | ${selectedInsight.bestPositive.gender}`
                  : "No strong positive"
              }
              helper="Highest positive ROAS correlation after filtering"
              tone="ink"
            />
          </section>

          <SectionIntro
            eyebrow="Demand Signal"
            title="Theme response and market context"
            description="These visuals show whether the selected Google Trends theme aligns with stronger or weaker campaign efficiency over the 14-day window."
          />
          <section className="two-column">
            <MiniLineChart series={selectedSeries} />
            <BucketBars rows={selectedBuckets} />
          </section>

          <section className="single-column">
            <InsightPanel theme={titleize(selectedTheme)} insight={selectedInsight} />
          </section>

          <SectionIntro
            eyebrow="Audience Actions"
            title="Segment alignment and cluster decisions"
            description="Use the filtered segment signals to identify who appears most demand-sensitive, then pair that with best and worst audience clusters from the Facebook-only analysis."
          />
          <section className="two-column">
            <SensitivityTable title="Highest Segment ROAS Correlations" rows={selectedSensitivity.top_positive} />
            <SensitivityTable title="Lowest Segment ROAS Correlations" rows={selectedSensitivity.top_negative} />
          </section>

          <section className="two-column">
            <ClusterList title="Scale Candidates" rows={data.clusterCards.best} tone="positive" />
            <ClusterList title="Review or Deprioritize" rows={data.clusterCards.worst} tone="negative" />
          </section>

          <section className="single-column">
            <DemographicTable rows={data.ageGenderSummary} />
          </section>
        </main>
      </div>
    </div>
  );
}
