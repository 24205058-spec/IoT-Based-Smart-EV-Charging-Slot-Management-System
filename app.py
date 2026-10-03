"""
IoT-Based Smart EV Charging Slot Management System
Backend Application (Flask, SQLite, Pandas, OpenPyXL, Plotly)
Academic IoT Demonstration - Simulation Mode
"""

import os
import re
from datetime import datetime
import pandas as pd
from flask import Flask, render_template, request, jsonify

import database

# Initialize Flask Application
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'EV_Charging_Dataset.xlsx')

# Ensure database is initialized when starting
with app.app_context():
    database.init_db()

# ============================================================================
# WEB PAGES
# ============================================================================

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Render the primary single-page EV charging dashboard."""
    return render_template('dashboard.html')

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/charging-status', methods=['GET'])
def get_charging_status():
    """
    Return all 10 slots and aggregated statistics for real-time polling.
    Used by dashboard frontend to dynamically refresh live status without page reload.
    """
    try:
        stats = database.get_charging_stats()
        slots = database.get_all_slots()
        return jsonify({
            "status": "success",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stats": stats,
            "slots": slots
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/recent-events', methods=['GET'])
def get_recent_events():
    """Return the most recent charging events from SQLite."""
    try:
        limit = request.args.get('limit', default=10, type=int)
        events = database.get_recent_events(limit=limit)
        return jsonify({
            "status": "success",
            "count": len(events),
            "events": events
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/slot/<slot_id>', methods=['GET'])
def get_slot_detail(slot_id):
    """Retrieve detailed state of a specific charging slot."""
    try:
        slot = database.get_slot_by_id(slot_id)
        if not slot:
            return jsonify({
                "status": "error",
                "message": f"Slot '{slot_id}' not found. Valid slots are EV01 to EV10."
            }), 404
        return jsonify({
            "status": "success",
            "slot": slot
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/query', methods=['POST'])
def handle_query():
    """
    Process natural language queries submitted from the dashboard search box.
    Queries SQLite dynamically and returns structured results.
    """
    try:
        data = request.get_json(silent=True) or {}
        query = data.get('query', '').strip()

        if not query:
            return jsonify({
                "status": "warning",
                "message": "Please enter a search query.",
                "data": None
            }), 400

        result = process_search_query(query)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Search processing error: {str(e)}",
            "data": None
        }), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """
    Historical charging analytics read from EV_Charging_Dataset.xlsx using Pandas.
    Provides calculated KPI metrics and Plotly-ready series.
    """
    try:
        if not os.path.exists(DATA_FILE):
            return jsonify({
                "status": "error",
                "message": f"Dataset file not found at {DATA_FILE}"
            }), 404

        df = pd.read_excel(DATA_FILE, engine='openpyxl')

        # Calculate KPIs
        total_records = int(len(df))
        completed_sessions = int((df['Status'] == 'COMPLETED').sum())
        avg_duration = round(float(df['Charging_Duration_Min'].mean()), 1)
        total_energy = round(float(df['Energy_Consumed_kWh'].sum()), 2)
        avg_energy = round(float(df['Energy_Consumed_kWh'].mean()), 2)

        car_count = int((df['Vehicle_Type'] == 'CAR').sum())
        two_wheeler_count = int((df['Vehicle_Type'] == '2-WHEELER').sum())
        suv_count = int((df['Vehicle_Type'] == 'SUV').sum())

        most_used_slot = str(df['Slot_ID'].value_counts().index[0])
        most_used_slot_count = int(df['Slot_ID'].value_counts().iloc[0])

        # 1. Daily Charging Sessions
        daily_counts = df.groupby('Date').size().reset_index(name='Sessions')
        daily_counts = daily_counts.sort_values('Date')
        daily_sessions = {
            "x": daily_counts['Date'].astype(str).tolist(),
            "y": daily_counts['Sessions'].tolist()
        }

        # 2. Daily Energy Consumption
        daily_energy_df = df.groupby('Date')['Energy_Consumed_kWh'].sum().reset_index()
        daily_energy_df = daily_energy_df.sort_values('Date')
        daily_energy = {
            "x": daily_energy_df['Date'].astype(str).tolist(),
            "y": [round(val, 2) for val in daily_energy_df['Energy_Consumed_kWh'].tolist()]
        }

        # 3. Vehicle Type Distribution
        v_dist = df['Vehicle_Type'].value_counts().reset_index()
        v_dist.columns = ['Vehicle_Type', 'Count']
        vehicle_distribution = {
            "labels": v_dist['Vehicle_Type'].tolist(),
            "values": v_dist['Count'].tolist()
        }

        # 4. Charging Slot Utilization
        slot_counts = df['Slot_ID'].value_counts().sort_index().reset_index()
        slot_counts.columns = ['Slot_ID', 'Count']
        slot_utilization = {
            "x": slot_counts['Slot_ID'].tolist(),
            "y": slot_counts['Count'].tolist()
        }

        # 5. Battery Level Distribution (Start vs End)
        battery_distribution = {
            "start": df['Battery_Start'].tolist(),
            "end": df['Battery_End'].tolist()
        }

        # 6. Charging Duration Distribution
        duration_distribution = {
            "durations": df['Charging_Duration_Min'].tolist()
        }

        return jsonify({
            "status": "success",
            "summary": {
                "total_records": total_records,
                "total_sessions": total_records,
                "completed_sessions": completed_sessions,
                "average_duration_min": avg_duration,
                "total_energy_kwh": total_energy,
                "average_energy_kwh": avg_energy,
                "car_count": car_count,
                "two_wheeler_count": two_wheeler_count,
                "suv_count": suv_count,
                "most_used_slot": most_used_slot,
                "most_used_slot_count": most_used_slot_count
            },
            "charts": {
                "daily_sessions": daily_sessions,
                "daily_energy": daily_energy,
                "vehicle_distribution": vehicle_distribution,
                "slot_utilization": slot_utilization,
                "battery_distribution": battery_distribution,
                "duration_distribution": duration_distribution
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Analytics error: {str(e)}"}), 500

# ============================================================================
# NODE-RED / IOT SIMULATION INGESTION ENDPOINTS
# ============================================================================

@app.route('/api/node-red/event', methods=['POST'])
def node_red_event():
    """
    Receive simulated IoT event messages from Node-RED.
    Logs event into charging_events and updates slot if needed.
    """
    try:
        payload = request.get_json(silent=True)
        if not payload:
            return jsonify({"status": "error", "message": "Malformed or empty JSON payload"}), 400

        event_type = payload.get('event_type')
        slot_id = payload.get('slot_id')

        if not event_type or not slot_id:
            return jsonify({"status": "error", "message": "Missing required fields: event_type and slot_id"}), 400

        # Validate slot ID format (EV01 - EV10)
        slot_id = slot_id.upper()
        if not re.match(r"^EV(0[1-9]|10)$", slot_id):
            return jsonify({"status": "error", "message": f"Invalid slot_id '{slot_id}'. Must be EV01 to EV10."}), 400

        vehicle_number = payload.get('vehicle_number')
        battery_level = payload.get('battery_level')
        charging_power = payload.get('charging_power')
        energy_consumed = payload.get('energy_consumed')
        timestamp = payload.get('timestamp') or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Map event type to slot status update
        status_map = {
            'CONNECTED': 'CHARGING',
            'CHARGING_STARTED': 'CHARGING',
            'CHARGING': 'CHARGING',
            'CHARGING_COMPLETED': 'COMPLETED',
            'DISCONNECTED': 'AVAILABLE',
            'FAULT': 'FAULT'
        }

        target_status = status_map.get(event_type)
        if target_status:
            database.update_slot(
                slot_id=slot_id,
                status=target_status,
                vehicle_number=vehicle_number,
                vehicle_type=payload.get('vehicle_type'),
                battery_level=battery_level,
                charging_power=charging_power,
                energy_consumed=energy_consumed
            )

        # Log event in charging_events
        database.log_event(
            event_type=event_type,
            slot_id=slot_id,
            vehicle_number=vehicle_number,
            battery_level=battery_level,
            charging_power=charging_power,
            energy_consumed=energy_consumed,
            timestamp=timestamp
        )

        return jsonify({
            "status": "success",
            "message": f"Event '{event_type}' for {slot_id} processed successfully",
            "slot_id": slot_id
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to ingest event: {str(e)}"}), 500

@app.route('/api/node-red/update', methods=['POST'])
def node_red_update():
    """
    Receive continuous simulated sensor telemetry from Node-RED.
    Updates SQLite charging_slots record and logs progress.
    """
    try:
        payload = request.get_json(silent=True)
        if not payload:
            return jsonify({"status": "error", "message": "Malformed or empty JSON payload"}), 400

        slot_id = payload.get('slot_id')
        if not slot_id:
            return jsonify({"status": "error", "message": "Missing slot_id"}), 400

        slot_id = slot_id.upper()
        if not re.match(r"^EV(0[1-9]|10)$", slot_id):
            return jsonify({"status": "error", "message": f"Invalid slot_id '{slot_id}'. Must be EV01 to EV10."}), 400

        existing = database.get_slot_by_id(slot_id)
        if not existing:
            return jsonify({"status": "error", "message": f"Slot {slot_id} not found"}), 404

        status = payload.get('status', existing['status'])
        vehicle_number = payload.get('vehicle_number', existing['vehicle_number'])
        vehicle_type = payload.get('vehicle_type', existing['vehicle_type'])
        battery_level = payload.get('battery_level', existing['battery_level'])
        charging_power = payload.get('charging_power', existing['charging_power'])
        energy_consumed = payload.get('energy_consumed', existing['energy_consumed'])
        start_time = payload.get('charging_start_time', existing['charging_start_time'])
        est_completion = payload.get('estimated_completion', existing['estimated_completion'])

        database.update_slot(
            slot_id=slot_id,
            status=status,
            vehicle_number=vehicle_number,
            vehicle_type=vehicle_type,
            battery_level=battery_level,
            charging_power=charging_power,
            energy_consumed=energy_consumed,
            charging_start_time=start_time,
            estimated_completion=est_completion
        )

        # Log charging telemetry event if charging or completed
        if status in ['CHARGING', 'COMPLETED', 'FAULT']:
            database.log_event(
                event_type=status,
                slot_id=slot_id,
                vehicle_number=vehicle_number,
                battery_level=battery_level,
                charging_power=charging_power,
                energy_consumed=energy_consumed
            )

        updated_slot = database.get_slot_by_id(slot_id)
        return jsonify({
            "status": "success",
            "message": f"Slot {slot_id} updated successfully",
            "slot": updated_slot
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to update slot: {str(e)}"}), 500

# ============================================================================
# SEARCH ENGINE LOGIC
# ============================================================================

def process_search_query(raw_query):
    """
    Parse natural language query and query SQLite.
    Returns structured results for:
    - available charging slots
    - how many chargers are available
    - how many EVs are currently charging
    - status of EV03 (or any EV01-EV10)
    - show charging vehicles
    - show completed charging
    - show today's charging sessions
    - show EVs below 30% battery
    - show highest energy consumption
    - show faulty chargers
    """
    q = raw_query.strip().lower()

    # 1. "status of EVxx" or mentions specific slot like "EV03"
    slot_match = re.search(r'\b(ev\s*0?[1-9]|ev\s*10)\b', q, re.IGNORECASE)
    if slot_match and any(k in q for k in ['status', 'details', 'info', 'show', 'check', 'what is', 'is']) or (slot_match and len(q.split()) <= 3):
        raw_num = re.sub(r'[^0-9]', '', slot_match.group(1))
        slot_id = f"EV{int(raw_num):02d}"
        slot = database.get_slot_by_id(slot_id)
        if slot:
            return {
                "status": "success",
                "type": "slot_detail",
                "title": f"Status of {slot_id}",
                "message": f"Status: {slot['status']} | Battery: {slot['battery_level']}% | Power: {slot['charging_power']} kW | Energy: {slot['energy_consumed']} kWh",
                "data": slot
            }
        else:
            return {
                "status": "warning",
                "type": "not_found",
                "message": f"Slot {slot_id} was not found in the database.",
                "data": None
            }

    # 2. "how many chargers are available" / count available
    if ("how many" in q or "count" in q or "number of" in q) and ("available" in q or "free" in q or "vacant" in q):
        slots = database.get_slots_by_status('AVAILABLE')
        count = len(slots)
        slot_names = ", ".join([s['slot_id'] for s in slots]) if slots else "None"
        return {
            "status": "success",
            "type": "count",
            "title": "Available Chargers Count",
            "message": f"There are currently {count} available charging slot(s): {slot_names}.",
            "count": count,
            "data": slots
        }

    # 3. "how many EVs are currently charging" / count charging
    if ("how many" in q or "count" in q or "number of" in q) and ("charging" in q or "in use" in q or "occupied" in q):
        slots = database.get_slots_by_status('CHARGING')
        count = len(slots)
        slot_names = ", ".join([s['slot_id'] for s in slots]) if slots else "None"
        return {
            "status": "success",
            "type": "count",
            "title": "Currently Charging Count",
            "message": f"There are currently {count} EV(s) actively charging: {slot_names}.",
            "count": count,
            "data": slots
        }

    # 4. "show today's charging sessions" / today's events
    if "today" in q or "day's" in q:
        events = database.get_today_events()
        return {
            "status": "success",
            "type": "event_list",
            "title": "Today's Charging Sessions & Events",
            "message": f"Found {len(events)} charging event(s) recorded today.",
            "data": events
        }

    # 5. "show EVs below 30% battery" (or other battery threshold)
    if "below" in q or "under" in q or "low battery" in q or "<" in q or ("battery" in q and "30" in q):
        threshold_match = re.search(r'(\d+)\s*%', q)
        if not threshold_match:
            threshold_match = re.search(r'(?:below|under|<)\s*(\d+)', q)
        threshold = int(threshold_match.group(1)) if threshold_match else 30

        slots = database.get_all_slots()
        low_battery_slots = [
            s for s in slots 
            if s['status'] in ('CHARGING', 'COMPLETED', 'FAULT') 
            and s['battery_level'] is not None 
            and 0 < s['battery_level'] < threshold
        ]
        return {
            "status": "success",
            "type": "slot_list",
            "title": f"EVs Below {threshold}% Battery",
            "message": f"Found {len(low_battery_slots)} connected vehicle(s) with battery level below {threshold}%.",
            "data": low_battery_slots
        }

    # 6. "show highest energy consumption" / top energy
    if "highest" in q or "maximum" in q or "max energy" in q or "most energy" in q or "top energy" in q:
        slots = database.get_all_slots()
        sorted_slots = sorted(slots, key=lambda s: s['energy_consumed'] or 0.0, reverse=True)
        top_slot = sorted_slots[0] if sorted_slots else None
        return {
            "status": "success",
            "type": "slot_detail",
            "title": "Highest Energy Consumption",
            "message": f"Slot {top_slot['slot_id']} has the highest energy consumption with {top_slot['energy_consumed']} kWh ({top_slot['status']})." if top_slot else "No consumption data available.",
            "data": top_slot
        }

    # 7. "show faulty chargers" / fault / error
    if "fault" in q or "error" in q or "broken" in q or "offline" in q:
        slots = database.get_slots_by_status('FAULT')
        return {
            "status": "success",
            "type": "slot_list",
            "title": "Faulty Chargers",
            "message": f"Found {len(slots)} charger(s) reporting FAULT state.",
            "data": slots
        }

    # 8. "available charging slots" / show available
    if "available" in q or "free slots" in q or "vacant slots" in q:
        slots = database.get_slots_by_status('AVAILABLE')
        return {
            "status": "success",
            "type": "slot_list",
            "title": "Available Charging Slots",
            "message": f"Found {len(slots)} available charging slot(s).",
            "data": slots
        }

    # 9. "show completed charging"
    if "completed" in q or "finished" in q or "done" in q:
        slots = database.get_slots_by_status('COMPLETED')
        return {
            "status": "success",
            "type": "slot_list",
            "title": "Completed Charging Sessions",
            "message": f"Found {len(slots)} completed charging session(s) parked at slots.",
            "data": slots
        }

    # 10. "show charging vehicles" / show currently charging
    if "charging" in q:
        slots = database.get_slots_by_status('CHARGING')
        return {
            "status": "success",
            "type": "slot_list",
            "title": "Active Charging Vehicles",
            "message": f"Found {len(slots)} active vehicle(s) currently charging.",
            "data": slots
        }

    # Fallback standard message
    return {
        "status": "info",
        "type": "unrecognized",
        "title": "Query Guide",
        "message": "Please search for charging slots, EV status, battery level, charging sessions or energy usage.",
        "suggestions": [
            "available charging slots",
            "how many chargers are available",
            "how many EVs are currently charging",
            "status of EV03",
            "show charging vehicles",
            "show completed charging",
            "show today's charging sessions",
            "show EVs below 30% battery",
            "show highest energy consumption",
            "show faulty chargers"
        ],
        "data": None
    }

# ============================================================================
# APPLICATION ENTRYPOINT
# ============================================================================

if __name__ == '__main__':
    print("==================================================")
    print(" IoT-Based Smart EV Charging Slot Management System")
    print(" Mode: DEMO / SIMULATION MODE (No physical ESP32 required)")
    print(" Dashboard URL: http://127.0.0.1:5000")
    print("==================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
