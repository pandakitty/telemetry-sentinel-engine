# Telemetry Sentinel Engine

An automated, high-frequency telemetry ingestion and anomaly detection pipeline designed to simulate spacecraft and ground station sensor feeds, parse data frames, and flag operational anomalies in real time. Built with an interactive Streamlit mission control dashboard for rapid data auditing and systems observability.

## 🚀 Live System Architecture
* **Telemetry Simulator (`telemetry_simulator.py`):** Multi-threaded packet generation engine simulating live spacecraft sensor streams (bus voltage, internal temperature, signal-to-noise ratio, and packet loss) with controlled stochastic anomaly injection.
* **Parsing & Z-Score Pipeline (`parser_pipeline.py`):** Structured Pandas transformation layer applying rolling-window Z-score statistical analysis to isolate operational faults independently of hardcoded static bounds.
* **Mission Control Dashboard (`observability_dashboard.py`):** Interactive web interface providing real-time metric tracking, operational health KPIs, dynamic stream controls, and automated anomaly logs.

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Data Processing & Analysis:** Pandas, NumPy
* **Interface & Visualization:** Streamlit, native web line charts

## 📦 Quickstart & Local Execution
1. Clone the repository and install dependencies:
   ```bash
   pip install pandas numpy streamlit
