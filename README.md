# IoT-Based Smart EV Charging Slot Management System

> **ACADEMIC DEMONSTRATION & SIMULATION NOTICE:**  
> This project is an **academic IoT demonstration** designed to model real-time EV charging slot occupancy, power delivery, live telemetry, and historical analytics.  
> **Physical IoT sensors (e.g. ESP32, ultrasonic/current sensors) are NOT physically connected.**  
> Real-time sensor telemetry is simulated through **Node-RED** and **Flask REST APIs**. The system architecture is completely decoupled and fully ready for future physical ESP32 sensor deployment without any backend restructuring.

---

## 1. Project Title & Overview
**IoT-Based Smart EV Charging Slot Management System** is a unified, full-stack, single-page web dashboard application that brings together real-time IoT simulation, relational database management, data science analytics, and interactive data visualization for electric vehicle charging infrastructure.

---

## 2. Problem Statement
The global transition toward electric mobility requires robust, efficient charging hub management. Major operational bottlenecks include:
- Inefficient slot discovery causing long waiting lines and driver frustration.
- Inadequate visibility into real-time charging power, battery states, and bay availability.
- Absence of centralized logging for charging events, billing estimates, and hardware faults.
- Lack of data-driven insights regarding daily grid load, peak consumption hours, and slot utilization.

This project addresses these challenges by simulating an intelligent IoT-monitored charging hub that manages 10 distinct bays (`EV01` to `EV10`), delivers real-time telemetry updates without page refreshes, provides natural-language search across live records, and analyzes historical charging datasets.

---

## 3. Project Objectives
1. **Real-Time Bay Monitoring:** Monitor 10 charging slots (`EV01` to `EV10`) with distinct states: `AVAILABLE`, `CHARGING`, `COMPLETED`, and `FAULT`.
2. **Dynamic Live Telemetry:** Display live battery levels (%), charging power (kW), and cumulative energy consumption (kWh) with automatic 3–5s polling via JavaScript `fetch()`.
3. **Natural-Language Search:** Query SQLite dynamically via `POST /api/query` for status, counts, battery thresholds, and events.
4. **Historical Analytics:** Ingest historical charging logs from Excel (`EV_Charging_Dataset.xlsx`) using **Pandas** and render interactive **Plotly.js** charts.
5. **IoT Simulation via Node-RED:** Simulate vehicle connection, battery ramping, and sensor fault telemetry using Node-RED flows and MQTT/HTTP integration.
6. **Future-Proof IoT Architecture:** Establish a standardized API interface ready for physical ESP32 microcontrollers.

---

## 4. Key Features
- **Luxury Automotive Yellow/Gold Visual System:** Bespoke dark theme (`#0B0B0B`, `#1B1B1B`, `#FFD43B`, `#E5B93F`) tailored for modern EV technology platforms.
- **Dynamic 10-Slot Grid:** Visual status cards for bays EV01–EV10 with custom battery level gauges, vehicle tags, and power draw meters.
- **Live Charging Monitor Table:** Detailed breakdown of active vehicle charging sessions, start timestamps, and estimated completion times.
- **Audit Event Stream:** Chronological event logs (`CONNECTED`, `CHARGING_STARTED`, `CHARGING`, `CHARGING_COMPLETED`, `DISCONNECTED`, `FAULT`).
- **Interactive Plotly Visualizations:**
  1. *Daily Charging Sessions* (Trend spline)
  2. *Daily Energy Consumption* (kWh bars)
  3. *Vehicle Type Distribution* (Donut chart: Cars, 2-Wheelers, SUVs)
  4. *Charging Slot Utilization* (Session frequency per bay)
  5. *Battery Level Distribution* (Start vs. End battery histogram)
  6. *Charging Duration Distribution* (Session length binned frequency)
- **Natural Language Search Engine:** Handles queries like *"status of EV03"*, *"how many chargers are available"*, *"show EVs below 30% battery"*, and *"show highest energy consumption"*.

---

## 5. System Architecture

