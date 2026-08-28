CREATE TABLE IF NOT EXISTS telemetry_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    satellite_id VARCHAR(50) NOT NULL,
    bus_voltage FLOAT NOT NULL,
    internal_temp FLOAT NOT NULL,
    snr FLOAT NOT NULL,
    is_anomaly BOOLEAN DEFAULT FALSE,
    z_score FLOAT DEFAULT 0.0
);

CREATE INDEX idx_telemetry_timestamp ON telemetry_events(timestamp DESC);
