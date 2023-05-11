from flask import Flask, request, jsonify, g
from flask_httpauth import HTTPTokenAuth
import psycopg2
from psycopg2.extras import execute_values
import json
import os
from flask import render_template
import random
from datetime import datetime, timedelta

app = Flask(__name__)

DATABASE_CONFIG = {
    'dbname': os.environ['DB_NAME'],
    'user': os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD'],
    'host': os.environ['DB_HOST'],
    'port': os.environ['DB_PORT']
}

TOKENS = {
    "vYTKxJNCLEh7XsrZOhHHLEUE9MpkzFRxJQvcUXGvip4": "usermame"
}

auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    if token in TOKENS:
        g.current_user = TOKENS[token]
        return True
    return False

def connect_db():
    return psycopg2.connect(**DATABASE_CONFIG)

@app.route('/add_data', methods=['POST'])
@auth.login_required
def add_data():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    timestamp = data.get('timestamp')
    client_id = data.get('client_id')
    hardware_id = data.get('hardware_id')
    sensor_data = json.dumps(data.get('data'))

    if not (timestamp and client_id and hardware_id and sensor_data):
        return jsonify({"error": "Missing data"}), 400

    conn = connect_db()
    cur = conn.cursor()

    query = """
    INSERT INTO sensor_data (timestamp, client_id, hardware_id, data)
    VALUES (%s, %s, %s, %s)
    """
    cur.execute(query, (timestamp, client_id, hardware_id, sensor_data))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"success": "Data added"}), 201

@app.route('/get_data', methods=['GET'])
@auth.login_required
def get_data():
    client_id = request.args.get('client_id')
    hardware_id = request.args.get('hardware_id')

    if not (client_id and hardware_id):
        return jsonify({"error": "Missing parameters"}), 400

    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT timestamp, data
    FROM sensor_data
    WHERE client_id = %s AND hardware_id = %s
    ORDER BY timestamp DESC
    """
    cur.execute(query, (client_id, hardware_id))
    results = cur.fetchall()

    cur.close()
    conn.close()

    response_data = [
    {"timestamp": str(row[0]), "data": row[1]} for row in results
    ]

    return jsonify(response_data)

@app.route('/', methods=['GET'])
def index():
    conn = connect_db()
    cur = conn.cursor()

    # Query to get the total number of records
    count_query = "SELECT COUNT(*) FROM sensor_data;"
    cur.execute(count_query)
    total_records = cur.fetchone()[0]

    # Query to get the latest record's timestamp
    latest_query = "SELECT timestamp FROM sensor_data ORDER BY timestamp DESC LIMIT 1;"
    cur.execute(latest_query)
    latest_timestamp = cur.fetchone()
    if latest_timestamp:
        latest_timestamp = str(latest_timestamp[0])
    else:
        latest_timestamp = "No data available"

    cur.close()
    conn.close()

    # Create a response with database statistics
    response_data = {
        "total_records": total_records,
        "latest_timestamp": latest_timestamp
    }
    return render_template("index.html", total_records=total_records, latest_timestamp=latest_timestamp)

def init_db():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id SERIAL NOT NULL,
                client_id VARCHAR(255) NOT NULL,
                hardware_id VARCHAR(255) NOT NULL,
                data JSONB NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                PRIMARY KEY (id, timestamp)
            );
            """)
            cur.execute("""
            SELECT create_hypertable('sensor_data', 'timestamp', if_not_exists => true, create_default_indexes => false);
            """)
        conn.commit()


@app.route('/add_sample_data', methods=['GET'])
def add_sample_data():
    client_id = f"client_{random.randint(1, 100)}"
    hardware_id = f"hardware_{random.randint(1, 100)}"
    data = {
        "temperature": random.uniform(20, 30),
        "humidity": random.uniform(40, 60),
    }
    timestamp = datetime.utcnow() - timedelta(minutes=random.randint(0, 1440))

    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sensor_data (client_id, hardware_id, data, timestamp)
                VALUES (%s, %s, %s, %s);
                """, (client_id, hardware_id, json.dumps(data), timestamp))
        conn.commit()

    return jsonify({"message": "Sample data added successfully"}), 200


if __name__ == '__main__':
    print("Hello world!")
    init_db()
    app.run(debug=True, host='0.0.0.0')