### Academic Simulation Pipeline (Current)
```
┌─────────────────────────────────┐
│   Node-RED IoT Simulator       │
│  (Virtual Edge Gateway Flows)   │
└───────────────┬─────────────────┘
                │ HTTP POST / MQTT
                ▼
┌─────────────────────────────────┐
│       Python Flask API          │
│  - Endpoint Ingestion           │
│  - Query Engine                 │
│  - Analytics Processor          │
└───────┬─────────────────┬───────┘
        │                 │
        ▼                 ▼
┌──────────────┐   ┌───────────────────────────┐
│ SQLite DB    │   │ Historical Dataset        │
│ charging.db  │   │ (EV_Charging_Dataset.xlsx)│
└───────┬──────┘   └─────────────┬─────────────┘
        │                        │ Pandas & OpenPyXL
        ▼                        ▼
┌──────────────────────────────────────────────┐
│  Single-Page Web Dashboard                   │
│  - HTML5 / CSS3 (Yellow-Gold Dark Theme)     │
│  - Vanilla JavaScript Polling fetch()        │
│  - Interactive Plotly.js Visualizations      │
└──────────────────────────────────────────────┘
```

### Future Physical IoT Deployment Architecture
```
┌────────────────────────────┐
│ Physical Sensors at Bays   │
│ - HC-SR04 Ultrasonic / IR  │ (Slot Occupancy Detection)
│ - ACS712 / SCT-013 Current │ (Real Power / Current Draw)
└─────────────┬──────────────┘
              │ GPIO Pins (Analog / Digital)
              ▼
┌────────────────────────────┐
│   ESP32 Microcontroller    │
│ - Wi-Fi Station Mode       │
│ - Local Analog Sampling    │
└─────────────┬──────────────┘
              │ Wi-Fi (MQTT over 1883 or HTTP POST)
              ▼
┌────────────────────────────┐
│      Flask API Server      │
│  (Same API: /api/node-red/update)
└────────────────────────────┘
```

---

## 6. Technology Stack & Role of Each Component

| Technology | Role & Purpose |
|------------|----------------|
| **Python Flask** | Lightweight backend web framework. Hosts web routes, provides RESTful JSON APIs for live slot states, search queries, historical metrics, and Node-RED ingestion. |
| **SQLite (`charging.db`)** | Relational embedded database storing live states for 10 charging bays (`charging_slots`) and transactional event logs (`charging_events`). Supports safe parameterized queries. |
| **Pandas & OpenPyXL** | Ingests and processes the historical Excel dataset (`EV_Charging_Dataset.xlsx`). Computes KPIs, groupings, aggregate statistics, and series distributions for Plotly. |
| **Plotly.js** | Renders 6 responsive, interactive, client-side data visualizations with custom gold-dark color schemes, hover states, and legends. |
| **HTML5 / CSS3 / Vanilla JS** | Pure frontend stack without heavy frameworks (no React, Angular, Vue, or Bootstrap). Uses CSS Grid and Flexbox for responsive luxury aesthetics and asynchronous `fetch()` polling. |
| **Node-RED** | Visual IoT orchestration tool acting as the simulation engine. Uses inject and function nodes to generate realistic charging cycles, battery increments, and fault alarms. |
| **MQTT** | Standardized IoT protocol supported in the Node-RED flow (`ev/charging/status`, `ev/charging/event`) for publish/subscribe telemetry exchange. |

---

## 7. Database Structure (SQLite: `charging.db`)

### Table 1: `charging_slots`
Stores current state and telemetry of the 10 charging bays (`EV01` to `EV10`).
```sql
CREATE TABLE IF NOT EXISTS charging_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,                -- 'AVAILABLE', 'CHARGING', 'COMPLETED', 'FAULT'
    vehicle_number TEXT,
    vehicle_type TEXT,                  -- 'CAR', '2-WHEELER', 'SUV'
    battery_level INTEGER DEFAULT 0,    -- 0 to 100%
    charging_power REAL DEFAULT 0.0,    -- in kW
    energy_consumed REAL DEFAULT 0.0,   -- in kWh
    charging_start_time TEXT,
    estimated_completion TEXT,
    last_updated TEXT
);
```

### Table 2: `charging_events`
Stores timestamped historical telemetry events and bay state changes.
```sql
CREATE TABLE IF NOT EXISTS charging_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,           -- 'CONNECTED', 'CHARGING_STARTED', 'CHARGING', 'CHARGING_COMPLETED', 'DISCONNECTED', 'FAULT'
    slot_id TEXT NOT NULL,
    vehicle_number TEXT,
    battery_level INTEGER,
    charging_power REAL,
    energy_consumed REAL,
    timestamp TEXT NOT NULL
);
```

