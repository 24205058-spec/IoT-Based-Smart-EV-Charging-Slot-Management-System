# Node-RED: EV CHARGING IoT SIMULATOR

## Academic Simulation Disclosure
> **ACADEMIC DEMONSTRATION NOTICE:**  
> This Node-RED flow serves as the **Virtual Edge Gateway and IoT Sensor Simulator** for the *IoT-Based Smart EV Charging Slot Management System*.  
> **No physical ESP32 hardware sensors are currently connected.**  
> The system architecture is fully engineered to be plug-and-play ready for future physical ESP32 and sensor hardware deployment without changing the backend database schema or API interface.

---

## 1. Flow Overview
The flow file `ev_charging_flow.json` provides:
- **Periodic Telemetry Generator:** An inject node fires every 5 seconds, triggering a JavaScript function that simulates battery ramping (e.g., slot `EV03` battery level increasing from 67% upwards, incrementing energy draw and power).
- **Interactive Event Triggers:**
  - `Trigger: EV04 Vehicle Arrival` (`CONNECTED` event, slot becomes occupied/charging)
  - `Trigger: EV02 Vehicle Departure` (`DISCONNECTED` event, slot resets to `AVAILABLE`)
  - `Trigger: EV09 Sensor Fault` (`FAULT` event, error state simulated)
- **Dual Communication Channels:**
  - **MQTT Topics:** Publishes live JSON packets to `ev/charging/status` and `ev/charging/event` (broker: `localhost:1883`).
  - **HTTP Endpoints:** Directly executes HTTP POST requests to Flask at:
    - `http://127.0.0.1:5000/api/node-red/update`
    - `http://127.0.0.1:5000/api/node-red/event`
    *(Ensures real-time updates work out-of-the-box even if a local MQTT broker is not actively running).*

---

## 2. Step-by-Step Setup & Import Instructions

### Step 1: Start Node-RED
Ensure Node.js and Node-RED are installed on your Windows system:
```powershell
node-red
```
The terminal will display:
```
Server now running at http://127.0.0.1:1880/
```

### Step 2: Open Node-RED Web Interface
Open your browser and navigate to:
```
http://127.0.0.1:1880/
```

### Step 3: Import the Flow
1. Click the top-right **Hamburger Menu** (`≡`).
2. Select **Import** (or press `Ctrl+I`).
3. Click **select a file to import** and browse to:
   `node_red/ev_charging_flow.json`
4. Choose **Import to: new flow** and click **Import**.

### Step 4: Deploy the Flow
Click the red **Deploy** button in the top-right corner.

### Step 5: Verify Live Telemetry
1. Open the Node-RED **Debug panel** (the insect icon on the right sidebar).
2. You will observe outgoing JSON payloads every 5 seconds.
3. Observe the Flask dashboard at `http://127.0.0.1:5000/`: the `EV03` battery percentage and energy consumption will update automatically every few seconds without refreshing the page!

---

## 3. MQTT Message Specifications

### Topic: `ev/charging/status`
Sent on every telemetry interval:
```json
{
  "slot_id": "EV03",
  "status": "CHARGING",
  "vehicle_number": "TN58AB1234",
  "vehicle_type": "CAR",
  "battery_level": 68,
  "charging_power": 7.2,
  "energy_consumed": 18.6
}
```

### Topic: `ev/charging/event`
Sent when state transitions or faults occur:
```json
{
  "event_type": "CONNECTED",
  "slot_id": "EV04",
  "vehicle_number": "HR26CQ9011",
  "vehicle_type": "CAR",
  "battery_level": 21,
  "charging_power": 11.0,
  "energy_consumed": 0.5
}
```

---

## 4. Future ESP32 Hardware Integration Guide
To transition this academic simulator to real physical IoT hardware:
1. **Sensors:**
   - **IR / Ultrasonic Sensor (HC-SR04):** Positioned at each parking slot floor or overhead to detect vehicle presence.
   - **Current Transformer (ACS712 / SCT-013):** Clamped onto AC mains line to measure real charging current and power draw.
2. **Microcontroller (ESP32):**
   - Connect sensors to ESP32 GPIO ADC and digital pins.
   - Connect ESP32 to local Wi-Fi.
   - Use Arduino `PubSubClient` or `HTTPClient` to send the identical JSON payload to the Flask API endpoint:
     `POST http://<SERVER_IP>:5000/api/node-red/update`
3. **No Backend Code Changes Required:** The Flask backend and SQLite database will accept the telemetry seamlessly.
