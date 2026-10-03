"""
Database Module for IoT-Based Smart EV Charging Slot Management System
Handles SQLite database connection, table initialization, demo data seeding,
and parameterized query operations for slots and charging events.
"""

import os
import sqlite3
from datetime import datetime, timedelta

DB_NAME = "charging.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, DB_NAME)

def get_db_connection():
    """Create and return a database connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialize SQLite tables for charging slots and charging events.
    Automatically seeds realistic demo data on first run without duplicating records.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create charging_slots table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS charging_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_id TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            vehicle_number TEXT,
            vehicle_type TEXT,
            battery_level INTEGER DEFAULT 0,
            charging_power REAL DEFAULT 0.0,
            energy_consumed REAL DEFAULT 0.0,
            charging_start_time TEXT,
            estimated_completion TEXT,
            last_updated TEXT
        )
    """)

    # Create charging_events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS charging_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            slot_id TEXT NOT NULL,
            vehicle_number TEXT,
            battery_level INTEGER,
            charging_power REAL,
            energy_consumed REAL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()

    # Seed demo charging slots if table is empty
    cursor.execute("SELECT COUNT(*) FROM charging_slots")
    count = cursor.fetchone()[0]

    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    if count == 0:
        demo_slots = [
            ("EV01", "CHARGING", "TN09BC4521", "CAR", 74, 11.0, 22.4, (now - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"), (now + timedelta(minutes=25)).strftime("%Y-%m-%d %H:%M:%S"), now_str),
            ("EV02", "COMPLETED", "DL03EF9912", "CAR", 100, 0.0, 38.6, (now - timedelta(hours=2, minutes=10)).strftime("%Y-%m-%d %H:%M:%S"), (now - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"), now_str),
            ("EV03", "CHARGING", "TN58AB1234", "CAR", 67, 7.2, 18.4, (now - timedelta(minutes=60)).strftime("%Y-%m-%d %H:%M:%S"), (now + timedelta(minutes=35)).strftime("%Y-%m-%d %H:%M:%S"), now_str),
            ("EV04", "AVAILABLE", None, None, 0, 0.0, 0.0, None, None, now_str),
            ("EV05", "AVAILABLE", None, None, 0, 0.0, 0.0, None, None, now_str),
            ("EV06", "CHARGING", "KA05MH7721", "SUV", 42, 22.0, 31.8, (now - timedelta(minutes=35)).strftime("%Y-%m-%d %H:%M:%S"), (now + timedelta(minutes=50)).strftime("%Y-%m-%d %H:%M:%S"), now_str),
            ("EV07", "COMPLETED", "MH12XY3490", "2-WHEELER", 100, 0.0, 4.2, (now - timedelta(hours=1, minutes=20)).strftime("%Y-%m-%d %H:%M:%S"), (now - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"), now_str),
            ("EV08", "CHARGING", "KL07CD8810", "CAR", 28, 7.4, 8.5, (now - timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"), (now + timedelta(minutes=75)).strftime("%Y-%m-%d %H:%M:%S"), now_str),
            ("EV09", "FAULT", "WB02LK5532", "CAR", 19, 0.0, 3.1, (now - timedelta(minutes=55)).strftime("%Y-%m-%d %H:%M:%S"), None, now_str),
            ("EV10", "AVAILABLE", None, None, 0, 0.0, 0.0, None, None, now_str)
        ]

        cursor.executemany("""
            INSERT INTO charging_slots 
            (slot_id, status, vehicle_number, vehicle_type, battery_level, charging_power, energy_consumed, charging_start_time, estimated_completion, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_slots)
        conn.commit()

    # Seed demo charging events if events table is empty
    cursor.execute("SELECT COUNT(*) FROM charging_events")
    event_count = cursor.fetchone()[0]

    if event_count == 0:
        demo_events = [
            ("CONNECTED", "EV08", "KL07CD8810", 22, 0.0, 0.0, (now - timedelta(minutes=25)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CHARGING_STARTED", "EV08", "KL07CD8810", 23, 7.4, 0.5, (now - timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CHARGING", "EV08", "KL07CD8810", 28, 7.4, 8.5, (now - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CONNECTED", "EV06", "KA05MH7721", 20, 0.0, 0.0, (now - timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CHARGING_STARTED", "EV06", "KA05MH7721", 22, 22.0, 1.2, (now - timedelta(minutes=35)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CHARGING", "EV06", "KA05MH7721", 42, 22.0, 31.8, (now - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CONNECTED", "EV03", "TN58AB1234", 35, 0.0, 0.0, (now - timedelta(minutes=65)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CHARGING_STARTED", "EV03", "TN58AB1234", 36, 7.2, 0.8, (now - timedelta(minutes=60)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CHARGING", "EV03", "TN58AB1234", 67, 7.2, 18.4, (now - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CHARGING_COMPLETED", "EV07", "MH12XY3490", 100, 0.0, 4.2, (now - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CHARGING_COMPLETED", "EV02", "DL03EF9912", 100, 0.0, 38.6, (now - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")),
            ("FAULT", "EV09", "WB02LK5532", 19, 0.0, 3.1, (now - timedelta(minutes=18)).strftime("%Y-%m-%d %H:%M:%S"))
        ]

        cursor.executemany("""
            INSERT INTO charging_events
            (event_type, slot_id, vehicle_number, battery_level, charging_power, energy_consumed, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, demo_events)
        conn.commit()

    conn.close()

def get_all_slots():
    """Retrieve all 10 slots sorted by slot_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM charging_slots ORDER BY slot_id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_slot_by_id(slot_id):
    """Retrieve single slot record by its identifier (e.g., 'EV03')."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM charging_slots WHERE UPPER(slot_id) = UPPER(?)", (slot_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_slots_by_status(status):
    """Retrieve slots filtered by status (AVAILABLE, CHARGING, COMPLETED, FAULT)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM charging_slots WHERE UPPER(status) = UPPER(?) ORDER BY slot_id ASC", (status,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_charging_stats():
    """Calculate aggregated live dashboard statistics."""
    slots = get_all_slots()
    total_slots = len(slots)
    available = sum(1 for s in slots if s['status'] == 'AVAILABLE')
    charging = sum(1 for s in slots if s['status'] == 'CHARGING')
    completed = sum(1 for s in slots if s['status'] == 'COMPLETED')
    fault = sum(1 for s in slots if s['status'] == 'FAULT')
    total_energy = round(sum(s['energy_consumed'] or 0.0 for s in slots), 2)

    # Average battery of active/connected vehicles
    active_batteries = [s['battery_level'] for s in slots if s['status'] in ('CHARGING', 'COMPLETED', 'FAULT') and s['battery_level'] is not None and s['battery_level'] > 0]
    avg_battery = round(sum(active_batteries) / len(active_batteries), 1) if active_batteries else 0.0

    return {
        "total_slots": total_slots,
        "available": available,
        "charging": charging,
        "completed": completed,
        "fault": fault,
        "energy_used": total_energy,
        "battery_average": avg_battery
    }

def get_recent_events(limit=10):
    """Retrieve recent charging events ordered by timestamp descending."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM charging_events ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_today_events():
    """Retrieve charging events logged today."""
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT * FROM charging_events WHERE timestamp LIKE ? ORDER BY id DESC", (f"{today_str}%",))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def log_event(event_type, slot_id, vehicle_number=None, battery_level=None, charging_power=None, energy_consumed=None, timestamp=None):
    """Insert a new event log into charging_events."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO charging_events 
        (event_type, slot_id, vehicle_number, battery_level, charging_power, energy_consumed, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (event_type, slot_id, vehicle_number, battery_level, charging_power, energy_consumed, timestamp))
    conn.commit()
    conn.close()

def update_slot(slot_id, status=None, vehicle_number=None, vehicle_type=None,
                battery_level=None, charging_power=None, energy_consumed=None,
                charging_start_time=None, estimated_completion=None):
    """
    Update telemetry or status of a charging slot and update last_updated timestamp.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Fetch current values
    existing = get_slot_by_id(slot_id)
    if not existing:
        conn.close()
        return False

    new_status = status if status is not None else existing['status']
    new_v_num = vehicle_number if vehicle_number is not None else existing['vehicle_number']
    new_v_type = vehicle_type if vehicle_type is not None else existing['vehicle_type']
    new_battery = battery_level if battery_level is not None else existing['battery_level']
    new_power = charging_power if charging_power is not None else existing['charging_power']
    new_energy = energy_consumed if energy_consumed is not None else existing['energy_consumed']
    new_start = charging_start_time if charging_start_time is not None else existing['charging_start_time']
    new_est = estimated_completion if estimated_completion is not None else existing['estimated_completion']

    # If status transitioned to AVAILABLE, clear active vehicle details
    if new_status == 'AVAILABLE':
        new_v_num = None
        new_v_type = None
        new_battery = 0
        new_power = 0.0
        new_energy = 0.0
        new_start = None
        new_est = None

    cursor.execute("""
        UPDATE charging_slots 
        SET status = ?, vehicle_number = ?, vehicle_type = ?,
            battery_level = ?, charging_power = ?, energy_consumed = ?,
            charging_start_time = ?, estimated_completion = ?, last_updated = ?
        WHERE UPPER(slot_id) = UPPER(?)
    """, (new_status, new_v_num, new_v_type, new_battery, new_power, new_energy, new_start, new_est, now_str, slot_id))
    
    conn.commit()
    conn.close()
    return True