---

## 8. REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the main single-page web dashboard. |
| `GET` | `/dashboard` | Alias for dashboard page. |
| `GET` | `/api/charging-status` | Returns live status for all 10 slots and aggregate hub statistics (Total, Available, Charging, Completed, Energy, Battery Avg). Polled every 3.5s. |
| `GET` | `/api/recent-events` | Returns recent charging events from `charging_events` table (limit default: 10). Polled every 4s. |
| `GET` | `/api/slot/<slot_id>` | Returns detailed record for a specific slot (e.g. `/api/slot/EV03`). |
| `POST` | `/api/query` | Natural language search endpoint. Parses search text and returns dynamic SQLite results. |
| `GET` | `/api/analytics` | Computes historical KPIs and chart series from `data/EV_Charging_Dataset.xlsx` using Pandas. |
| `POST` | `/api/node-red/event` | Ingests simulated discrete events (connection, disconnection, fault) from Node-RED or IoT hardware. |
| `POST` | `/api/node-red/update` | Ingests continuous sensor telemetry updates (battery ramping, power, kWh) from Node-RED or IoT hardware. |

---

## 9. Search Functionality (`POST /api/query`)

The frontend search bar sends queries formatted as:
```json
{
  "query": "available charging slots"
}
```

The Flask backend dynamically interprets the natural language string and queries SQLite using parameterized SQL queries.

### Supported Queries:
1. **"available charging slots"**: Returns all bays where `status = 'AVAILABLE'`.
2. **"how many chargers are available"**: Returns the exact count of available slots.
3. **"how many EVs are currently charging"**: Returns the count of slots where `status = 'CHARGING'`.
4. **"status of EV03"**: Returns the full database record for bay `EV03` (Status, Battery %, Power kW, Energy kWh, Timestamps).
5. **"show charging vehicles"**: Returns all actively charging vehicles and their license plates.
6. **"show completed charging"**: Returns vehicles that reached 100% and are awaiting departure.
7. **"show today's charging sessions"**: Retrieves all charging event logs recorded today.
8. **"show EVs below 30% battery"**: Filters connected vehicles with battery level under 30%.
9. **"show highest energy consumption"**: Identifies the slot with the maximum cumulative kWh draw.
10. **"show faulty chargers"**: Returns slots currently reporting `FAULT` state.

*Fallback Response:* If an unrecognized query is entered, the system suggests valid query patterns:
> *"Please search for charging slots, EV status, battery level, charging sessions or energy usage."*

---

## 10. Historical Analytics & Excel Dataset
- **Dataset File:** `data/EV_Charging_Dataset.xlsx`
- **Columns:** `Record_ID`, `Date`, `Entry_Time`, `Exit_Time`, `Slot_ID`, `Vehicle_Type`, `Charging_Duration_Min`, `Energy_Consumed_kWh`, `Battery_Start`, `Battery_End`, `Status`.
- **Processing:** Processed on demand via **Pandas** and **OpenPyXL** without impacting the live SQLite operational database.
- **Computed Metrics:**
  - Total records and completed sessions
  - Average charging duration (minutes)
  - Total energy consumed and average energy per session (kWh)
  - Vehicle fleet breakdown (Cars vs. 2-Wheelers vs. SUVs)
  - Most frequently utilized charging bay
  - Daily energy draw and session trends

---

## 11. Step-by-Step Installation & Setup

### Prerequisites
- Python 3.10 to 3.13 installed on Windows.
- VS Code (Visual Studio Code).
- Node.js & Node-RED (optional for simulation triggers).

### Step 1: Open Project in VS Code
1. Unzip `IoT-Based-Smart-EV-Charging-Slot-Management-System.zip`.
2. Launch VS Code.
3. Go to **File -> Open Folder...** and select `IoT-Based-Smart-EV-Charging-Slot-Management-System`.

### Step 2: Create Virtual Environment
Open PowerShell inside VS Code (`Ctrl + ~`) and run:
```powershell
python -m venv venv
```

