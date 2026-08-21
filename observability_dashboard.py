"""
Module: System Health & Metric Observability Dashboard
Author: Ashley Love
Purpose: Provides a real-time administrative interface and operational dashboard 
         to monitor simulated spacecraft telemetry feeds, tracking system health scores,
         active voltage/thermal anomalies, and packet loss trends.
Stakeholder Note: Built for mission control observability and fast-response data auditing.
"""

import streamlit as st
import pandas as pd
import numpy as np
import time

# Import your existing pipeline modules
from telemetry_simulator import TelemetrySimulator
from parser_pipeline import TelemetryParserPipeline

# Page Configuration
st.set_page_config(
    page_title="Telemetry Sentinel | Mission Control",
    page_icon="🛰️",
    layout="wide"
)

# Header Section
st.title("🛰️ Telemetry Sentinel: Mission Control Dashboard")
st.markdown("**System Observability & Automated Anomaly Detection Panel** | *Engineered for Real-Time Satellite Monitoring*")
st.markdown("---")

# Sidebar Controls for Operators
st.sidebar.header("Simulation Parameters")
sat_id = st.sidebar.selectbox("Select Target Satellite", ["SAT_MILSATCOM_01", "SAT_MILSATCOM_02", "SAT_RECON_09"])
packet_count = st.sidebar.slider("Stream Packet Batch Size", min_value=10, max_value=100, value=30, step=10)
anomaly_prob = st.sidebar.slider("Anomaly Injection Probability", min_value=0.0, max_value=0.5, value=0.15, step=0.05)

# Initialize Session Data or Trigger Stream
if st.sidebar.button("Run Telemetry Pass & Audit", type="primary"):
    with st.spinner(f"Ingesting live telemetry stream for {sat_id}..."):
        # 1. Run Simulator
        sim = TelemetrySimulator(sat_id=sat_id)
        raw_logs = sim.stream_telemetry(total_packets=packet_count, interval=0.01, anomaly_probability=anomaly_prob)
        
        # 2. Run Parser Pipeline
        pipeline = TelemetryParserPipeline(raw_logs)
        df = pipeline.ingest_and_transform()
        df = pipeline.detect_statistical_anomalies(window_size=3, threshold=2.0)
        summary = pipeline.generate_audit_summary()
        
        # Save to Streamlit session state so it persists on screen
        st.session_state["telemetry_df"] = df
        st.session_state["audit_summary"] = summary
        st.success("Telemetry ingestion and Z-score anomaly audit complete!")

# Main Dashboard View (If data exists)
if "telemetry_df" in st.session_state and not st.session_state["telemetry_df"].empty:
    df = st.session_state["telemetry_df"]
    summary = st.session_state["audit_summary"]

    # Top-Level KPI Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Frames Processed", summary["total_frames_processed"])
    with col2:
        st.metric("Anomalies Flagged", summary["anomalies_flagged"], delta_color="inverse")
    with col3:
        st.metric("System Health Score", f"{summary['system_health_score_pct']}%")
    with col4:
        operational_status = "NOMINAL" if summary["anomalies_flagged"] == 0 else "WARNING"
        st.metric("Operational Status", operational_status)

    st.markdown("---")

    # Visualizations: Real-time Telemetry Trends
    st.subheader("📊 High-Frequency Telemetry Sensor Streams")
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("**Bus Voltage Stability (V)**")
        st.line_chart(df, x="timestamp", y="bus_voltage_v")
        
    with col_chart2:
        st.markdown("**Internal Thermal Profile (°C)**")
        st.line_chart(df, x="timestamp", y="internal_temp_c")

    # Detailed Anomaly Log Table
    st.subheader("🚨 System Audit & Anomaly Log")
    anomalies_only = df[df["system_flagged_anomaly"] == True]
    
    if not anomalies_only.empty:
        st.warning(f"Attention: {len(anomalies_only)} frames triggered automated statistical alert thresholds.")
        st.dataframe(anomalies_only[["timestamp", "sequence_number", "bus_voltage_v", "internal_temp_c", "signal_to_noise_db", "reported_status"]], use_container_width=True)
    else:
        st.success("All data frames are operating entirely within nominal historical boundaries.")

else:
    st.info("👈 Use the sidebar controls and click **Run Telemetry Pass & Audit** to initialize the live dashboard feed.")
