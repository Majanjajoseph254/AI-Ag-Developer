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


def show_sustainability():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    hero_b64 = get_image_base64("assets/images/farm_aerial.png")
    if hero_b64:
        st.markdown(f"""
        <div style="position: relative; border-radius: 20px; overflow: hidden; margin-bottom: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
            <img src="data:image/png;base64,{hero_b64}" style="width: 100%; height: 220px; object-fit: cover; display: block;">
            <div style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(6,78,59,0.85) 0%, rgba(4,120,87,0.7) 50%, rgba(5,150,105,0.5) 100%); display: flex; flex-direction: column; justify-content: center; padding: 2rem 2.5rem;">
                <h1 style="color: white; font-family: 'Poppins', sans-serif; font-size: 1.8rem; margin: 0 0 0.25rem 0;">🌍 Sustainability Dashboard</h1>
                <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin: 0;">Track your environmental impact and build a greener farm</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hero-section">
            <h1 style="color: white;">🌍 Sustainability Dashboard</h1>
            <p>Track your environmental impact and build a greener farm</p>
        </div>
        """, unsafe_allow_html=True)

    logs = fetch_all(
        "SELECT * FROM sustainability_logs WHERE user_id = %s ORDER BY logged_at DESC",
        (user_id,),
    )

    water_logs = [l for l in logs if l["category"] == "Water"]
    energy_logs = [l for l in logs if l["category"] == "Energy"]
    fertilizer_logs = [l for l in logs if l["category"] == "Fertilizer"]
    pesticide_logs = [l for l in logs if l["category"] == "Pesticide"]
    waste_logs = [l for l in logs if l["category"] == "Waste"]

    water_total = sum(float(l["value"]) for l in water_logs) if water_logs else 0
    energy_total = sum(float(l["value"]) for l in energy_logs) if energy_logs else 0
    fertilizer_total = sum(float(l["value"]) for l in fertilizer_logs) if fertilizer_logs else 0
    pesticide_total = sum(float(l["value"]) for l in pesticide_logs) if pesticide_logs else 0
    waste_total = sum(float(l["value"]) for l in waste_logs) if waste_logs else 0

    score = _calculate_impact_score(water_total, energy_total, fertilizer_total, pesticide_total, waste_total, len(logs))

    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "🌿", score, "Impact Score"),
        (c2, "💧", f"{water_total:.0f}", "Water (liters)"),
        (c3, "⚡", f"{energy_total:.0f}", "Energy (kWh)"),
        (c4, "📊", len(logs), "Total Logs"),
    ]
    for col, icon, val, label in stats:
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">{icon}</div>
                <div class="stat-value">{val}</div>
                <div class="stat-label">{html_escape(label)}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Log Resource",
        "📊 Resource Analytics",
        "🎯 Sustainability Goals",
        "🌱 Recommendations",
        "📋 Report",
    ])

    with tab1:
        _render_log_form(user_id)

    with tab2:
        _render_analytics(logs, water_total, energy_total, fertilizer_total, pesticide_total, waste_total)

    with tab3:
        _render_goals(water_total, energy_total, fertilizer_total, pesticide_total, waste_total)

    with tab4:
        _render_recommendations(water_total, energy_total, fertilizer_total, pesticide_total)

    with tab5:
        _render_report(logs, score, water_total, energy_total, fertilizer_total, pesticide_total, waste_total)


def _calculate_impact_score(water, energy, fertilizer, pesticide, waste, log_count):
    if log_count == 0:
        return 50

    score = 70

    if water > 0 and water < 5000:
        score += 8
    elif water > 10000:
        score -= 5

    if energy > 0 and energy < 500:
        score += 8
    elif energy > 2000:
        score -= 5

    if fertilizer > 0 and fertilizer < 200:
        score += 7
    elif fertilizer > 500:
        score -= 5

    if pesticide == 0 and log_count > 0:
        score += 10
    elif pesticide > 0 and pesticide < 50:
        score += 5
    elif pesticide > 100:
        score -= 8

    if waste > 0:
        score -= min(waste / 100, 10)

    if log_count >= 10:
        score += 5
    elif log_count >= 5:
        score += 3

    return max(0, min(100, int(score)))


