import os
import json
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from kafka import KafkaConsumer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://admin:password123@localhost:5432/telemetry_db")

consumer = KafkaConsumer(
    'spacecraft-telemetry',
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest'
)

conn = psycopg2.connect(POSTGRES_URI)
cursor = conn.cursor()
buffer = []

def process_and_sink(batch):
    df = pd.DataFrame(batch)
    # Calculate rolling Z-score for temperature anomalies
    df['mean'] = df['internal_temp'].rolling(window=10, min_periods=1).mean()
    df['std'] = df['internal_temp'].rolling(window=10, min_periods=1).std().fillna(1.0)
    df['z_score'] = (df['internal_temp'] - df['mean']) / df['std']
    df['is_anomaly'] = df['z_score'].abs() > 2.5

    records = [
        (
            row['timestamp'], row['satellite_id'], row['bus_voltage'],
            row['internal_temp'], row['snr'], bool(row['is_anomaly']), float(row['z_score'])
        )
        for _, row in df.iterrows()
    ]

    insert_query = """
        INSERT INTO telemetry_events 
        (timestamp, satellite_id, bus_voltage, internal_temp, snr, is_anomaly, z_score)
        VALUES %s
    """
    execute_values(cursor, insert_query, records)
    conn.commit()

print("Kafka consumer active. Ingesting stream...")
for msg in consumer:
    buffer.append(msg.value)
    if len(buffer) >= 20:  # Micro-batching for high performance
        process_and_sink(buffer)
        buffer.clear()
