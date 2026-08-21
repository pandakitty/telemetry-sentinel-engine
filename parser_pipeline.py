"""
Module: Telemetry Parser & Anomaly Detection Pipeline
Author: Ashley Love
Purpose: Ingests raw telemetry logs, structures data frames via Pandas, and applies 
         rolling Z-score statistical analysis to isolate operational anomalies 
         and secure system reliability.
Stakeholder Note: Engineered for automated data quality checking and anomaly isolation.
"""

import pandas as pd
import numpy as np
from datetime import datetime

class TelemetryParserPipeline:
    def __init__(self, raw_telemetry_logs):
        """
        Initializes the pipeline with raw JSON-style telemetry packet lists.
        """
        self.raw_data = raw_telemetry_logs
        self.df = pd.DataFrame()

    def ingest_and_transform(self):
        """
        Flattens nested JSON telemetry dictionaries into a structured Pandas DataFrame
        for high-performance data processing.
        """
        if not self.raw_data:
            print("Warning: No telemetry data provided to ingest.")
            return self.df

        flattened_rows = []
        for packet in self.raw_data:
            row = {
                "timestamp": packet.get("timestamp"),
                "satellite_id": packet.get("satellite_id"),
                "sequence_number": packet.get("sequence_number"),
                "bus_voltage_v": packet["metrics"].get("bus_voltage_v"),
                "internal_temp_c": packet["metrics"].get("internal_temp_c"),
                "signal_to_noise_db": packet["metrics"].get("signal_to_noise_db"),
                "packet_loss_rate": packet["metrics"].get("packet_loss_rate"),
                "reported_status": packet.get("status")
            }
            flattened_rows.append(row)

        self.df = pd.DataFrame(flattened_rows)
        # Convert timestamp to standard datetime format
        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
        print(f"Successfully structured {len(self.df)} telemetry frames into DataFrame.")
        return self.df

    def detect_statistical_anomalies(self, window_size=3, threshold=2.0):
        """
        Applies a rolling Z-score algorithm across voltage and temperature metrics 
        to flag statistically significant anomalies independent of static hardcoded thresholds.
        """
        if self.df.empty:
            print("DataFrame is empty. Run ingest_and_transform() first.")
            return self.df

        analysis_columns = ["bus_voltage_v", "internal_temp_c", "signal_to_noise_db"]
        
        for col in analysis_columns:
            # Calculate rolling mean and rolling standard deviation
            rolling_mean = self.df[col].rolling(window=window_size, min_periods=1).mean()
            rolling_std = self.df[col].rolling(window=window_size, min_periods=1).std().fillna(1.0)
            
            # Prevent division by zero if std is 0
            rolling_std = rolling_std.replace(0, 1.0)

            # Compute Z-Score
            z_score_col = f"{col}_zscore"
            self.df[z_score_col] = (self.df[col] - rolling_mean) / rolling_std

            # Flag rows where absolute Z-score exceeds our sensitivity threshold
            flag_col = f"{col}_anomaly_flag"
            self.df[flag_col] = abs(self.df[z_score_col]) > threshold

        # Create a consolidated system alert flag
        flag_columns = [f"{col}_anomaly_flag" for col in analysis_columns]
        self.df["system_flagged_anomaly"] = self.df[flag_columns].any(axis=1)

        anomalies_detected = self.df["system_flagged_anomaly"].sum()
        print(f"Anomaly Detection Complete: Flagged {anomalies_detected} anomalous data frames.")
        return self.df

    def generate_audit_summary(self):
        """
        Outputs a clean summary report of operational status for stakeholders.
        """
        if self.df.empty:
            return "No data available for audit summary."

        total_frames = len(self.df)
        total_anomalies = self.df["system_flagged_anomaly"].sum()
        health_percentage = round(((total_frames - total_anomalies) / total_frames) * 100, 2)

        summary = {
            "total_frames_processed": total_frames,
            "anomalies_flagged": int(total_anomalies),
            "system_health_score_pct": health_percentage,
            "audit_timestamp": datetime.utcnow().isoformat() + "Z"
        }
        return summary

if __name__ == "__main__":
    # Test integration with the simulator module
    from telemetry_simulator import TelemetrySimulator
    
    sim = TelemetrySimulator()
    sample_logs = sim.stream_telemetry(total_packets=15, interval=0.05, anomaly_probability=0.2)
    
    pipeline = TelemetryParserPipeline(sample_logs)
    pipeline.ingest_and_transform()
    analyzed_df = pipeline.detect_statistical_anomalies()
    print("\nAudit Summary Report:")
    print(pipeline.generate_audit_summary())
