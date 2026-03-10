import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
from datetime import datetime, timedelta
from html import escape as html_escape
from backend.db import fetch_all, fetch_one, execute_query


def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def show_robotics():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    hero_b64 = get_image_base64("assets/images/iot_sensor.png")
    if hero_b64:
        st.markdown(f"""
        <div style="position: relative; border-radius: 20px; overflow: hidden; margin-bottom: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
            <img src="data:image/png;base64,{hero_b64}" style="width: 100%; height: 220px; object-fit: cover; display: block;">
            <div style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(6,78,59,0.85) 0%, rgba(4,120,87,0.7) 50%, rgba(5,150,105,0.5) 100%); display: flex; flex-direction: column; justify-content: center; padding: 2rem 2.5rem;">
                <h1 style="color: white; font-family: 'Poppins', sans-serif; font-size: 1.8rem; margin: 0 0 0.25rem 0;">🤖 Robotics & Automation</h1>
                <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin: 0;">Manage automated farm tasks, drone surveys, and smart equipment</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hero-section">
            <h1 style="color: white;">🤖 Robotics & Automation</h1>
            <p>Manage automated farm tasks, drone surveys, and smart equipment</p>
        </div>
        """, unsafe_allow_html=True)

    total_tasks = fetch_one("SELECT COUNT(*) as count FROM automation_tasks WHERE user_id = %s", (user_id,))
    pending_tasks = fetch_one("SELECT COUNT(*) as count FROM automation_tasks WHERE user_id = %s AND status = 'pending'", (user_id,))
    running_tasks = fetch_one("SELECT COUNT(*) as count FROM automation_tasks WHERE user_id = %s AND status = 'running'", (user_id,))
    completed_tasks = fetch_one("SELECT COUNT(*) as count FROM automation_tasks WHERE user_id = %s AND status = 'completed'", (user_id,))
    total_area = fetch_one("SELECT COALESCE(SUM(area_covered), 0) as total FROM automation_tasks WHERE user_id = %s AND status = 'completed'", (user_id,))

    c1, c2, c3, c4, c5 = st.columns(5)
    stats = [
        (c1, "📋", total_tasks["count"] if total_tasks else 0, "Total Tasks"),
        (c2, "⏳", pending_tasks["count"] if pending_tasks else 0, "Pending"),
        (c3, "🔄", running_tasks["count"] if running_tasks else 0, "Running"),
        (c4, "✅", completed_tasks["count"] if completed_tasks else 0, "Completed"),
        (c5, "🗺️", f"{float(total_area['total']) if total_area else 0:.1f} ha", "Area Covered"),
    ]
    for col, icon, val, label in stats:
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">{icon}</div>
                <div class="stat-value">{val}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📝 Task Manager", "🚁 Drone Dashboard", "📊 Analytics", "🔧 Equipment"])

    with tab1:
        st.markdown("#### Schedule Automation Task")
        with st.form("add_automation_task", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                task_name = st.text_input("Task Name", placeholder="e.g., Field A Drone Survey")
                task_type = st.selectbox("Task Type", ["Drone Survey", "Auto-Irrigation", "Pest Spraying", "Soil Sampling", "Crop Monitoring", "Harvesting", "Seeding", "Fertilizer Application"])
            with col_b:
                scheduled_at = st.date_input("Scheduled Date", value=datetime.now().date())
                scheduled_time = st.time_input("Scheduled Time", value=datetime.now().replace(second=0, microsecond=0).time())
                area_covered = st.number_input("Area to Cover (hectares)", min_value=0.0, step=0.5, value=1.0)
            notes = st.text_area("Notes", placeholder="Additional details about this task...")
            submitted = st.form_submit_button("Schedule Task", use_container_width=True)

            if submitted and task_name and task_type:
                scheduled_datetime = datetime.combine(scheduled_at, scheduled_time)
                execute_query(
                    "INSERT INTO automation_tasks (user_id, task_name, task_type, status, scheduled_at, area_covered, notes) VALUES (%s, %s, %s, 'pending', %s, %s, %s)",
                    (user_id, task_name, task_type, scheduled_datetime, area_covered, notes)
                )
                st.success(f"Task '{task_name}' scheduled successfully!")
                st.rerun()
            elif submitted:
                st.warning("Please fill in task name and type.")

        st.markdown("---")
        st.markdown("#### Task Status Board")

        tasks = fetch_all(
            "SELECT * FROM automation_tasks WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )

        if tasks:
            status_cols = st.columns(3)
            status_groups = {"pending": [], "running": [], "completed": []}
            for t in tasks:
                s = t.get("status", "pending")
                if s in status_groups:
                    status_groups[s].append(t)

            headers = [("⏳ Pending", "pending", "#f59e0b"), ("🔄 Running", "running", "#3b82f6"), ("✅ Completed", "completed", "#16a34a")]
            for i, (header, status_key, color) in enumerate(headers):
                with status_cols[i]:
                    st.markdown(f"**{header}** ({len(status_groups[status_key])})")
                    for t in status_groups[status_key]:
                        t_name = html_escape(t.get("task_name", ""))
                        t_type = html_escape(t.get("task_type", ""))
                        sched = t.get("scheduled_at")
                        sched_str = sched.strftime("%b %d, %H:%M") if sched else "N/A"
                        area = t.get("area_covered") or 0
                        st.markdown(f"""
                        <div class="modern-card" style="margin-bottom: 0.75rem; border-left: 4px solid {color};">
                            <div style="font-weight: 600; font-size: 0.95rem;">{t_name}</div>
                            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.25rem;">🏷️ {t_type}</div>
                            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">📅 {sched_str} · 🗺️ {float(area):.1f} ha</div>
                        </div>
                        """, unsafe_allow_html=True)

                    if not status_groups[status_key]:
                        st.caption("No tasks")

            st.markdown("---")
            st.markdown("#### Update Task Status")
            active_tasks = [t for t in tasks if t["status"] != "completed"]
            if active_tasks:
                task_options = {f"{t['task_name']} (ID: {t['id']})": t["id"] for t in active_tasks}
                col_u1, col_u2, col_u3 = st.columns([3, 2, 1])
                with col_u1:
                    selected_task = st.selectbox("Select Task", list(task_options.keys()), key="update_task_select")
                with col_u2:
                    new_status = st.selectbox("New Status", ["pending", "running", "completed"], key="update_status_select")
                with col_u3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Update", use_container_width=True, key="update_task_btn"):
                        task_id = task_options[selected_task]
                        if new_status == "completed":
                            execute_query(
                                "UPDATE automation_tasks SET status = %s, completed_at = NOW() WHERE id = %s AND user_id = %s",
                                (new_status, task_id, user_id)
                            )
                        else:
                            execute_query(
                                "UPDATE automation_tasks SET status = %s, completed_at = NULL WHERE id = %s AND user_id = %s",
                                (new_status, task_id, user_id)
                            )
                        st.success("Task status updated!")
                        st.rerun()
            else:
                st.info("No active tasks to update.")
        else:
            st.info("No automation tasks yet. Schedule your first task above!")

    with tab2:
        st.markdown("#### Drone Monitoring Dashboard")

        drone_tasks = fetch_all(
            "SELECT * FROM automation_tasks WHERE user_id = %s AND task_type = 'Drone Survey' ORDER BY scheduled_at DESC LIMIT 10",
            (user_id,)
        )

        if drone_tasks:
            st.markdown("##### Recent Drone Missions")
            for dt in drone_tasks:
                dt_name = html_escape(dt.get("task_name", ""))
                dt_status = dt.get("status", "pending")
                dt_sched = dt.get("scheduled_at")
                dt_sched_str = dt_sched.strftime("%b %d, %Y at %H:%M") if dt_sched else "N/A"
                dt_area = dt.get("area_covered") or 0
                dt_notes = html_escape(dt.get("notes", "") or "")

                status_colors = {"pending": "#f59e0b", "running": "#3b82f6", "completed": "#16a34a"}
                status_emoji = {"pending": "⏳", "running": "🔄", "completed": "✅"}
                s_color = status_colors.get(dt_status, "#94a3b8")
                s_emoji = status_emoji.get(dt_status, "❓")

                st.markdown(f"""
                <div class="activity-item">
                    <div class="activity-dot" style="background: {s_color};"></div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600;">🚁 {dt_name}</div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">
                            {s_emoji} {html_escape(dt_status.capitalize())} · 📅 {dt_sched_str} · 🗺️ {float(dt_area):.1f} ha
                        </div>
                        {"<div style='font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;'>📝 " + dt_notes + "</div>" if dt_notes else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No drone missions scheduled. Create a 'Drone Survey' task in the Task Manager.")

        st.markdown("---")
        st.markdown("##### Simulated Flight Data")

        import random
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            st.metric("Battery Level", f"{random.randint(60, 100)}%", f"{random.randint(-5, -1)}%")
        with col_f2:
            st.metric("Altitude", f"{random.randint(30, 120)} m", f"+{random.randint(1, 10)} m")
        with col_f3:
            st.metric("Speed", f"{random.uniform(5, 25):.1f} km/h")
        with col_f4:
            st.metric("Signal Strength", f"{random.randint(70, 100)}%")

        hours = list(range(6, 19))
        alt_data = [random.randint(20, 120) for _ in hours]
        speed_data = [random.uniform(5, 30) for _ in hours]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hours, y=alt_data, mode="lines+markers", name="Altitude (m)",
            line=dict(color="#3b82f6", width=2.5), marker=dict(size=6)
        ))
        fig.add_trace(go.Scatter(
            x=hours, y=speed_data, mode="lines+markers", name="Speed (km/h)",
            line=dict(color="#f59e0b", width=2.5), marker=dict(size=6), yaxis="y2"
        ))
        fig.update_layout(
            title="Drone Flight Profile (Simulated)",
            xaxis=dict(title="Hour of Day", showgrid=False),
            yaxis=dict(title="Altitude (m)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
            yaxis2=dict(title="Speed (km/h)", overlaying="y", side="right"),
            height=350,
            margin=dict(t=40, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.25),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("#### Automation Analytics")

        all_tasks = fetch_all(
            "SELECT * FROM automation_tasks WHERE user_id = %s",
            (user_id,)
        )

        if all_tasks:
            type_counts = {}
            for t in all_tasks:
                tt = t.get("task_type", "Other")
                type_counts[tt] = type_counts.get(tt, 0) + 1

            col_ch1, col_ch2 = st.columns(2)

            with col_ch1:
                st.markdown("##### Tasks by Type")
                fig_type = px.pie(
                    values=list(type_counts.values()),
                    names=list(type_counts.keys()),
                    color_discrete_sequence=["#16a34a", "#059669", "#0d9488", "#0891b2", "#2563eb", "#7c3aed", "#f59e0b", "#ef4444"],
                    hole=0.4,
                )
                fig_type.update_layout(
                    height=300,
                    margin=dict(t=20, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                )
                st.plotly_chart(fig_type, use_container_width=True)

            with col_ch2:
                st.markdown("##### Task Status Distribution")
                status_counts = {"pending": 0, "running": 0, "completed": 0}
                for t in all_tasks:
                    s = t.get("status", "pending")
                    if s in status_counts:
                        status_counts[s] += 1

                fig_status = px.bar(
                    x=list(status_counts.keys()),
                    y=list(status_counts.values()),
                    color=list(status_counts.keys()),
                    color_discrete_map={"pending": "#f59e0b", "running": "#3b82f6", "completed": "#16a34a"},
                    labels={"x": "Status", "y": "Count"},
                )
                fig_status.update_layout(
                    height=300,
                    margin=dict(t=20, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                    showlegend=False,
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
                )
                st.plotly_chart(fig_status, use_container_width=True)

            st.markdown("---")
            st.markdown("##### Efficiency Metrics")

            completed_count = sum(1 for t in all_tasks if t.get("status") == "completed")
            total_count = len(all_tasks)
            completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0
            total_area_val = sum(float(t.get("area_covered") or 0) for t in all_tasks if t.get("status") == "completed")

            completed_with_times = [t for t in all_tasks if t.get("status") == "completed" and t.get("scheduled_at") and t.get("completed_at")]
            if completed_with_times:
                avg_duration_hrs = sum(
                    (t["completed_at"] - t["scheduled_at"]).total_seconds() / 3600
                    for t in completed_with_times
                ) / len(completed_with_times)
            else:
                avg_duration_hrs = 0

            est_time_saved = completed_count * 2.5

            mc1, mc2, mc3, mc4 = st.columns(4)
            metrics = [
                (mc1, "🎯", f"{completion_rate:.0f}%", "Completion Rate"),
                (mc2, "🗺️", f"{total_area_val:.1f} ha", "Total Area Covered"),
                (mc3, "⏱️", f"{avg_duration_hrs:.1f} hrs", "Avg Task Duration"),
                (mc4, "💡", f"{est_time_saved:.0f} hrs", "Est. Time Saved"),
            ]
            for col, icon, val, label in metrics:
                with col:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-icon">{icon}</div>
                        <div class="stat-value" style="font-size: 1.5rem;">{val}</div>
                        <div class="stat-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### Area Covered by Task Type")
            area_by_type = {}
            for t in all_tasks:
                if t.get("status") == "completed":
                    tt = t.get("task_type", "Other")
                    area_by_type[tt] = area_by_type.get(tt, 0) + float(t.get("area_covered") or 0)

            if area_by_type:
                fig_area = px.bar(
                    x=list(area_by_type.keys()),
                    y=list(area_by_type.values()),
                    labels={"x": "Task Type", "y": "Area (hectares)"},
                    color_discrete_sequence=["#16a34a"],
                )
                fig_area.update_layout(
                    height=300,
                    margin=dict(t=20, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
                )
                st.plotly_chart(fig_area, use_container_width=True)
            else:
                st.info("Complete some tasks to see area coverage analytics.")
        else:
            st.info("No automation tasks yet. Schedule tasks to see analytics.")

    with tab4:
        st.markdown("#### Equipment Inventory")

        equipment_data = [
            {"name": "DJI Agras T30", "type": "Agricultural Drone", "status": "Available", "icon": "🚁", "specs": "30L tank, 40 ha/hr coverage, RTK precision"},
            {"name": "AutoTrac Universal 300", "type": "Auto-Steering System", "status": "In Use", "icon": "🚜", "specs": "Sub-inch accuracy, compatible with all tractors"},
            {"name": "See & Spray Ultimate", "type": "Smart Sprayer", "status": "Available", "icon": "🔫", "specs": "AI weed detection, 77% herbicide reduction"},
            {"name": "Harvest CROO", "type": "Harvesting Robot", "status": "Maintenance", "icon": "🤖", "specs": "8 acres/day, gentle fruit picking"},
            {"name": "TerraSentia", "type": "Crop Scout Robot", "status": "Available", "icon": "📱", "specs": "Under-canopy phenotyping, autonomous navigation"},
            {"name": "FieldBee GPS", "type": "Guidance System", "status": "In Use", "icon": "📡", "specs": "RTK GPS, 2.5cm accuracy, auto-steering"},
        ]

        eq_cols = st.columns(3)
        for i, eq in enumerate(equipment_data):
            with eq_cols[i % 3]:
                status_color = {"Available": "#16a34a", "In Use": "#3b82f6", "Maintenance": "#f59e0b"}.get(eq["status"], "#94a3b8")
                st.markdown(f"""
                <div class="modern-card" style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 2rem;">{eq["icon"]}</span>
                        <span style="background: {status_color}; color: white; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{html_escape(eq["status"])}</span>
                    </div>
                    <div style="font-weight: 600; font-size: 1rem; margin-bottom: 0.25rem;">{html_escape(eq["name"])}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">{html_escape(eq["type"])}</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">📋 {html_escape(eq["specs"])}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### Equipment Utilization")

        eq_names = [eq["name"] for eq in equipment_data]
        import random
        utilization = [random.randint(40, 95) for _ in eq_names]

        fig_util = px.bar(
            x=utilization,
            y=eq_names,
            orientation="h",
            labels={"x": "Utilization (%)", "y": "Equipment"},
            color=utilization,
            color_continuous_scale=["#fbbf24", "#16a34a"],
        )
        fig_util.update_layout(
            height=350,
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", range=[0, 100]),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig_util, use_container_width=True)
