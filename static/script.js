/**
 * IoT-Based Smart EV Charging Slot Management System
 * Frontend Controller: AJAX Polling, Search Handler, Dynamic Slot Grid, Plotly Analytics
 */

// Global State
let pollingIntervalSlots = null;
let pollingIntervalEvents = null;
let analyticsLoaded = false;

// Theme Palette for Plotly Charts
const THEME = {
    bgCard: '#1B1B1B',
    bgPlot: '#141414',
    text: '#B8B8B8',
    textBright: '#FFFFFF',
    grid: '#262626',
    yellow: '#FFD43B',
    gold: '#E5B93F',
    highlight: '#FFF1A8',
    available: '#6F8F5F',
    completed: '#8A8A8A',
    fault: '#B94A48'
};

document.addEventListener('DOMContentLoaded', () => {
    initClock();
    fetchChargingStatus();
    fetchRecentEvents();
    fetchAnalytics();

    // Setup polling every 3.5 seconds for live status without page refresh
    pollingIntervalSlots = setInterval(fetchChargingStatus, 3500);
    pollingIntervalEvents = setInterval(fetchRecentEvents, 4000);
});

// ============================================================================
// CLOCK & TIME UTILS
// ============================================================================

function initClock() {
    function update() {
        const now = new Date();
        const el = document.getElementById('systemClock');
        if (el) {
            el.textContent = now.toLocaleTimeString();
        }
    }
    update();
    setInterval(update, 1000);
}

function updateSyncIndicator() {
    const syncEl = document.getElementById('lastSyncTime');
    if (syncEl) {
        const now = new Date();
        syncEl.textContent = `Last sync: ${now.toLocaleTimeString()}`;
    }
}

// ============================================================================
// CHARGING STATUS & SLOTS POLLING
// ============================================================================

async function fetchChargingStatus() {
    try {
        const res = await fetch('/api/charging-status');
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const data = await res.json();

        if (data.status === 'success') {
            updateKPIs(data.stats);
            renderSlotsGrid(data.slots);
            renderActiveMonitor(data.slots);
            updateSyncIndicator();
        }
    } catch (err) {
        console.error('Error fetching charging status:', err);
    }
}

function updateKPIs(stats) {
    if (!stats) return;
    document.getElementById('statTotalSlots').textContent = stats.total_slots ?? 10;
    document.getElementById('statAvailable').textContent = stats.available ?? 0;
    document.getElementById('statCharging').textContent = stats.charging ?? 0;
    document.getElementById('statCompleted').textContent = stats.completed ?? 0;
    
    const energyEl = document.getElementById('statEnergy');
    energyEl.innerHTML = `${(stats.energy_used ?? 0).toFixed(1)} <span class="unit">kWh</span>`;

    const battEl = document.getElementById('statBatteryAvg');
    battEl.innerHTML = `${(stats.battery_average ?? 0).toFixed(1)} <span class="unit">%</span>`;
}

function renderSlotsGrid(slots) {
    const grid = document.getElementById('slotsGrid');
    if (!grid || !slots) return;

    let html = '';
    slots.forEach(slot => {
        const isCharging = slot.status === 'CHARGING';
        const isAvail = slot.status === 'AVAILABLE';
        const isComp = slot.status === 'COMPLETED';
        const isFault = slot.status === 'FAULT';

        let statusClass = 'is-available';
        if (isCharging) statusClass = 'is-charging';
        else if (isComp) statusClass = 'is-completed';
        else if (isFault) statusClass = 'is-fault';

        let batteryClass = 'charging';
        if (isComp) batteryClass = 'completed';
        else if (isFault || (slot.battery_level > 0 && slot.battery_level < 30)) batteryClass = 'low';

        html += `
            <div class="slot-card ${statusClass}" id="slot-${slot.slot_id}">
                <div class="slot-card-header">
                    <span class="slot-id-badge">${slot.slot_id}</span>
                    <span class="slot-status-badge badge-${slot.status}">${slot.status}</span>
                </div>

                <div class="vehicle-info">
                    ${slot.vehicle_number 
                        ? `<span class="vehicle-number">${slot.vehicle_number}</span>
                           <span class="vehicle-type">${slot.vehicle_type || 'ELECTRIC VEHICLE'}</span>`
                        : `<span class="no-vehicle">No EV connected</span>
                           <span class="vehicle-type">Bay Ready</span>`
                    }
                </div>

                <div class="battery-bar-container">
                    <div class="battery-header">
                        <span>Battery State</span>
                        <span style="font-family: var(--font-mono); font-weight: 600;">${slot.battery_level || 0}%</span>
                    </div>
                    <div class="battery-track">
                        <div class="battery-fill ${batteryClass}" style="width: ${slot.battery_level || 0}%"></div>
                    </div>
                </div>

                <div class="slot-telemetry">
                    <div class="telemetry-item">
                        <span class="telemetry-label">Power</span>
                        <span class="telemetry-val">${(slot.charging_power || 0).toFixed(1)} kW</span>
                    </div>
                    <div class="telemetry-item">
                        <span class="telemetry-label">Energy</span>
                        <span class="telemetry-val">${(slot.energy_consumed || 0).toFixed(1)} kWh</span>
                    </div>
                </div>
            </div>
        `;
    });

    grid.innerHTML = html;
}

