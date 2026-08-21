# Telemetry Sentinel Engine

An automated, high-frequency telemetry ingestion and anomaly detection pipeline designed to simulate spacecraft and ground station sensor feeds, parse data frames, and flag operational anomalies in real time.

## Tech Stack
* **Language:** Python 3.10+
* **Data Processing:** Pandas, NumPy, SQLAlchemy
* **Analysis:** Rolling-window Z-score statistical anomaly detection
* **Visualization:** Streamlit / Flask

## Key Features
* **Live Telemetry Generation:** Multi-threaded packet simulation injecting high-voltage drops, thermal spikes, and signal degradations.
* **Resilient Parsing Pipeline:** Automated filtering and validation framework to clean incoming data streams.
* **Audit-Ready Logging:** Detailed error tracking and status reporting for operational observability.
