# NIFTY Market Mood Indicator 📈

An automated, data-driven pipeline designed to calculate a daily **Market Mood Score (0-100)** for the NIFTY 50 index. 

This project synthesizes institutional cash flows and key technical indicators to provide actionable quantitative insights. It features a rule-based evaluation engine and outputs clean, structured data ready for integration with business intelligence tools like Power BI and Google Sheets.

## 🚀 Key Features

* **Data Ingestion:** Automated extraction of OHLCV data for NIFTY & BANKNIFTY via `yfinance`, combined with FII/DII net cash flow data.
* **Quantitative Analysis:** Computes critical technical indicators including **RSI(14)**, **Anchored VWAP** (Monthly & Weekly), and **20-Day Volume Z-Scores**.
* **Statistical Tracking:** Monitors the 20-day rolling correlation between NIFTY and BANKNIFTY to gauge broader market participation.
* **Algorithmic Scoring Engine:** Utilizes a customizable, rule-based alerts system to generate a weighted daily market mood score.
* **BI Integration:** Exports processed metrics to a streamlined CSV format (`out/daily_dashboard.csv`) optimized for seamless dashboard visualization.

## 🛠️ Technical Stack
* **Language:** Python
* **Libraries:** `yfinance`, `pandas`, `numpy`
* **Configuration:** YAML (Rule Engine)
* **Visualization:** Power BI / Google Sheets

## 📂 Project Structure

```text
├── data/
│   └── fii_dii_sample.csv       # Institutional net flows (INR crore)
├── src/
│   ├── etl.py                   # Data extraction, transformation, and merging
│   ├── indicators.py            # Logic for RSI, VWAP, rolling stats, and correlations
│   ├── alerts.py                # Rule engine for boolean triggers and score weighting
│   └── mood_score.py            # Main pipeline entry point
├── docs/
│   └── method_note.md           # Documentation on scoring methodology and logic
├── dashboards/
│   └── powerbi_model_spec.md    # Schema and relationships for BI integration
├── rules.yaml                   # Configurable thresholds and weights for the mood score
└── requirements.txt             # Project dependencies