function renderActiveMonitor(slots) {
    const tbody = document.getElementById('activeMonitorBody');
    if (!tbody || !slots) return;

    // Filter active (charging or completed) sessions
    const active = slots.filter(s => s.status === 'CHARGING' || s.status === 'COMPLETED');

    if (active.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center" style="color: var(--text-muted); padding: 20px;">No vehicles currently charging or completed.</td></tr>`;
        return;
    }

    let rowsHtml = '';
    active.forEach(s => {
        const isCharging = s.status === 'CHARGING';
        const statusBadge = `<span class="slot-status-badge badge-${s.status}">${s.status}</span>`;
        const startTime = s.charging_start_time ? s.charging_start_time.split(' ')[1] : '--';
        const estFinish = s.estimated_completion ? s.estimated_completion.split(' ')[1] : '--';

        rowsHtml += `
            <tr>
                <td><span class="monitor-slot-tag">${s.slot_id}</span> ${statusBadge}</td>
                <td style="font-family: var(--font-mono); font-weight: 600;">${s.vehicle_number || 'N/A'}</td>
                <td>${s.vehicle_type || 'CAR'}</td>
                <td style="font-family: var(--font-mono); color: ${isCharging ? 'var(--primary-yellow)' : 'var(--text-primary)'}; font-weight: 700;">
                    ${s.battery_level}%
                </td>
                <td style="font-family: var(--font-mono);">${(s.charging_power || 0).toFixed(1)} kW</td>
                <td style="font-family: var(--font-mono); color: var(--secondary-gold);">${(s.energy_consumed || 0).toFixed(1)} kWh</td>
                <td style="font-family: var(--font-mono); color: var(--text-muted);">${startTime}</td>
                <td style="font-family: var(--font-mono); color: var(--text-muted);">${estFinish}</td>
            </tr>
        `;
    });

    tbody.innerHTML = rowsHtml;
}

// ============================================================================
// RECENT EVENTS POLLING
// ============================================================================

async function fetchRecentEvents() {
    try {
        const res = await fetch('/api/recent-events?limit=8');
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const data = await res.json();

        if (data.status === 'success') {
            renderRecentEvents(data.events);
        }
    } catch (err) {
        console.error('Error fetching recent events:', err);
    }
}

