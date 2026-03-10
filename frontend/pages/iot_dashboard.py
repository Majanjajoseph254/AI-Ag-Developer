import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from backend.iot import (
    register_device, get_user_devices, update_device, delete_device,
    simulate_sensor_reading, get_readings, get_readings_range,
    check_alerts, get_alerts, mark_alert_read, generate_historical_data
)


def show_iot_dashboard():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    st.title("📡 IoT Dashboard")
    st.markdown("Monitor your farm sensors, view analytics, and manage alerts.")

    unread_alerts = get_alerts(user_id, unread_only=True)
    alert_count = len(unread_alerts) if unread_alerts else 0
    alert_label = f"🔔 Alerts ({alert_count})" if alert_count > 0 else "🔔 Alerts"

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Device Management", "📊 Live Monitoring", "📈 Analytics", alert_label])

    with tab1:
        _device_management_tab(user_id)

    with tab2:
        _live_monitoring_tab(user_id)

    with tab3:
        _analytics_tab(user_id)

    with tab4:
        _alerts_tab(user_id)


def _device_management_tab(user_id):
    st.subheader("Manage Your IoT Devices")

    with st.expander("➕ Add New Device", expanded=False):
        with st.form("add_device_form"):
            dev_name = st.text_input("Device Name", placeholder="e.g., Field Sensor 1")
            dev_type = st.selectbox("Device Type", ["Soil Sensor", "Weather Station", "Light Sensor", "Full Station"])
            dev_location = st.text_input("Location", placeholder="e.g., North Field")
            submitted = st.form_submit_button("Add Device", type="primary")
            if submitted:
                if dev_name and dev_location:
                    try:
                        register_device(user_id, dev_name, dev_type, dev_location)
                        st.success(f"Device '{dev_name}' registered successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to register device: {e}")
                else:
                    st.warning("Please fill in all fields.")

    devices = get_user_devices(user_id)
    if not devices:
        st.info("No IoT devices registered yet. Add your first device above!")
        return

    for device in devices:
        dev_id = device["id"]
        is_active = device["is_active"]
        status_icon = "🟢" if is_active else "🔴"
        status_text = "Active" if is_active else "Inactive"

        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            with col1:
                st.markdown(f"**{status_icon} {device['device_name']}**")
                st.caption(f"{device['device_type']} | {device['location']}")
            with col2:
                st.markdown(f"Status: **{status_text}**")
            with col3:
                toggle_label = "Deactivate" if is_active else "Activate"
                if st.button(toggle_label, key=f"toggle_{dev_id}"):
                    update_device(dev_id, user_id, not is_active)
                    st.rerun()
            with col4:
                col_demo, col_del = st.columns(2)
                with col_demo:
                    if st.button("📊", key=f"demo_{dev_id}", help="Generate 30 days of demo data"):
                        with st.spinner("Generating..."):
                            count = generate_historical_data(dev_id, days=30)
                        st.success(f"Generated {count} readings!")
                        st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"del_{dev_id}", help="Delete device"):
                        delete_device(dev_id, user_id)
                        st.rerun()
            st.divider()


