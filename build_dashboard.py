import json
from pathlib import Path
import pandas as pd

FOLDER = Path(__file__).resolve().parent
ANALYTICS_FILE = FOLDER / "aqi_analytics.xlsx"
OUTPUT_HTML = FOLDER / "index.html"

def load_data():
    excel = pd.ExcelFile(ANALYTICS_FILE)
    return {s: pd.read_excel(excel, s) for s in excel.sheet_names}

def build_dashboard():
    sheets = load_data()
    
    categories = sheets["AQI Categories"].to_dict(orient="records")
    pollutants = sheets["Pollutant Frequency"].to_dict(orient="records")
    seasons = sheets["Seasonal Analysis"].to_dict(orient="records")
    weekdays = sheets["Weekday Analysis"].to_dict(orient="records")
    states = sheets["State Analysis"].to_dict(orient="records")
    cities = sheets["City Analysis"].to_dict(orient="records")
    monthly = sheets["Monthly Trends"].copy()
    monthly["month_str"] = pd.to_datetime(monthly["month"]).dt.strftime("%b %Y")
    monthly_data = monthly.to_dict(orient="records")
    state_shares = sheets["State Category Shares"].to_dict(orient="records")
    overview = dict(zip(sheets["Overview"]["Metric"], sheets["Overview"]["Value"]))
    insights = dict(zip(sheets["Key Insights"]["Finding"], sheets["Key Insights"]["Result"]))

    # Prepare JSON structures for frontend
    data_json = json.dumps({
        "categories": categories,
        "pollutants": pollutants,
        "seasons": seasons,
        "weekdays": weekdays,
        "states": states,
        "cities": cities,
        "monthly": monthly_data,
        "state_shares": state_shares,
        "overview": overview,
        "insights": insights
    }, default=str)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Air Quality Index (AQI) Executive Dashboard</title>
  <!-- Chart.js CDN with fallback handling -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg-primary: #0f172a;
      --bg-secondary: #1e293b;
      --bg-card: #1e293b;
      --border-color: #334155;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      --accent-blue: #38bdf8;
      --accent-purple: #a855f7;
      --good: #10b981;
      --satisfactory: #84cc16;
      --moderate: #eab308;
      --poor: #f97316;
      --very-poor: #ef4444;
      --severe: #991b1b;
      --card-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.2);
    }}

    [data-theme="light"] {{
      --bg-primary: #f8fafc;
      --bg-secondary: #ffffff;
      --bg-card: #ffffff;
      --border-color: #e2e8f0;
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #94a3b8;
      --card-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.02);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      transition: background-color 0.2s ease, border-color 0.2s ease;
    }}

    body {{
      background-color: var(--bg-primary);
      color: var(--text-primary);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    /* Header */
    header {{
      background-color: var(--bg-secondary);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 50;
    }}

    .header-container {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 1rem 1.5rem;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .brand-icon {{
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, #0284c7, #38bdf8);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      color: white;
      box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.4);
    }}

    .brand-text h1 {{
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}

    .brand-text p {{
      font-size: 0.75rem;
      color: var(--text-secondary);
    }}

    .nav-tabs {{
      display: flex;
      gap: 0.5rem;
      background-color: var(--bg-primary);
      padding: 0.25rem;
      border-radius: 8px;
      border: 1px solid var(--border-color);
    }}

    .nav-tab {{
      padding: 0.5rem 1rem;
      font-size: 0.85rem;
      font-weight: 600;
      border-radius: 6px;
      border: none;
      background: transparent;
      color: var(--text-secondary);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}

    .nav-tab.active {{
      background-color: var(--bg-secondary);
      color: var(--accent-blue);
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }}

    .theme-toggle {{
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      padding: 0.5rem 0.85rem;
      border-radius: 8px;
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    /* Container */
    main {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 1.5rem;
      flex: 1;
      width: 100%;
    }}

    /* KPI Grid */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1.25rem;
      margin-bottom: 1.5rem;
    }}

    .kpi-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1.25rem;
      box-shadow: var(--card-shadow);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      overflow: hidden;
    }}

    .kpi-card::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      width: 4px;
      height: 100%;
      background: var(--accent-blue);
    }}

    .kpi-card.moderate::before {{ background: var(--moderate); }}
    .kpi-card.records::before {{ background: var(--accent-blue); }}
    .kpi-card.delhi::before {{ background: var(--very-poor); }}
    .kpi-card.clean::before {{ background: var(--good); }}

    .kpi-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
    }}

    .kpi-title {{
      font-size: 0.8rem;
      text-transform: uppercase;
      font-weight: 700;
      color: var(--text-secondary);
      letter-spacing: 0.05em;
    }}

    .kpi-badge {{
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.2rem 0.5rem;
      border-radius: 20px;
      background: rgba(234, 179, 8, 0.2);
      color: var(--moderate);
    }}

    .kpi-badge.good {{ background: rgba(16, 185, 129, 0.2); color: var(--good); }}
    .kpi-badge.very-poor {{ background: rgba(239, 68, 68, 0.2); color: var(--very-poor); }}
    .kpi-badge.blue {{ background: rgba(56, 189, 248, 0.2); color: var(--accent-blue); }}

    .kpi-value {{
      font-size: 2rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      margin-bottom: 0.25rem;
    }}

    .kpi-footer {{
      font-size: 0.75rem;
      color: var(--text-muted);
    }}

    /* AQI Legend Bar */
    .aqi-scale-bar {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1rem 1.25rem;
      margin-bottom: 1.5rem;
      box-shadow: var(--card-shadow);
    }}

    .scale-title {{
      font-size: 0.8rem;
      font-weight: 700;
      margin-bottom: 0.75rem;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .scale-steps {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 0.5rem;
    }}

    .scale-step {{
      padding: 0.5rem;
      border-radius: 6px;
      text-align: center;
      font-size: 0.75rem;
      font-weight: 600;
      color: white;
    }}

    .step-good {{ background: var(--good); }}
    .step-satisfactory {{ background: var(--satisfactory); color: #1e293b; }}
    .step-moderate {{ background: var(--moderate); color: #1e293b; }}
    .step-poor {{ background: var(--poor); }}
    .step-very-poor {{ background: var(--very-poor); }}
    .step-severe {{ background: var(--severe); }}

    /* Grid Layouts */
    .grid-2 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
      gap: 1.5rem;
      margin-bottom: 1.5rem;
    }}

    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.5rem;
      margin-bottom: 1.5rem;
    }}

    .card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1.25rem;
      box-shadow: var(--card-shadow);
      display: flex;
      flex-direction: column;
    }}

    .card-title {{
      font-size: 1rem;
      font-weight: 700;
      margin-bottom: 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .card-subtitle {{
      font-size: 0.75rem;
      color: var(--text-secondary);
      font-weight: 400;
    }}

    .chart-container {{
      position: relative;
      flex: 1;
      min-height: 280px;
      width: 100%;
    }}

    /* Table styling */
    .table-wrapper {{
      overflow-x: auto;
      max-height: 480px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.85rem;
    }}

    th {{
      background-color: var(--bg-primary);
      color: var(--text-secondary);
      font-weight: 700;
      padding: 0.75rem 1rem;
      position: sticky;
      top: 0;
      border-bottom: 2px solid var(--border-color);
      white-space: nowrap;
    }}

    td {{
      padding: 0.75rem 1rem;
      border-bottom: 1px solid var(--border-color);
      color: var(--text-primary);
      white-space: nowrap;
    }}

    tr:hover td {{
      background-color: rgba(56, 189, 248, 0.05);
    }}

    .search-input {{
      padding: 0.5rem 0.75rem;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      background-color: var(--bg-primary);
      color: var(--text-primary);
      font-size: 0.85rem;
      outline: none;
      width: 240px;
    }}

    .search-input:focus {{
      border-color: var(--accent-blue);
    }}

    .pill {{
      display: inline-block;
      padding: 0.2rem 0.5rem;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 700;
      color: white;
    }}

    /* Tab content hiding */
    .tab-pane {{
      display: none;
    }}

    .tab-pane.active {{
      display: block;
    }}

    /* Footer */
    footer {{
      background-color: var(--bg-secondary);
      border-top: 1px solid var(--border-color);
      padding: 1.25rem 1.5rem;
      text-align: center;
      font-size: 0.8rem;
      color: var(--text-secondary);
      margin-top: 2rem;
    }}

    @media (max-width: 768px) {{
      .grid-2, .grid-3 {{
        grid-template-columns: 1fr;
      }}
      .search-input {{
        width: 100%;
      }}
    }}
  </style>
</head>
<body data-theme="dark">

  <!-- Header -->
  <header>
    <div class="header-container">
      <div class="brand">
        <div class="brand-icon">💨</div>
        <div class="brand-text">
          <h1>India Air Quality Index (AQI) Dashboard</h1>
          <p>CPCB Ambient Air Quality Monitoring | 235,785 Observations Analyzed</p>
        </div>
      </div>

      <nav class="nav-tabs">
        <button class="nav-tab active" onclick="switchTab('overview')">📊 National Overview</button>
        <button class="nav-tab" onclick="switchTab('geography')">🗺️ State & City Rankings</button>
        <button class="nav-tab" onclick="switchTab('seasons')">🌦️ Seasonal & Trends</button>
        <button class="nav-tab" onclick="switchTab('data')">📑 Data Health & Shares</button>
      </nav>

      <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">☀️ Light Mode</button>
    </div>
  </header>

  <!-- Main Content -->
  <main>

    <!-- TAB 1: OVERVIEW -->
    <div id="tab-overview" class="tab-pane active">
      <!-- KPI Row -->
      <div class="kpi-grid">
        <div class="kpi-card moderate">
          <div class="kpi-header">
            <span class="kpi-title">National Average AQI</span>
            <span class="kpi-badge">Moderate</span>
          </div>
          <div class="kpi-value">{overview.get('Average AQI', '111.2')}</div>
          <div class="kpi-footer">Median: {overview.get('Median AQI', '92.0')} | Std Dev: {overview.get('AQI standard deviation', '68.4')}</div>
        </div>

        <div class="kpi-card records">
          <div class="kpi-header">
            <span class="kpi-title">Monitored Observations</span>
            <span class="kpi-badge blue">Complete</span>
          </div>
          <div class="kpi-value">{int(overview.get('Complete AQI observations', 235785)):,}</div>
          <div class="kpi-footer">Across {overview.get('States / territories', 32)} States & {overview.get('Cities / areas', 289)} Cities</div>
        </div>

        <div class="kpi-card delhi">
          <div class="kpi-header">
            <span class="kpi-title">Highest State Avg AQI</span>
            <span class="kpi-badge very-poor">Delhi</span>
          </div>
          <div class="kpi-value">206.42</div>
          <div class="kpi-footer">Poor / Severe | 1,125 observations</div>
        </div>

        <div class="kpi-card clean">
          <div class="kpi-header">
            <span class="kpi-title">Cleanest State Avg AQI</span>
            <span class="kpi-badge good">Mizoram</span>
          </div>
          <div class="kpi-value">47.25</div>
          <div class="kpi-footer">Good Category | 1,000 observations</div>
        </div>
      </div>

      <!-- AQI Scale Explanation Bar -->
      <div class="aqi-scale-bar">
        <div class="scale-title">National Air Quality Index (NAQI) Standard Bands</div>
        <div class="scale-steps">
          <div class="scale-step step-good">Good (0–50)</div>
          <div class="scale-step step-satisfactory">Satisfactory (51–100)</div>
          <div class="scale-step step-moderate">Moderate (101–200)</div>
          <div class="scale-step step-poor">Poor (201–300)</div>
          <div class="scale-step step-very-poor">Very Poor (301–400)</div>
          <div class="scale-step step-severe">Severe (401–500)</div>
        </div>
      </div>

      <!-- Main Charts Grid -->
      <div class="grid-2">
        <div class="card">
          <div class="card-title">
            <span>📈 Monthly Average AQI Timeline</span>
            <span class="card-subtitle">Peak in Winter (Dec) • Low in Monsoon (Aug)</span>
          </div>
          <div class="chart-container">
            <canvas id="monthlyTrendChart"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-title">
            <span>🎯 Observations by AQI Category</span>
            <span class="card-subtitle">37.7% Satisfactory • 32.9% Moderate</span>
          </div>
          <div class="chart-container">
            <canvas id="categoryDonutChart"></canvas>
          </div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-title">
            <span>🏭 Top 10 Most Impacted States</span>
            <span class="card-subtitle">Ranked by Average AQI</span>
          </div>
          <div class="chart-container">
            <canvas id="topStatesChart"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-title">
            <span>💨 Dominant Pollutants Distribution</span>
            <span class="card-subtitle">Share of Mentions (PM10 & PM2.5 dominate 79.7%)</span>
          </div>
          <div class="chart-container">
            <canvas id="pollutantsChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: GEOGRAPHIC RANKINGS -->
    <div id="tab-geography" class="tab-pane">
      <div class="grid-2" style="margin-bottom: 1.5rem;">
        <div class="card">
          <div class="card-title">
            <span>🔥 10 Most Polluted Cities in India</span>
            <span class="card-subtitle">Cities with ≥30 monitoring records</span>
          </div>
          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>City / Area</th>
                  <th>State</th>
                  <th>Avg AQI</th>
                  <th>Category</th>
                </tr>
              </thead>
              <tbody id="topCitiesTable"></tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <div class="card-title">
            <span>🌿 Cleanest States / Territories</span>
            <span class="card-subtitle">Lowest average AQI across India</span>
          </div>
          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>State</th>
                  <th>Avg AQI</th>
                  <th>Median</th>
                  <th>Observations</th>
                </tr>
              </thead>
              <tbody id="cleanStatesTable"></tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span>📍 All 32 States & Union Territories AQI Table</span>
          <input type="text" id="stateSearch" class="search-input" placeholder="🔍 Search state..." onkeyup="filterStatesTable()">
        </div>
        <div class="table-wrapper">
          <table id="allStatesTable">
            <thead>
              <tr>
                <th>State / UT</th>
                <th>Average AQI</th>
                <th>Median AQI</th>
                <th>Max AQI</th>
                <th>Monitored Cities</th>
                <th>Observations</th>
                <th>Status Category</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 3: SEASONS & TEMPORAL -->
    <div id="tab-seasons" class="tab-pane">
      <div class="kpi-grid">
        <div class="kpi-card delhi">
          <div class="kpi-header">
            <span class="kpi-title">Winter (Dec–Feb)</span>
            <span class="kpi-badge very-poor">Highest</span>
          </div>
          <div class="kpi-value">143.13</div>
          <div class="kpi-footer">Inversion & Biomass burning • 59,302 records</div>
        </div>

        <div class="kpi-card clean">
          <div class="kpi-header">
            <span class="kpi-title">Monsoon (Jun–Sep)</span>
            <span class="kpi-badge good">Cleanest</span>
          </div>
          <div class="kpi-value">72.12</div>
          <div class="kpi-footer">Rain wash-out effect • 72,893 records</div>
        </div>

        <div class="kpi-card moderate">
          <div class="kpi-header">
            <span class="kpi-title">Post-Monsoon (Oct–Nov)</span>
            <span class="kpi-badge">Spike</span>
          </div>
          <div class="kpi-value">134.35</div>
          <div class="kpi-footer">Crop stubble burning • 40,004 records</div>
        </div>

        <div class="kpi-card moderate">
          <div class="kpi-header">
            <span class="kpi-title">Summer (Mar–May)</span>
            <span class="kpi-badge">Moderate</span>
          </div>
          <div class="kpi-value">111.39</div>
          <div class="kpi-footer">High wind dispersal • 63,586 records</div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-title">
            <span>🌦️ Seasonal AQI Comparison</span>
            <span class="card-subtitle">Significant reduction during Monsoon</span>
          </div>
          <div class="chart-container">
            <canvas id="seasonChart"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-title">
            <span>📅 Day-of-Week AQI Variation</span>
            <span class="card-subtitle">Remarkably steady across Monday to Sunday (~111)</span>
          </div>
          <div class="chart-container">
            <canvas id="weekdayChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: DATA HEALTH & SHARES -->
    <div id="tab-data" class="tab-pane">
      <div class="grid-2">
        <div class="card">
          <div class="card-title">
            <span>✅ Data Cleaning & Quality Audit</span>
            <span class="card-subtitle">Pipeline Verification Checks</span>
          </div>
          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Audit Check</th>
                  <th>Result</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>Source Records</td><td>235,785 rows</td><td><span class="pill" style="background:var(--accent-blue);">Verified</span></td></tr>
                <tr><td>Duplicate Rows</td><td>0 duplicates</td><td><span class="pill" style="background:var(--good);">Passed</span></td></tr>
                <tr><td>Missing Critical Values</td><td>0 missing in Date, State, AQI</td><td><span class="pill" style="background:var(--good);">Passed</span></td></tr>
                <tr><td>AQI Range Check (0–500)</td><td>Min: 0, Max: 500</td><td><span class="pill" style="background:var(--good);">Passed</span></td></tr>
                <tr><td>CPCB Category Consistency</td><td>100% matched to standards</td><td><span class="pill" style="background:var(--good);">Passed</span></td></tr>
                <tr><td>Station Count (> 0)</td><td>All stations positive</td><td><span class="pill" style="background:var(--good);">Passed</span></td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <div class="card-title">
            <span>📊 State AQI Category Distribution (%)</span>
            <span class="card-subtitle">Share of Good vs Severe days per state</span>
          </div>
          <div class="table-wrapper">
            <table id="stateSharesTable">
              <thead>
                <tr>
                  <th>State</th>
                  <th>% Good</th>
                  <th>% Satisfactory</th>
                  <th>% Moderate</th>
                  <th>% Poor+</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

  </main>

  <!-- Footer -->
  <footer>
    <p>Air Quality Index (AQI) Data Analytics & Visualization (DAV) Project | Central Pollution Control Board (CPCB) Standard</p>
    <p style="margin-top: 0.35rem; color: var(--text-muted);">Self-contained dashboard generated from verified analytics pipeline</p>
  </footer>

  <script>
    const DATA = {data_json};

    function getAqiBadge(val) {{
      if (val <= 50) return `<span class="pill" style="background:var(--good)">Good (${{val}})</span>`;
      if (val <= 100) return `<span class="pill" style="background:var(--satisfactory); color:#1e293b">Satisfactory (${{val}})</span>`;
      if (val <= 200) return `<span class="pill" style="background:var(--moderate); color:#1e293b">Moderate (${{val}})</span>`;
      if (val <= 300) return `<span class="pill" style="background:var(--poor)">Poor (${{val}})</span>`;
      if (val <= 400) return `<span class="pill" style="background:var(--very-poor)">Very Poor (${{val}})</span>`;
      return `<span class="pill" style="background:var(--severe)">Severe (${{val}})</span>`;
    }}

    function switchTab(tabId) {{
      document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));
      document.getElementById('tab-' + tabId).classList.add('active');
      event.currentTarget.classList.add('active');
    }}

    function toggleTheme() {{
      const body = document.body;
      const btn = document.getElementById('themeBtn');
      if (body.getAttribute('data-theme') === 'dark') {{
        body.setAttribute('data-theme', 'light');
        btn.textContent = '🌙 Dark Mode';
      }} else {{
        body.setAttribute('data-theme', 'dark');
        btn.textContent = '☀️ Light Mode';
      }}
    }}

    // Render Tables
    function renderTables() {{
      // Top 10 cities
      const topCitiesBody = document.getElementById('topCitiesTable');
      topCitiesBody.innerHTML = DATA.cities.slice(0, 10).map((c, i) => `
        <tr>
          <td><strong>#${{i+1}}</strong></td>
          <td>${{c.area}}</td>
          <td>${{c.state}}</td>
          <td><strong>${{c.average_aqi.toFixed(1)}}</strong></td>
          <td>${{getAqiBadge(c.average_aqi)}}</td>
        </tr>
      `).join('');

      // Cleanest states
      const cleanStatesBody = document.getElementById('cleanStatesTable');
      const cleanStates = [...DATA.states].reverse().slice(0, 8);
      cleanStatesBody.innerHTML = cleanStates.map((s, i) => `
        <tr>
          <td><strong>#${{i+1}}</strong></td>
          <td>${{s.state}}</td>
          <td><strong>${{s.average_aqi.toFixed(1)}}</strong></td>
          <td>${{s.median_aqi.toFixed(1)}}</td>
          <td>${{s.observations.toLocaleString()}}</td>
        </tr>
      `).join('');

      // All states
      const allStatesBody = document.querySelector('#allStatesTable tbody');
      allStatesBody.innerHTML = DATA.states.map(s => `
        <tr>
          <td><strong>${{s.state}}</strong></td>
          <td>${{s.average_aqi.toFixed(1)}}</td>
          <td>${{s.median_aqi.toFixed(1)}}</td>
          <td>${{s.maximum_aqi}}</td>
          <td>${{s.cities}}</td>
          <td>${{s.observations.toLocaleString()}}</td>
          <td>${{getAqiBadge(s.average_aqi)}}</td>
        </tr>
      `).join('');

      // State Shares
      const sharesBody = document.querySelector('#stateSharesTable tbody');
      sharesBody.innerHTML = DATA.state_shares.slice(0, 15).map(s => {{
        const poorPlus = (s['Poor share'] || 0) + (s['Very Poor share'] || 0) + (s['Severe share'] || 0);
        return `
          <tr>
            <td><strong>${{s.state}}</strong></td>
            <td>${{s['Good share']}}%</td>
            <td>${{s['Satisfactory share']}}%</td>
            <td>${{s['Moderate share']}}%</td>
            <td style="color:var(--very-poor); font-weight:700">${{poorPlus.toFixed(1)}}%</td>
          </tr>
        `;
      }}).join('');
    }}

    function filterStatesTable() {{
      const q = document.getElementById('stateSearch').value.toLowerCase();
      document.querySelectorAll('#allStatesTable tbody tr').forEach(row => {{
        const text = row.cells[0].textContent.toLowerCase();
        row.style.display = text.includes(q) ? '' : 'none';
      }});
    }}

    // Render Charts using Chart.js
    function renderCharts() {{
      if (typeof Chart === 'undefined') return;

      // 1. Monthly Trend
      new Chart(document.getElementById('monthlyTrendChart'), {{
        type: 'line',
        data: {{
          labels: DATA.monthly.map(m => m.month_str),
          datasets: [{{
            label: 'Average AQI',
            data: DATA.monthly.map(m => m.average_aqi),
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.15)',
            borderWidth: 2.5,
            fill: true,
            tension: 0.35,
            pointRadius: 2,
            pointHoverRadius: 6
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{
            y: {{ grid: {{ color: 'rgba(148, 163, 184, 0.1)' }} }},
            x: {{ grid: {{ display: false }} }}
          }}
        }}
      }});

      // 2. Category Donut
      new Chart(document.getElementById('categoryDonutChart'), {{
        type: 'doughnut',
        data: {{
          labels: DATA.categories.map(c => c.category),
          datasets: [{{
            data: DATA.categories.map(c => c.observations),
            backgroundColor: [
              '#10b981', // Good
              '#84cc16', // Satisfactory
              '#eab308', // Moderate
              '#f97316', // Poor
              '#ef4444', // Very Poor
              '#991b1b'  // Severe
            ],
            borderWidth: 0
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ position: 'bottom', labels: {{ color: '#94a3b8', font: {{ size: 11 }} }} }}
          }}
        }}
      }});

      // 3. Top States Bar
      const top10 = DATA.states.slice(0, 10);
      new Chart(document.getElementById('topStatesChart'), {{
        type: 'bar',
        data: {{
          labels: top10.map(s => s.state),
          datasets: [{{
            label: 'Average AQI',
            data: top10.map(s => s.average_aqi),
            backgroundColor: top10.map(s => s.average_aqi >= 200 ? '#ef4444' : (s.average_aqi >= 150 ? '#f97316' : '#eab308')),
            borderRadius: 6
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          plugins: {{ legend: {{ display: false }} }},
          scales: {{
            x: {{ grid: {{ color: 'rgba(148, 163, 184, 0.1)' }} }},
            y: {{ grid: {{ display: false }} }}
          }}
        }}
      }});

      // 4. Pollutants Bar
      const topPollutants = DATA.pollutants.slice(0, 6);
      new Chart(document.getElementById('pollutantsChart'), {{
        type: 'bar',
        data: {{
          labels: topPollutants.map(p => p.pollutant),
          datasets: [{{
            label: '% Share',
            data: topPollutants.map(p => p.share_of_pollutant_mentions_percent),
            backgroundColor: '#0284c7',
            borderRadius: 6
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{
            y: {{ grid: {{ color: 'rgba(148, 163, 184, 0.1)' }} }},
            x: {{ grid: {{ display: false }} }}
          }}
        }}
      }});

      // 5. Seasonal Chart
      new Chart(document.getElementById('seasonChart'), {{
        type: 'bar',
        data: {{
          labels: DATA.seasons.map(s => s.season),
          datasets: [{{
            label: 'Average AQI',
            data: DATA.seasons.map(s => s.average_aqi),
            backgroundColor: ['#ef4444', '#f97316', '#10b981', '#eab308'],
            borderRadius: 8
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{
            y: {{ grid: {{ color: 'rgba(148, 163, 184, 0.1)' }} }}
          }}
        }}
      }});

      // 6. Weekday Chart
      new Chart(document.getElementById('weekdayChart'), {{
        type: 'line',
        data: {{
          labels: DATA.weekdays.map(w => w.weekday),
          datasets: [{{
            label: 'Average AQI',
            data: DATA.weekdays.map(w => w.average_aqi),
            borderColor: '#a855f7',
            backgroundColor: 'rgba(168, 85, 247, 0.15)',
            borderWidth: 2.5,
            fill: true,
            tension: 0.3,
            pointRadius: 4
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{
            y: {{ min: 105, max: 115, grid: {{ color: 'rgba(148, 163, 184, 0.1)' }} }}
          }}
        }}
      }});
    }}

    window.addEventListener('DOMContentLoaded', () => {{
      renderTables();
      renderCharts();
    }});
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated dashboard at: {OUTPUT_HTML} ({len(html_content):,} bytes)")

if __name__ == "__main__":
    build_dashboard()