### Step 3: Activate Virtual Environment
On Windows PowerShell:
```powershell
venv\Scripts\activate
```
*(If PowerShell execution policy blocks scripts, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`)*

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Start the Flask Application
```powershell
python app.py
```
Terminal output:
```
==================================================
 IoT-Based Smart EV Charging Slot Management System
 Mode: DEMO / SIMULATION MODE (No physical ESP32 required)
 Dashboard URL: http://127.0.0.1:5000
==================================================
 * Running on http://127.0.0.1:5000
```

### Step 6: Open the Dashboard
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```
The dashboard immediately renders with populated demo slots, live statistics, active sessions, and Plotly historical analytics!

---

## 12. Running the Node-RED Simulation

### Step 1: Start Node-RED
Open a separate PowerShell terminal window and run:
```powershell
node-red
```

### Step 2: Access Node-RED Interface
Open your browser to:
```
http://127.0.0.1:1880/
```

### Step 3: Import the Flow
1. Click the top-right menu (`≡`) -> **Import**.
2. Select `node_red/ev_charging_flow.json`.
3. Click **Import** and then click the red **Deploy** button.

### Step 4: Verify Real-Time Updates
- The Node-RED flow automatically fires every 5 seconds.
- Look at slot `EV03` on the Flask dashboard (`http://127.0.0.1:5000/`): watch the battery percentage increment (`67% -> 68% -> 69%...`) and the energy consumption rise automatically **without refreshing the page**!
- Click manual trigger buttons in Node-RED (e.g. *Trigger: EV04 Vehicle Arrival*) to simulate new vehicles plugging in.

---

## 13. Viva Presentation Guide (Q&A)

### Q1: Why is this system labeled "DEMO / SIMULATION MODE"?
**Answer:** In an academic presentation, academic integrity is paramount. Physical sensors (ESP32, ultrasonic detectors, current clamps) are not physically plugged in. Instead of creating fake hardware claims, this project uses Node-RED as a Virtual Edge Gateway. The architecture and API contracts are 100% production-ready for physical hardware drops.

### Q2: Why use both SQLite and Excel?
**Answer:** They serve distinct architectural roles:
- **SQLite (`charging.db`):** Acts as the high-speed Online Transaction Processing (OLTP) database for live slot states, immediate telemetry updates, and recent audit logs.
- **Excel (`EV_Charging_Dataset.xlsx`):** Acts as the historical data warehouse for Online Analytical Processing (OLAP). Using Pandas and OpenPyXL, we analyze long-term trends and render Plotly charts without locking the operational SQLite database.

### Q3: How do live updates work without page refreshes?
**Answer:** The frontend script (`static/script.js`) establishes an asynchronous polling loop using the standard JavaScript `fetch()` API every 3.5 seconds to `/api/charging-status`. When JSON telemetry arrives, the DOM updates targeted slot cards and KPI metrics selectively without reloading the document.

### Q4: How does the system handle search queries?
**Answer:** The search input posts to `/api/query`. The backend uses natural language pattern matching and regular expressions to identify intent (status checks, count queries, battery thresholds, fault listings) and executes parameterized SQLite queries to prevent SQL injection.

### Q5: How would physical ESP32 sensors be integrated?
**Answer:** An ESP32 connected to HC-SR04 ultrasonic sensors (measuring distance to detect parked vehicles) and ACS712 current sensors (measuring AC power draw) would format sensor readings into JSON and send an HTTP POST request or publish via MQTT to `/api/node-red/update`. The Flask server and dashboard will process it identically.

---

## 14. Troubleshooting

1. **Port 5000 Already in Use:**  
   Change the port in `app.py`: `app.run(host='0.0.0.0', port=5001, debug=True)` and open `http://127.0.0.1:5001`.
2. **PowerShell Script Execution Policy Error:**  
   Run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and then run `venv\Scripts\activate`.
3. **Plotly Charts Not Showing:**  
   Ensure an active internet connection on the initial load to fetch the Plotly CDN script (`https://cdn.plot.ly/plotly-2.35.2.min.js`).

---

## 15. Future Enhancements
- Integration of an automated billing and tariff calculation engine (Peak vs. Off-peak pricing).
- Reservation and slot pre-booking system with mobile push notifications.
- Solar PV microgrid integration to dynamically throttle charging power based on renewable generation.
- RFID / NFC card authentication for driver vehicle check-in.
