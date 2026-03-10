import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
from datetime import datetime, date
from html import escape as html_escape
from backend.db import fetch_all, fetch_one, execute_query


def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def show_labour():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    hero_b64 = get_image_base64("assets/images/farmer_inspecting.png")
    if hero_b64:
        st.markdown(f"""
        <div style="position: relative; border-radius: 20px; overflow: hidden; margin-bottom: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
            <img src="data:image/png;base64,{hero_b64}" style="width: 100%; height: 220px; object-fit: cover; display: block;">
            <div style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(6,78,59,0.85) 0%, rgba(4,120,87,0.7) 50%, rgba(5,150,105,0.5) 100%); display: flex; flex-direction: column; justify-content: center; padding: 2rem 2.5rem;">
                <h1 style="color: white; font-family: 'Poppins', sans-serif; font-size: 1.8rem; margin: 0 0 0.25rem 0;">👷 Labour Management</h1>
                <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin: 0;">Assign tasks, track productivity, and manage your workforce efficiently</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hero-section">
            <h1 style="color: white;">👷 Labour Management</h1>
            <p>Assign tasks, track productivity, and manage your workforce efficiently</p>
        </div>
        """, unsafe_allow_html=True)

    all_tasks = fetch_all(
        "SELECT * FROM labour_tasks WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,),
    )

    total_tasks = len(all_tasks) if all_tasks else 0
    completed_tasks = len([t for t in all_tasks if t["status"] == "completed"]) if all_tasks else 0
    pending_tasks = len([t for t in all_tasks if t["status"] == "pending"]) if all_tasks else 0
    in_progress_tasks = len([t for t in all_tasks if t["status"] == "in-progress"]) if all_tasks else 0

    on_time = 0
    total_with_due = 0
    if all_tasks:
        for t in all_tasks:
            if t["status"] == "completed" and t.get("due_date"):
                total_with_due += 1
                completed_dt = t.get("completed_at")
                if completed_dt and completed_dt.date() <= t["due_date"]:
                    on_time += 1
                elif not completed_dt:
                    on_time += 1
    on_time_rate = round((on_time / total_with_due * 100), 1) if total_with_due > 0 else 100.0

    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "📋", total_tasks, "Total Tasks"),
        (c2, "✅", completed_tasks, "Completed"),
        (c3, "🔄", in_progress_tasks, "In Progress"),
        (c4, "🎯", f"{on_time_rate}%", "On-Time Rate"),
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

    tab1, tab2, tab3, tab4 = st.tabs(["📝 Assign Task", "📊 Task Board", "💰 Cost Calculator", "📈 Analytics"])

    with tab1:
        st.markdown("#### Create New Task Assignment")
        with st.form("labour_task_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                task_name = st.text_input("Task Name", placeholder="e.g., Harvest maize field A")
                worker_name = st.text_input("Worker Name", placeholder="e.g., John Doe")
                priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"])
            with col_b:
                status = st.selectbox("Status", ["pending", "in-progress", "completed"])
                due_date = st.date_input("Due Date", value=date.today())
                hours_worked = st.number_input("Hours Worked", min_value=0.0, step=0.5, value=0.0)

            col_c, col_d = st.columns(2)
            with col_c:
                hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, step=0.5, value=10.0)
            with col_d:
                notes = st.text_area("Notes", placeholder="Additional details about the task...")

            submitted = st.form_submit_button("➕ Assign Task", use_container_width=True)
            if submitted:
                if not task_name.strip():
                    st.error("Task name is required.")
                elif not worker_name.strip():
                    st.error("Worker name is required.")
                else:
                    completed_at = datetime.now() if status == "completed" else None
                    execute_query(
                        """INSERT INTO labour_tasks 
                        (user_id, task_name, worker_name, priority, status, due_date, completed_at, hours_worked, hourly_rate, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (user_id, task_name.strip(), worker_name.strip(), priority, status, due_date, completed_at, hours_worked, hourly_rate, notes.strip()),
                    )
                    st.success(f"Task '{html_escape(task_name.strip())}' assigned to {html_escape(worker_name.strip())}!")
                    st.rerun()

    with tab2:
        st.markdown("#### Task Board")

        board_cols = st.columns(3)
        status_groups = [
            ("⏳ Pending", "pending", pending_tasks),
            ("🔄 In Progress", "in-progress", in_progress_tasks),
            ("✅ Completed", "completed", completed_tasks),
        ]

        priority_colors = {
            "urgent": "#dc2626",
            "high": "#f97316",
            "medium": "#eab308",
            "low": "#22c55e",
        }

        for idx, (header, status_val, count) in enumerate(status_groups):
            with board_cols[idx]:
                st.markdown(f"**{header} ({count})**")
                st.markdown("---")
                status_tasks = [t for t in all_tasks if t["status"] == status_val] if all_tasks else []
                if status_tasks:
                    for t in status_tasks:
                        t_name = html_escape(t.get("task_name", ""))
                        w_name = html_escape(t.get("worker_name", ""))
                        p = t.get("priority", "medium")
                        p_color = priority_colors.get(p, "#eab308")
                        due = t.get("due_date")
                        due_str = due.strftime("%b %d") if due else "No due date"
                        hours = t.get("hours_worked") or 0
                        rate = t.get("hourly_rate") or 0
                        cost = float(hours) * float(rate)
                        st.markdown(f"""
                        <div class="modern-card" style="margin-bottom: 0.75rem; padding: 1rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong style="font-size: 0.95rem;">{t_name}</strong>
                                <span style="background: {p_color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">{html_escape(p)}</span>
                            </div>
                            <div style="font-size: 0.85rem; color: var(--text-secondary);">
                                👤 {w_name}<br>
                                📅 {due_str} &nbsp;|&nbsp; ⏱ {hours}h &nbsp;|&nbsp; 💰 ${cost:.2f}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"No {status_val} tasks.")

        if all_tasks:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Update Task Status")
            col_u1, col_u2, col_u3 = st.columns([2, 1, 1])
            task_options = {f"{t['task_name']} (#{t['id']})": t['id'] for t in all_tasks}
            with col_u1:
                selected_task = st.selectbox("Select Task", list(task_options.keys()), key="update_task_select")
            with col_u2:
                new_status = st.selectbox("New Status", ["pending", "in-progress", "completed"], key="update_status_select")
            with col_u3:
                update_hours = st.number_input("Update Hours", min_value=0.0, step=0.5, key="update_hours")
            if st.button("🔄 Update Task", use_container_width=True):
                task_id = task_options[selected_task]
                completed_at = datetime.now() if new_status == "completed" else None
                if update_hours > 0:
                    execute_query(
                        "UPDATE labour_tasks SET status = %s, completed_at = %s, hours_worked = %s WHERE id = %s AND user_id = %s",
                        (new_status, completed_at, update_hours, task_id, user_id),
                    )
                else:
                    execute_query(
                        "UPDATE labour_tasks SET status = %s, completed_at = %s WHERE id = %s AND user_id = %s",
                        (new_status, completed_at, task_id, user_id),
                    )
                st.success("Task updated successfully!")
                st.rerun()

    with tab3:
        st.markdown("#### Labor Cost Calculator")
        st.markdown("""
        <div class="modern-card" style="margin-bottom: 1.5rem;">
            <h3 style="margin-top: 0;">💰 Estimate Your Labor Costs</h3>
            <p style="color: var(--text-secondary);">Calculate total labor costs based on workers, hours, and pay rates.</p>
        </div>
        """, unsafe_allow_html=True)

        col_calc1, col_calc2 = st.columns(2)
        with col_calc1:
            num_workers = st.number_input("Number of Workers", min_value=1, step=1, value=5, key="calc_workers")
            hours_per_day = st.number_input("Hours per Day", min_value=1.0, step=0.5, value=8.0, key="calc_hours")
            rate_per_hour = st.number_input("Rate per Hour ($)", min_value=0.0, step=0.5, value=12.0, key="calc_rate")
        with col_calc2:
            num_days = st.number_input("Number of Days", min_value=1, step=1, value=5, key="calc_days")
            overtime_hours = st.number_input("Overtime Hours (per worker/day)", min_value=0.0, step=0.5, value=0.0, key="calc_overtime")
            overtime_multiplier = st.number_input("Overtime Multiplier", min_value=1.0, step=0.25, value=1.5, key="calc_ot_mult")

        daily_regular = num_workers * hours_per_day * rate_per_hour
        daily_overtime = num_workers * overtime_hours * rate_per_hour * overtime_multiplier
        daily_total = daily_regular + daily_overtime
        total_cost = daily_total * num_days

        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-value">${daily_regular:,.2f}</div>
                <div class="stat-label">Daily Regular</div>
            </div>
            """, unsafe_allow_html=True)
        with r2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">⏰</div>
                <div class="stat-value">${daily_overtime:,.2f}</div>
                <div class="stat-label">Daily Overtime</div>
            </div>
            """, unsafe_allow_html=True)
        with r3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">📅</div>
                <div class="stat-value">${daily_total:,.2f}</div>
                <div class="stat-label">Daily Total</div>
            </div>
            """, unsafe_allow_html=True)
        with r4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">💵</div>
                <div class="stat-value">${total_cost:,.2f}</div>
                <div class="stat-label">Grand Total</div>
            </div>
            """, unsafe_allow_html=True)

        if all_tasks:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Actual Labor Costs from Tasks")
            total_actual = sum(float(t.get("hours_worked") or 0) * float(t.get("hourly_rate") or 0) for t in all_tasks)
            total_hours = sum(float(t.get("hours_worked") or 0) for t in all_tasks)
            st.markdown(f"""
            <div class="modern-card">
                <div style="display: flex; justify-content: space-around; text-align: center;">
                    <div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: var(--primary-dark);">{total_hours:.1f}h</div>
                        <div style="color: var(--text-secondary); font-size: 0.85rem;">Total Hours Logged</div>
                    </div>
                    <div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: var(--primary-dark);">${total_actual:,.2f}</div>
                        <div style="color: var(--text-secondary); font-size: 0.85rem;">Total Labor Cost</div>
                    </div>
                    <div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: var(--primary-dark);">{len(set(t.get('worker_name','') for t in all_tasks))}</div>
                        <div style="color: var(--text-secondary); font-size: 0.85rem;">Unique Workers</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown("#### Workforce Analytics")

        if all_tasks and len(all_tasks) > 0:
            worker_stats = {}
            for t in all_tasks:
                w = t.get("worker_name", "Unknown")
                if w not in worker_stats:
                    worker_stats[w] = {"total": 0, "completed": 0, "hours": 0, "cost": 0}
                worker_stats[w]["total"] += 1
                if t["status"] == "completed":
                    worker_stats[w]["completed"] += 1
                worker_stats[w]["hours"] += float(t.get("hours_worked") or 0)
                worker_stats[w]["cost"] += float(t.get("hours_worked") or 0) * float(t.get("hourly_rate") or 0)

            col_ch1, col_ch2 = st.columns(2)

            with col_ch1:
                st.markdown("##### Tasks by Status")
                status_counts = {}
                for t in all_tasks:
                    s = t.get("status", "pending")
                    status_counts[s] = status_counts.get(s, 0) + 1
                fig = px.pie(
                    values=list(status_counts.values()),
                    names=list(status_counts.keys()),
                    color_discrete_sequence=["#f59e0b", "#3b82f6", "#16a34a", "#ef4444"],
                    hole=0.4,
                )
                fig.update_layout(
                    height=300,
                    margin=dict(t=20, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_ch2:
                st.markdown("##### Tasks by Priority")
                priority_counts = {}
                for t in all_tasks:
                    p = t.get("priority", "medium")
                    priority_counts[p] = priority_counts.get(p, 0) + 1
                fig = px.bar(
                    x=list(priority_counts.keys()),
                    y=list(priority_counts.values()),
                    color=list(priority_counts.keys()),
                    color_discrete_map=priority_colors,
                )
                fig.update_layout(
                    height=300,
                    margin=dict(t=20, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                    showlegend=False,
                    xaxis_title="Priority",
                    yaxis_title="Count",
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("##### Worker Performance")
            worker_names = list(worker_stats.keys())
            worker_completed = [worker_stats[w]["completed"] for w in worker_names]
            worker_total = [worker_stats[w]["total"] for w in worker_names]
            worker_hours = [worker_stats[w]["hours"] for w in worker_names]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Completed",
                x=worker_names,
                y=worker_completed,
                marker_color="#16a34a",
            ))
            fig.add_trace(go.Bar(
                name="Total Assigned",
                x=worker_names,
                y=worker_total,
                marker_color="#93c5fd",
            ))
            fig.update_layout(
                barmode="group",
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
                xaxis_title="Worker",
                yaxis_title="Tasks",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("##### Hours by Worker")
            fig_hours = px.bar(
                x=worker_names,
                y=worker_hours,
                color_discrete_sequence=["#0891b2"],
            )
            fig_hours.update_layout(
                height=300,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
                xaxis_title="Worker",
                yaxis_title="Hours",
            )
            st.plotly_chart(fig_hours, use_container_width=True)
        else:
            st.info("No task data available yet. Create tasks to see workforce analytics.")