function renderRecentEvents(events) {
    const container = document.getElementById('recentEventsList');
    if (!container || !events) return;

    if (events.length === 0) {
        container.innerHTML = `<div class="loading-placeholder">No recent charging events recorded.</div>`;
        return;
    }

    let html = '';
    events.forEach(ev => {
        const timePart = ev.timestamp ? ev.timestamp.split(' ')[1] : '--';
        const telemetryInfo = ev.battery_level ? `${ev.battery_level}% &bull; ${(ev.charging_power || 0).toFixed(1)} kW` : '';

        html += `
            <div class="event-row event-${ev.event_type}">
                <div class="event-left">
                    <div class="event-meta">
                        <span class="event-type-badge">${ev.event_type}</span>
                        <span class="event-slot">${ev.slot_id}</span>
                        ${ev.vehicle_number ? `<span class="event-vehicle">${ev.vehicle_number}</span>` : ''}
                    </div>
                </div>
                <div class="event-right">
                    <span class="event-time">${timePart}</span>
                    <span class="event-telemetry">${telemetryInfo}</span>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// ============================================================================
// SEARCH PROCESSING
// ============================================================================

async function handleSearchSubmit(e) {
    if (e) e.preventDefault();
    const input = document.getElementById('searchInput');
    const query = input.value.trim();
    if (!query) return;

    await executeSearch(query);
}

function quickQuery(queryText) {
    const input = document.getElementById('searchInput');
    input.value = queryText;
    executeSearch(queryText);
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    closeSearchResult();
}

function closeSearchResult() {
    const card = document.getElementById('searchResultsCard');
    if (card) card.style.display = 'none';
}

async function executeSearch(query) {
    const card = document.getElementById('searchResultsCard');
    const titleEl = document.getElementById('searchResultTitle');
    const msgEl = document.getElementById('searchResultMessage');
    const contentEl = document.getElementById('searchResultContent');

    titleEl.textContent = `Search: "${query}"`;
    msgEl.textContent = 'Querying SQLite database...';
    contentEl.innerHTML = '';
    card.style.display = 'block';

    try {
        const res = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        const result = await res.json();

        msgEl.textContent = result.message || '';

        if (result.type === 'slot_detail' && result.data) {
            const s = result.data;
            contentEl.innerHTML = `
                <div class="result-mini-card" style="border-left: 3px solid var(--primary-yellow); max-width: 480px;">
                    <div class="rm-header">
                        <span class="rm-slot">${s.slot_id}</span>
                        <span class="slot-status-badge badge-${s.status}">${s.status}</span>
                    </div>
                    <div class="rm-body">
                        <div><strong>Vehicle:</strong> ${s.vehicle_number || 'None'} (${s.vehicle_type || 'N/A'})</div>
                        <div><strong>Battery:</strong> ${s.battery_level}%</div>
                        <div><strong>Charging Power:</strong> ${s.charging_power} kW</div>
                        <div><strong>Energy Consumed:</strong> ${s.energy_consumed} kWh</div>
                        <div><strong>Start Time:</strong> ${s.charging_start_time || 'N/A'}</div>
                        <div><strong>Est. Completion:</strong> ${s.estimated_completion || 'N/A'}</div>
                    </div>
                </div>
            `;
        } else if (result.type === 'slot_list' && Array.isArray(result.data)) {
            if (result.data.length === 0) {
                contentEl.innerHTML = `<div style="color: var(--text-muted); font-style: italic;">No matching slots found.</div>`;
            } else {
                let cardsHtml = '<div class="result-cards-grid">';
                result.data.forEach(s => {
                    cardsHtml += `
                        <div class="result-mini-card">
                            <div class="rm-header">
                                <span class="rm-slot">${s.slot_id}</span>
                                <span class="slot-status-badge badge-${s.status}">${s.status}</span>
                            </div>
                            <div class="rm-body">
                                <div><strong>Vehicle:</strong> ${s.vehicle_number || 'None'}</div>
                                <div><strong>Battery:</strong> ${s.battery_level}% | <strong>Power:</strong> ${s.charging_power} kW</div>
                                <div><strong>Energy:</strong> ${s.energy_consumed} kWh</div>
                            </div>
                        </div>
                    `;
                });
                cardsHtml += '</div>';
                contentEl.innerHTML = cardsHtml;
            }
        } else if (result.type === 'event_list' && Array.isArray(result.data)) {
            let evHtml = '<div class="events-list" style="max-height: 250px;">';
            result.data.slice(0, 8).forEach(ev => {
                evHtml += `
                    <div class="event-row event-${ev.event_type}">
                        <div class="event-left">
                            <span class="event-type-badge">${ev.event_type} - ${ev.slot_id}</span>
                            <span class="event-vehicle">${ev.vehicle_number || 'N/A'}</span>
                        </div>
                        <div class="event-right">
                            <span class="event-time">${ev.timestamp}</span>
                            <span class="event-telemetry">${ev.battery_level || 0}% &bull; ${ev.charging_power || 0} kW</span>
                        </div>
                    </div>
                `;
            });
            evHtml += '</div>';
            contentEl.innerHTML = evHtml;
        } else if (result.type === 'unrecognized' && result.suggestions) {
            let sugHtml = '<div class="query-chips" style="margin-top: 10px;">';
            result.suggestions.forEach(s => {
                sugHtml += `<button type="button" class="chip" onclick="quickQuery('${s}')">${s}</button>`;
            });
            sugHtml += '</div>';
            contentEl.innerHTML = sugHtml;
        }
    } catch (err) {
        msgEl.textContent = `Error executing search: ${err.message}`;
    }
}

// ============================================================================
// HISTORICAL ANALYTICS & PLOTLY VISUALIZATIONS
// ============================================================================

async function fetchAnalytics() {
    try {
        const res = await fetch('/api/analytics');
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const data = await res.json();

        if (data.status === 'success') {
            renderAnalyticsSummary(data.summary);
            renderPlotlyCharts(data.charts);
            analyticsLoaded = true;
        }
    } catch (err) {
        console.error('Error fetching analytics:', err);
    }
}

function renderAnalyticsSummary(summary) {
    if (!summary) return;
    document.getElementById('hTotalRecords').textContent = summary.total_records;
    document.getElementById('hCompleted').textContent = summary.completed_sessions;
    document.getElementById('hAvgDuration').textContent = `${summary.average_duration_min} min`;
    document.getElementById('hTotalEnergy').textContent = `${summary.total_energy_kwh} kWh`;
    document.getElementById('hAvgEnergy').textContent = `${summary.average_energy_kwh} kWh`;
    document.getElementById('hMostUsedSlot').textContent = `${summary.most_used_slot} (${summary.most_used_slot_count})`;
}

function renderPlotlyCharts(charts) {
    if (!charts || !window.Plotly) return;

    const commonLayout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { family: 'Outfit, sans-serif', color: THEME.text, size: 12 },
        margin: { l: 45, r: 20, t: 30, b: 40 },
        showlegend: false
    };

    const config = { responsive: true, displayModeBar: false };

    // 1. Daily Charging Sessions
    if (charts.daily_sessions) {
        Plotly.newPlot('chartDailySessions', [{
            x: charts.daily_sessions.x,
            y: charts.daily_sessions.y,
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: THEME.yellow, width: 3, shape: 'spline' },
            marker: { color: THEME.highlight, size: 6 },
            fill: 'tozeroy',
            fillcolor: 'rgba(255, 212, 59, 0.1)'
        }], {
            ...commonLayout,
            xaxis: { color: THEME.text, gridcolor: THEME.grid, tickangle: -25 },
            yaxis: { color: THEME.text, gridcolor: THEME.grid, title: 'Sessions' }
        }, config);
    }

    // 2. Daily Energy Consumption
    if (charts.daily_energy) {
        Plotly.newPlot('chartDailyEnergy', [{
            x: charts.daily_energy.x,
            y: charts.daily_energy.y,
            type: 'bar',
            marker: {
                color: THEME.gold,
                line: { color: THEME.yellow, width: 1 }
            }
        }], {
            ...commonLayout,
            xaxis: { color: THEME.text, gridcolor: THEME.grid, tickangle: -25 },
            yaxis: { color: THEME.text, gridcolor: THEME.grid, title: 'kWh' }
        }, config);
    }

    // 3. Vehicle Type Distribution
    if (charts.vehicle_distribution) {
        Plotly.newPlot('chartVehicleDistribution', [{
            labels: charts.vehicle_distribution.labels,
            values: charts.vehicle_distribution.values,
            type: 'pie',
            hole: 0.55,
            marker: {
                colors: [THEME.yellow, THEME.available, THEME.completed, THEME.gold]
            },
            textinfo: 'label+percent',
            insidetextorientation: 'radial'
        }], {
            ...commonLayout,
            showlegend: true,
            legend: { orientation: 'h', y: -0.15, font: { color: THEME.text } }
        }, config);
    }

    // 4. Charging Slot Utilization
    if (charts.slot_utilization) {
        Plotly.newPlot('chartSlotUtilization', [{
            x: charts.slot_utilization.x,
            y: charts.slot_utilization.y,
            type: 'bar',
            marker: {
                color: 'rgba(255, 212, 59, 0.85)',
                line: { color: THEME.yellow, width: 1 }
            }
        }], {
            ...commonLayout,
            xaxis: { color: THEME.text, gridcolor: THEME.grid },
            yaxis: { color: THEME.text, gridcolor: THEME.grid, title: 'Total Sessions' }
        }, config);
    }

    // 5. Battery Level Distribution (Start vs End)
    if (charts.battery_distribution) {
        Plotly.newPlot('chartBatteryDistribution', [
            {
                x: charts.battery_distribution.start,
                name: 'Start Battery (%)',
                type: 'histogram',
                opacity: 0.75,
                marker: { color: '#B94A48' }
            },
            {
                x: charts.battery_distribution.end,
                name: 'End Battery (%)',
                type: 'histogram',
                opacity: 0.75,
                marker: { color: THEME.available }
            }
        ], {
            ...commonLayout,
            barmode: 'overlay',
            showlegend: true,
            legend: { orientation: 'h', y: 1.15, font: { color: THEME.text } },
            xaxis: { color: THEME.text, gridcolor: THEME.grid, title: 'Battery %' },
            yaxis: { color: THEME.text, gridcolor: THEME.grid, title: 'Frequency' }
        }, config);
    }

    // 6. Charging Duration Distribution
    if (charts.duration_distribution) {
        Plotly.newPlot('chartDurationDistribution', [{
            x: charts.duration_distribution.durations,
            type: 'histogram',
            marker: {
                color: THEME.gold,
                line: { color: THEME.highlight, width: 1 }
            },
            nbinsx: 12
        }], {
            ...commonLayout,
            xaxis: { color: THEME.text, gridcolor: THEME.grid, title: 'Minutes' },
            yaxis: { color: THEME.text, gridcolor: THEME.grid, title: 'Count' }
        }, config);
    }
}
