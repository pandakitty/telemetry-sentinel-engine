"""
Module: Telemetry Simulator
Author: Ashley Love
Purpose: Generates simulated high-frequency spacecraft/ground station telemetry 
         packets, injecting deliberate anomaly spikes to test downstream anomaly 
         detection pipelines and alerting thresholds.
Stakeholder Note: Designed for robust system testing and pipeline resilience validation.
"""

import time
import random
import json
from datetime import datetime

class TelemetrySimulator:
    def __init__(self, sat_id="SAT_MILSATCOM_01"):
        self.sat_id = sat_id
        # Baseline normal operational parameters
        self.base_voltage = 28.5  # Volts
        self.base_temp = 42.0     # Celsius
        self.base_snr = 15.2      # dB (Signal-to-Noise Ratio)
        self.seq = 1000

    def generate_packet(self, inject_anomaly=False):
        """
        Generates a single telemetry data frame dictionary.
        If inject_anomaly is True, introduces out-of-bounds voltage drop or temperature spike.
        """
        self.seq += 1
        
        # Default jitter
        voltage = round(self.base_voltage + random.uniform(-0.3, 0.3), 2)
        temp = round(self.base_temp + random.uniform(-0.5, 0.5), 2)
        snr = round(self.base_snr + random.uniform(-0.8, 0.8), 2)
        packet_loss = 0.01  # 1% baseline packet loss
        
        # Professional Engineering Logic: Inject anomalies for stress-testing filters
        if inject_anomaly:
            anomaly_type = random.choice(["voltage_drop", "thermal_spike", "signal_degradation"])
            if anomaly_type == "voltage_drop":
                voltage = round(random.uniform(22.0, 24.5), 2) # Critical low voltage
            elif anomaly_type == "thermal_spike":
                temp = round(random.uniform(65.0, 85.0), 2)     # Overheating alert range
            elif anomaly_type == "signal_degradation":
                snr = round(random.uniform(1.0, 4.0), 2)       # High packet drop risk
                packet_loss = round(random.uniform(0.15, 0.45), 2)

        packet = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "satellite_id": self.sat_id,
            "sequence_number": self.seq,
            "metrics": {
                "bus_voltage_v": voltage,
                "internal_temp_c": temp,
                "signal_to_noise_db": snr,
                "packet_loss_rate": packet_loss
            },
            "status": "ALERT" if inject_anomaly else "NOMINAL"
        }
        return packet

    def stream_telemetry(self, total_packets=50, interval=0.5, anomaly_probability=0.15):
        """
        Simulates a continuous streaming telemetry feed with configurable frequency 
        and random anomaly injection rates.
        """
        print(f"Initializing telemetry stream for {self.sat_id}...")
        stream_log = []
        
        for _ in range(total_packets):
            # Determine if this transmission cycle contains an anomaly
            is_anomaly = random.random() < anomaly_probability
            packet = self.generate_packet(inject_anomaly=is_anomaly)
            
            stream_log.append(packet)
            print(json.dumps(packet))
            
            # Simulate transmission delay between ground station passes
            time.sleep(interval)
            
        return stream_log

if __name__ == "__main__":
    # Execute a quick test stream
    simulator = TelemetrySimulator()
    simulator.stream_telemetry(total_packets=10, interval=0.2)