def _live_monitoring_tab(user_id):
    st.subheader("Live Sensor Monitoring")

    devices = get_user_devices(user_id)
    if not devices:
        st.info("No devices available. Register a device first.")
        return

    device_options = {f"{d['device_name']} ({d['device_type']})": d for d in devices}
    selected_name = st.selectbox("Select Device", list(device_options.keys()), key="live_device")
    selected_device = device_options[selected_name]
    dev_id = selected_device["id"]

    col_sim, col_check = st.columns(2)
    with col_sim:
        if st.button("🔄 Simulate New Reading", type="primary"):
            result = simulate_sensor_reading(dev_id)
            if result:
                check_alerts(dev_id)
                st.success("New reading simulated!")
                st.rerun()
    with col_check:
        st.caption("💡 Click simulate to generate a new sensor reading")

    readings = get_readings(dev_id, limit=1)
    if not readings:
        st.info("No readings yet. Click 'Simulate New Reading' to generate data.")
        return

    latest = readings[0]
    st.markdown(f"**Latest Reading** — {latest.get('recorded_at', 'N/A')}")

    metrics = []
    if latest.get("soil_moisture") is not None:
        val = float(latest["soil_moisture"])
        status = "🟢" if 25 <= val <= 75 else ("🔴" if val < 25 else "🟡")
        metrics.append(("Soil Moisture", f"{val}%", status))
    if latest.get("soil_temperature") is not None:
        val = float(latest["soil_temperature"])
        status = "🟢" if 15 <= val <= 30 else "🟡"
        metrics.append(("Soil Temp", f"{val}°C", status))
    if latest.get("soil_ph") is not None:
        val = float(latest["soil_ph"])
        status = "🟢" if 5.5 <= val <= 7.5 else "🟡"
        metrics.append(("Soil pH", f"{val}", status))
    if latest.get("air_temperature") is not None:
        val = float(latest["air_temperature"])
        status = "🟢" if val <= 35 else "🔴"
        metrics.append(("Air Temp", f"{val}°C", status))
    if latest.get("air_humidity") is not None:
        val = float(latest["air_humidity"])
        status = "🟢" if val <= 85 else "🟡"
        metrics.append(("Humidity", f"{val}%", status))
    if latest.get("rainfall") is not None:
        val = float(latest["rainfall"])
        status = "🟢" if val < 30 else "🟡"
        metrics.append(("Rainfall", f"{val} mm", status))
    if latest.get("wind_speed") is not None:
        val = float(latest["wind_speed"])
        status = "🟢" if val <= 15 else "🔴"
        metrics.append(("Wind Speed", f"{val} m/s", status))
    if latest.get("light_intensity") is not None:
        val = float(latest["light_intensity"])
        metrics.append(("Light", f"{val:,.0f} lux", "🟢"))

    if metrics:
        cols = st.columns(min(len(metrics), 4))
        for i, (name, value, status) in enumerate(metrics):
            with cols[i % len(cols)]:
                st.metric(f"{status} {name}", value)


def _analytics_tab(user_id):
    st.subheader("Sensor Analytics")

    devices = get_user_devices(user_id)
    if not devices:
        st.info("No devices available. Register a device first.")
        return

    device_options = {f"{d['device_name']} ({d['device_type']})": d for d in devices}
    selected_name = st.selectbox("Select Device", list(device_options.keys()), key="analytics_device")
    selected_device = device_options[selected_name]
    dev_id = selected_device["id"]
    dev_type = selected_device["device_type"]

    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30), key="analytics_start")
    with col_end:
        end_date = st.date_input("End Date", value=datetime.now(), key="analytics_end")

    readings = get_readings_range(dev_id, start_date, end_date)
    if not readings:
        st.info("No readings found for the selected date range. Generate demo data from Device Management tab.")
        return

    df = pd.DataFrame(readings)
    df["recorded_at"] = pd.to_datetime(df["recorded_at"])

    numeric_cols = ["soil_moisture", "soil_temperature", "air_temperature",
                    "air_humidity", "light_intensity", "soil_ph", "rainfall", "wind_speed"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if dev_type in ("Soil Sensor", "Full Station"):
        if "soil_moisture" in df.columns and df["soil_moisture"].notna().any():
            fig = px.line(df, x="recorded_at", y="soil_moisture", title="Soil Moisture Over Time")
            fig.update_layout(yaxis_title="Moisture (%)", xaxis_title="Time")
            fig.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="Low threshold")
            fig.add_hline(y=75, line_dash="dash", line_color="orange", annotation_text="High threshold")
            st.plotly_chart(fig, use_container_width=True)

        if "soil_ph" in df.columns and df["soil_ph"].notna().any():
            fig = px.line(df, x="recorded_at", y="soil_ph", title="Soil pH Over Time")
            fig.update_layout(yaxis_title="pH", xaxis_title="Time")
            fig.add_hline(y=5.5, line_dash="dash", line_color="red", annotation_text="Low pH")
            fig.add_hline(y=7.5, line_dash="dash", line_color="red", annotation_text="High pH")
            st.plotly_chart(fig, use_container_width=True)

    temp_cols = []
    if "soil_temperature" in df.columns and df["soil_temperature"].notna().any():
        temp_cols.append("soil_temperature")
    if "air_temperature" in df.columns and df["air_temperature"].notna().any():
        temp_cols.append("air_temperature")
    if temp_cols:
        fig = go.Figure()
        labels = {"soil_temperature": "Soil Temperature", "air_temperature": "Air Temperature"}
        for col in temp_cols:
            fig.add_trace(go.Scatter(x=df["recorded_at"], y=df[col], mode="lines", name=labels.get(col, col)))
        fig.update_layout(title="Temperature Over Time", yaxis_title="Temperature (°C)", xaxis_title="Time")
        st.plotly_chart(fig, use_container_width=True)

    if dev_type in ("Weather Station", "Full Station"):
        humid_rain = []
        if "air_humidity" in df.columns and df["air_humidity"].notna().any():
            humid_rain.append("air_humidity")
        if "rainfall" in df.columns and df["rainfall"].notna().any():
            humid_rain.append("rainfall")
        if humid_rain:
            fig = go.Figure()
            if "air_humidity" in humid_rain:
                fig.add_trace(go.Scatter(x=df["recorded_at"], y=df["air_humidity"], mode="lines", name="Humidity (%)"))
            if "rainfall" in humid_rain:
                fig.add_trace(go.Bar(x=df["recorded_at"], y=df["rainfall"], name="Rainfall (mm)", opacity=0.5))
            fig.update_layout(title="Humidity & Rainfall", yaxis_title="Value", xaxis_title="Time")
            st.plotly_chart(fig, use_container_width=True)

    if "light_intensity" in df.columns and df["light_intensity"].notna().any() and dev_type in ("Light Sensor", "Full Station"):
        fig = px.line(df, x="recorded_at", y="light_intensity", title="Light Intensity Over Time")
        fig.update_layout(yaxis_title="Intensity (lux)", xaxis_title="Time")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Summary Statistics")
    available = [c for c in numeric_cols if c in df.columns and df[c].notna().any()]
    if available:
        stats_data = []
        col_labels = {
            "soil_moisture": "Soil Moisture (%)",
            "soil_temperature": "Soil Temp (°C)",
            "air_temperature": "Air Temp (°C)",
            "air_humidity": "Humidity (%)",
            "light_intensity": "Light (lux)",
            "soil_ph": "Soil pH",
            "rainfall": "Rainfall (mm)",
            "wind_speed": "Wind (m/s)"
        }
        for col in available:
            stats_data.append({
                "Metric": col_labels.get(col, col),
                "Min": round(df[col].min(), 2),
                "Max": round(df[col].max(), 2),
                "Average": round(df[col].mean(), 2)
            })
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)


