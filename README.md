# Air Quality Index (AQI) Data Analysis and Visualization (DAV)

A comprehensive data analytics and visualization project exploring ambient air quality across Indian states and cities using Central Pollution Control Board (CPCB) monitoring records.

---

## 📌 Project Overview

This project implements an end-to-end data pipeline to:
1. **Clean and Standardize** raw monitoring observations across multiple states and monitoring stations.
2. **Analyze Trends** across temporal dimensions (daily, weekly, monthly, seasonal, yearly) and geographical hierarchies (state-level and city-level rankings).
3. **Visualize Findings** using Matplotlib charts, an interactive multi-view Plotly dashboard, and a multi-page Power BI dashboard.

---

## 📊 Key Findings & Insights

- **Geographic Disparities**:
  - **Highest Average AQI**: Delhi (206.42 average across 1,125 observations)
  - **Lowest Average AQI**: Mizoram (47.25 average across 1,000 observations)
  - **Highest City Average ($\ge 30$ observations)**: Byrnihat, Assam (240.00 average)
- **Temporal Patterns**:
  - **Worst Air Quality Month**: December (Winter temperature inversion and post-harvest biomass burning)
  - **Best Air Quality Month**: August (Monsoon precipitation wash-out effect)
- **Air Quality Categories**:
  - *Satisfactory* is the most common classification (37.70% of total observations).
- **Dominant Pollutants**:
  - $\text{PM}_{10}$ (135,806 mentions) and $\text{PM}_{2.5}$ (78,030 mentions) constitute the primary drivers of elevated AQI levels across monitoring stations.

---

## 🗂️ Project Structure

```text
DAV PROJECT/
├── clean_aqi_data.py              # Data cleaning, deduplication & CPCB category alignment
├── analyze_aqi.py                # Exploratory analysis & statistical aggregation
├── visualize_aqi.py              # Matplotlib chart generator & Plotly dashboard builder
├── aqi.xlsx                      # Original raw dataset
├── aqi_cleaned.xlsx              # Formatted cleaned dataset with summary metadata
├── aqi_cleaned.csv               # Cleaned dataset (CSV format for Looker Studio / BI tools)
├── aqi_analytics.xlsx            # 12-sheet statistical and cross-tabulation workbook
├── AQI DASHBOARD 2.pbix          # 3-page Microsoft Power BI interactive dashboard
├── AQI PROJECT GRAPHS.xlsx       # Excel visualization workbook
├── requirements.txt              # Python package dependencies
├── .gitignore                    # Git ignore file for Python/macOS
└── aqi_graphs/                   # Generated charts and dashboards
    ├── aqi_interactive_dashboard.html   # Standalone interactive Plotly dashboard
    ├── aqi_monthly_trend.png
    ├── aqi_state_averages.png
    ├── aqi_city_averages.png
    ├── aqi_category_distribution.png
    ├── aqi_category_pie.png
    ├── aqi_pollutants.png
    ├── aqi_pollutant_pie.png
    ├── aqi_weekday_averages.png
    ├── aqi_year_month_heatmap.png
    ├── aqi_by_station_count.png
    ├── aqi_state_category_mix.png
    └── aqi_value_distribution.png
```

---

## 🚀 Getting Started

### 1. Environment Setup
Clone the repository and create a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Running the Pipeline

- **Step 1: Clean the raw data**
  ```bash
  python clean_aqi_data.py
  ```
- **Step 2: Generate analytical summaries**
  ```bash
  python analyze_aqi.py
  ```
- **Step 3: Generate visual plots and the interactive dashboard**
  ```bash
  python visualize_aqi.py
  ```

---

## 🖥️ Dashboards & Exploration

1. **Interactive HTML Dashboard**:
   - Open `aqi_graphs/aqi_interactive_dashboard.html` directly in any web browser for interactive zooming, panning, and hover tooltips.
2. **Power BI Report (`AQI DASHBOARD 2.pbix`)**:
   - Open in Power BI Desktop (Windows) or upload to [Power BI Service](https://app.powerbi.com) to view:
     - Page 1: National Overview
     - Page 2: Heat Map (India TopoJSON map visual)
     - Page 3: Data Analysis
3. **Google Looker Studio**:
   - Connect `aqi_cleaned.csv` to [Looker Studio](https://lookerstudio.google.com) for cloud-hosted dashboarding.