def _render_log_form(user_id):
    st.markdown("#### Log Resource Usage")
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)

    with st.form("sustainability_log_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("Category", ["Water", "Energy", "Fertilizer", "Pesticide", "Waste"])
            value = st.number_input("Value", min_value=0.0, step=0.1)
        with col2:
            metric_name = st.text_input("Metric Name", placeholder="e.g., Irrigation water usage")
            unit = st.selectbox("Unit", ["liters", "kWh", "kg", "gallons", "tons", "units"])

        notes = st.text_area("Notes (optional)", placeholder="Additional details about this log entry")

        submitted = st.form_submit_button("Log Resource", use_container_width=True)
        if submitted:
            if not metric_name.strip():
                st.error("Please enter a metric name.")
            elif value <= 0:
                st.error("Please enter a value greater than 0.")
            else:
                try:
                    execute_query(
                        """INSERT INTO sustainability_logs (user_id, category, metric_name, value, unit, notes)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (user_id, category, metric_name.strip(), value, unit, notes.strip() if notes else None),
                    )
                    st.success("Resource usage logged successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error logging resource: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Recent Logs")

    recent_logs = fetch_all(
        "SELECT * FROM sustainability_logs WHERE user_id = %s ORDER BY logged_at DESC LIMIT 15",
        (user_id,),
    )

    if recent_logs:
        for log in recent_logs:
            cat_icons = {"Water": "💧", "Energy": "⚡", "Fertilizer": "🧪", "Pesticide": "🐛", "Waste": "🗑️"}
            icon = cat_icons.get(log["category"], "📊")
            metric = html_escape(str(log.get("metric_name", "")))
            cat = html_escape(str(log.get("category", "")))
            val = log.get("value", 0)
            unit = html_escape(str(log.get("unit", "")))
            log_date = log["logged_at"].strftime("%b %d, %Y at %H:%M") if log.get("logged_at") else ""
            notes_text = f" — {html_escape(str(log['notes']))}" if log.get("notes") else ""

            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div>
                    <div style="font-weight: 500;">{icon} {metric} ({cat}): {val} {unit}{notes_text}</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">{log_date}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No resource logs yet. Start logging your resource usage above.")


def _render_analytics(logs, water_total, energy_total, fertilizer_total, pesticide_total, waste_total):
    st.markdown("#### Resource Usage Breakdown")

    if not logs:
        st.info("No data available. Log some resource usage to see analytics.")
        return

    categories = []
    values = []
    if water_total > 0:
        categories.append("Water")
        values.append(water_total)
    if energy_total > 0:
        categories.append("Energy")
        values.append(energy_total)
    if fertilizer_total > 0:
        categories.append("Fertilizer")
        values.append(fertilizer_total)
    if pesticide_total > 0:
        categories.append("Pesticide")
        values.append(pesticide_total)
    if waste_total > 0:
        categories.append("Waste")
        values.append(waste_total)

    if categories:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                values=values,
                names=categories,
                color_discrete_sequence=["#0891b2", "#f59e0b", "#16a34a", "#dc2626", "#8b5cf6"],
                hole=0.4,
                title="Resource Distribution",
            )
            fig.update_layout(
                height=350,
                margin=dict(t=40, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                x=categories,
                y=values,
                color=categories,
                color_discrete_sequence=["#0891b2", "#f59e0b", "#16a34a", "#dc2626", "#8b5cf6"],
                title="Resource Totals",
            )
            fig.update_layout(
                height=350,
                margin=dict(t=40, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
                showlegend=False,
                xaxis_title="",
                yaxis_title="Total Value",
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Usage Over Time")

    dated_logs = [l for l in logs if l.get("logged_at")]
    if dated_logs:
        time_data = {}
        for l in dated_logs:
            d = l["logged_at"].strftime("%Y-%m-%d")
            cat = l["category"]
            if d not in time_data:
                time_data[d] = {}
            time_data[d][cat] = time_data[d].get(cat, 0) + float(l["value"])

        dates = sorted(time_data.keys())
        all_cats = list(set(l["category"] for l in dated_logs))
        cat_colors = {"Water": "#0891b2", "Energy": "#f59e0b", "Fertilizer": "#16a34a", "Pesticide": "#dc2626", "Waste": "#8b5cf6"}

        fig = go.Figure()
        for cat in all_cats:
            y_vals = [time_data[d].get(cat, 0) for d in dates]
            fig.add_trace(go.Scatter(
                x=dates,
                y=y_vals,
                mode="lines+markers",
                name=cat,
                line=dict(color=cat_colors.get(cat, "#64748b"), width=2),
                marker=dict(size=6),
            ))

        fig.update_layout(
            height=350,
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Biodiversity Index Calculator")
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        crop_varieties = st.number_input("Crop Varieties Grown", min_value=0, value=3, key="bio_crops")
    with col2:
        tree_species = st.number_input("Tree Species on Farm", min_value=0, value=2, key="bio_trees")
    with col3:
        beneficial_insects = st.selectbox("Beneficial Insect Presence", ["None", "Low", "Medium", "High"], index=2, key="bio_insects")

    insect_scores = {"None": 0, "Low": 5, "Medium": 15, "High": 25}
    biodiversity_index = min(100, crop_varieties * 8 + tree_species * 10 + insect_scores[beneficial_insects])

    color = "#16a34a" if biodiversity_index >= 60 else "#f59e0b" if biodiversity_index >= 30 else "#dc2626"
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem;">
        <div style="font-size: 3rem; font-weight: 700; color: {color}; font-family: 'Poppins', sans-serif;">{biodiversity_index}/100</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem;">Biodiversity Index Score</div>
        <div style="margin-top: 0.5rem; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden;">
            <div style="height: 100%; width: {biodiversity_index}%; background: {color}; border-radius: 4px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def _render_goals(water_total, energy_total, fertilizer_total, pesticide_total, waste_total):
    st.markdown("#### Sustainability Goals")
    st.markdown("Track your progress toward eco-friendly farming targets.")

    goals = [
        ("💧 Water Conservation", "Keep water usage below 5,000 liters/month", water_total, 5000, "liters"),
        ("⚡ Energy Efficiency", "Reduce energy usage below 500 kWh/month", energy_total, 500, "kWh"),
        ("🧪 Reduce Fertilizer", "Use less than 200 kg of fertilizer", fertilizer_total, 200, "kg"),
        ("🐛 Minimize Pesticides", "Keep pesticide usage under 50 kg", pesticide_total, 50, "kg"),
        ("🗑️ Waste Reduction", "Keep waste under 100 kg", waste_total, 100, "kg"),
    ]

    for title, desc, current, target, unit in goals:
        pct = min(100, (current / target * 100)) if target > 0 else 0
        remaining = max(0, target - current)

        if pct <= 70:
            bar_color = "#16a34a"
            status = "On Track"
        elif pct <= 100:
            bar_color = "#f59e0b"
            status = "Warning"
        else:
            bar_color = "#dc2626"
            status = "Exceeded"

        st.markdown(f"""
        <div class="modern-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div>
                    <div style="font-weight: 600; font-size: 1rem;">{title}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">{html_escape(desc)}</div>
                </div>
                <div style="background: {bar_color}15; color: {bar_color}; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                    {status}
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.25rem;">
                <span>{current:.0f} / {target} {html_escape(unit)}</span>
                <span>{pct:.0f}%</span>
            </div>
            <div style="height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden;">
                <div style="height: 100%; width: {min(pct, 100):.0f}%; background: {bar_color}; border-radius: 4px; transition: width 0.5s ease;"></div>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">
                {"✅ Goal met!" if pct <= 100 and current > 0 else f"⚠️ Exceeded by {current - target:.0f} {html_escape(unit)}" if pct > 100 else f"Remaining: {remaining:.0f} {html_escape(unit)}"}
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_recommendations(water, energy, fertilizer, pesticide):
    st.markdown("#### Eco-Friendly Practice Recommendations")

    recommendations = [
        {
            "icon": "💧",
            "title": "Water Conservation",
            "practices": [
                "Install drip irrigation to reduce water waste by up to 60%",
                "Mulch around crops to retain soil moisture",
                "Collect rainwater for irrigation use",
                "Schedule irrigation during early morning or evening to reduce evaporation",
                "Use soil moisture sensors to optimize watering schedules",
            ],
            "priority": "high" if water > 5000 else "medium" if water > 2000 else "low",
        },
        {
            "icon": "⚡",
            "title": "Energy Efficiency",
            "practices": [
                "Switch to solar-powered irrigation pumps",
                "Use energy-efficient LED grow lights",
                "Optimize equipment usage schedules to reduce peak energy consumption",
                "Insulate storage facilities to reduce cooling/heating energy",
                "Consider wind turbines for farm energy needs",
            ],
            "priority": "high" if energy > 2000 else "medium" if energy > 500 else "low",
        },
        {
            "icon": "🌿",
            "title": "Organic Farming",
            "practices": [
                "Use compost and green manure instead of synthetic fertilizers",
                "Practice crop rotation to maintain soil fertility naturally",
                "Introduce beneficial insects for natural pest control",
                "Use neem-based or organic pesticides",
                "Plant cover crops to improve soil health",
            ],
            "priority": "high" if fertilizer > 200 or pesticide > 50 else "medium",
        },
        {
            "icon": "🌳",
            "title": "Agroforestry & Biodiversity",
            "practices": [
                "Plant native trees along field boundaries",
                "Create hedgerows to support wildlife corridors",
                "Integrate fruit trees with crop fields",
                "Maintain wildflower strips for pollinators",
                "Establish buffer zones near water bodies",
            ],
            "priority": "medium",
        },
        {
            "icon": "♻️",
            "title": "Waste Management",
            "practices": [
                "Compost crop residues and organic waste",
                "Recycle plastic packaging and containers",
                "Convert animal waste into biogas",
                "Use biodegradable mulch films",
                "Repurpose agricultural byproducts",
            ],
            "priority": "medium",
        },
    ]

    priority_colors = {"high": "#dc2626", "medium": "#f59e0b", "low": "#16a34a"}
    priority_labels = {"high": "High Priority", "medium": "Medium Priority", "low": "Low Priority"}

    for rec in recommendations:
        p_color = priority_colors[rec["priority"]]
        p_label = priority_labels[rec["priority"]]
        practices_html = "".join(
            f'<div class="activity-item"><div class="activity-dot"></div><div style="font-size: 0.9rem;">{html_escape(p)}</div></div>'
            for p in rec["practices"]
        )

        st.markdown(f"""
        <div class="modern-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <div style="font-weight: 600; font-size: 1.05rem;">{rec["icon"]} {html_escape(rec["title"])}</div>
                <div style="background: {p_color}15; color: {p_color}; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">
                    {p_label}
                </div>
            </div>
            {practices_html}
        </div>
        """, unsafe_allow_html=True)


def _render_report(logs, score, water, energy, fertilizer, pesticide, waste):
    st.markdown("#### Sustainability Report")

    if not logs:
        st.info("No data available to generate a report. Start logging resource usage first.")
        return

    today = date.today().strftime("%B %d, %Y")
    total_entries = len(logs)
    categories_used = len(set(l["category"] for l in logs))

    if score >= 80:
        grade = "A"
        grade_color = "#16a34a"
        summary_text = "Excellent sustainability practices! Your farm is a model for eco-friendly agriculture."
    elif score >= 60:
        grade = "B"
        grade_color = "#059669"
        summary_text = "Good sustainability performance. There are opportunities for further improvement."
    elif score >= 40:
        grade = "C"
        grade_color = "#f59e0b"
        summary_text = "Average sustainability. Consider implementing more eco-friendly practices."
    else:
        grade = "D"
        grade_color = "#dc2626"
        summary_text = "Sustainability needs improvement. Focus on reducing resource consumption."

    st.markdown(f"""
    <div class="modern-card" style="margin-bottom: 1.5rem;">
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 0.85rem; color: var(--text-secondary);">Report Generated: {html_escape(today)}</div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; margin: 1.5rem 0;">
                <div>
                    <div style="font-size: 4rem; font-weight: 800; color: {grade_color}; font-family: 'Poppins', sans-serif;">{grade}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">Overall Grade</div>
                </div>
                <div>
                    <div style="font-size: 3rem; font-weight: 700; color: var(--primary-dark); font-family: 'Poppins', sans-serif;">{score}/100</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">Impact Score</div>
                </div>
            </div>
            <div style="font-size: 0.95rem; color: var(--text-secondary); max-width: 500px; margin: 0 auto;">{html_escape(summary_text)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="modern-card">
            <h3 style="margin-bottom: 1rem;">📊 Resource Summary</h3>
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div><span style="font-weight: 500;">💧 Water:</span> {water:.0f} liters</div>
            </div>
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div><span style="font-weight: 500;">⚡ Energy:</span> {energy:.0f} kWh</div>
            </div>
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div><span style="font-weight: 500;">🧪 Fertilizer:</span> {fertilizer:.0f} kg</div>
            </div>
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div><span style="font-weight: 500;">🐛 Pesticide:</span> {pesticide:.0f} kg</div>
            </div>
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div><span style="font-weight: 500;">🗑️ Waste:</span> {waste:.0f} kg</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="modern-card">
            <h3 style="margin-bottom: 1rem;">📈 Statistics</h3>
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div><span style="font-weight: 500;">Total Log Entries:</span> {total_entries}</div>
            </div>
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div><span style="font-weight: 500;">Categories Tracked:</span> {categories_used}</div>
            </div>
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div><span style="font-weight: 500;">Impact Score:</span> {score}/100</div>
            </div>
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div><span style="font-weight: 500;">Grade:</span> {grade}</div>
            </div>
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div><span style="font-weight: 500;">Status:</span> {"🟢 Active" if total_entries > 0 else "⚪ No data"}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