def _alerts_tab(user_id):
    st.subheader("IoT Alerts")

    all_alerts = get_alerts(user_id, unread_only=False)
    if not all_alerts:
        st.info("No alerts yet. Alerts are generated when sensor readings exceed thresholds.")
        return

    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        severity_filter = st.selectbox("Filter by Severity", ["All", "high", "medium"], key="alert_severity")
    with col_filter2:
        device_names = list(set(a.get("device_name", "Unknown") for a in all_alerts))
        device_filter = st.selectbox("Filter by Device", ["All"] + device_names, key="alert_device")
    with col_filter3:
        read_filter = st.selectbox("Filter by Status", ["All", "Unread", "Read"], key="alert_read")

    filtered = all_alerts
    if severity_filter != "All":
        filtered = [a for a in filtered if a.get("severity") == severity_filter]
    if device_filter != "All":
        filtered = [a for a in filtered if a.get("device_name") == device_filter]
    if read_filter == "Unread":
        filtered = [a for a in filtered if not a.get("is_read")]
    elif read_filter == "Read":
        filtered = [a for a in filtered if a.get("is_read")]

    st.caption(f"Showing {len(filtered)} alert(s)")

    for alert in filtered:
        severity = alert.get("severity", "medium")
        is_read = alert.get("is_read", False)

        if severity == "high":
            icon = "🔴"
        else:
            icon = "🟡"

        read_icon = "✉️" if not is_read else "📭"

        with st.container():
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                st.markdown(f"{icon} **{alert.get('alert_type', 'Alert')}** {read_icon}")
                st.caption(f"{alert.get('message', '')} — {alert.get('device_name', '')} ({alert.get('device_type', '')})")
                st.caption(f"🕐 {alert.get('created_at', '')}")
            with col2:
                severity_colors = {"high": "🔴 High", "medium": "🟡 Medium"}
                st.markdown(severity_colors.get(severity, severity))
            with col3:
                if not is_read:
                    if st.button("✓", key=f"read_{alert['id']}", help="Mark as read"):
                        mark_alert_read(alert["id"], user_id)
                        st.rerun()
            st.divider()
