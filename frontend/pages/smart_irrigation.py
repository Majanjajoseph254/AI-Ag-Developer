import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
from datetime import datetime, date, timedelta
from html import escape as html_escape
from backend.db import fetch_all, fetch_one, execute_query, execute_returning


def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def show_smart_irrigation():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    hero_b64 = get_image_base64("assets/images/weather_station.png")
    if hero_b64:
        st.markdown(f"""
        <div style="position: relative; border-radius: 20px; overflow: hidden; margin-bottom: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
            <img src="data:image/png;base64,{hero_b64}" style="width: 100%; height: 220px; object-fit: cover; display: block;">
            <div style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(6,78,59,0.85) 0%, rgba(4,120,87,0.7) 50%, rgba(5,150,105,0.5) 100%); display: flex; flex-direction: column; justify-content: center; padding: 2rem 2.5rem;">
                <h1 style="color: white; font-family: 'Poppins', sans-serif; font-size: 1.8rem; margin: 0 0 0.25rem 0;">💧 Smart Irrigation</h1>
                <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin: 0;">Optimize water usage with intelligent irrigation scheduling and analytics</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hero-section">
            <h1 style="color: white;">💧 Smart Irrigation</h1>
            <p>Optimize water usage with intelligent irrigation scheduling and analytics</p>
        </div>
        """, unsafe_allow_html=True)

    schedules = fetch_all(
        "SELECT * FROM irrigation_schedules WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )

    active_count = sum(1 for s in schedules if s.get("is_active"))
    total_water = sum(float(s.get("water_per_session") or 0) for s in schedules if s.get("is_active"))
    total_area = sum(float(s.get("area_hectares") or 0) for s in schedules if s.get("is_active"))

    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "📋", len(schedules), "Total Schedules"),
        (c2, "✅", active_count, "Active Schedules"),
        (c3, "💧", f"{total_water:,.0f} L", "Water Per Cycle"),
        (c4, "🌾", f"{total_area:,.1f} ha", "Irrigated Area"),
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

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Schedule Manager",
        "📊 Water Analytics",
        "🌡️ Soil Moisture",
        "⚖️ Method Comparison",
        "💰 Water Budget"
    ])

    with tab1:
        st.markdown("#### Add Irrigation Schedule")
        with st.form("add_irrigation_schedule", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                crop_name = st.text_input("Crop Name", placeholder="e.g., Maize, Tomato")
                area = st.number_input("Area (hectares)", min_value=0.1, max_value=10000.0, value=1.0, step=0.5)
                method = st.selectbox("Irrigation Method", ["Drip", "Sprinkler", "Flood", "Furrow", "Center Pivot", "Sub-surface"])
            with col_b:
                frequency = st.selectbox("Frequency", ["Daily", "Every 2 Days", "Every 3 Days", "Weekly", "Bi-Weekly", "Monthly"])
                water_per_session = st.number_input("Water per Session (liters)", min_value=1.0, max_value=1000000.0, value=500.0, step=50.0)
                next_scheduled = st.date_input("Next Scheduled Date", value=date.today())

            submitted = st.form_submit_button("Add Schedule", use_container_width=True)
            if submitted and crop_name.strip():
                execute_query(
                    """INSERT INTO irrigation_schedules
                    (user_id, crop_name, area_hectares, method, frequency, water_per_session, next_scheduled, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)""",
                    (user_id, crop_name.strip(), area, method, frequency, water_per_session, next_scheduled)
                )
                st.success("Irrigation schedule added successfully!")
                st.rerun()
            elif submitted:
                st.warning("Please enter a crop name.")

        st.markdown("---")
        st.markdown("#### Current Schedules")

        if schedules:
            for s in schedules:
                status_color = "#16a34a" if s.get("is_active") else "#94a3b8"
                status_text = "Active" if s.get("is_active") else "Inactive"
                crop = html_escape(str(s.get("crop_name", "")))
                method_val = html_escape(str(s.get("method", "")))
                freq = html_escape(str(s.get("frequency", "")))
                area_val = s.get("area_hectares", 0)
                water_val = s.get("water_per_session", 0)
                next_date = s.get("next_scheduled")
                next_str = next_date.strftime("%b %d, %Y") if next_date else "Not set"

                st.markdown(f"""
                <div class="modern-card" style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <h3 style="margin: 0 0 0.25rem 0;">🌱 {crop}</h3>
                            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                                {method_val} &bull; {freq} &bull; {area_val} ha &bull; {water_val} L/session
                            </p>
                            <p style="margin: 0.25rem 0 0; font-size: 0.85rem; color: var(--text-muted);">Next: {next_str}</p>
                        </div>
                        <div style="display: inline-block; background: {status_color}; color: white; padding: 0.2rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                            {status_text}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_toggle, col_del = st.columns([1, 1])
                with col_toggle:
                    toggle_label = "Deactivate" if s.get("is_active") else "Activate"
                    if st.button(toggle_label, key=f"toggle_{s['id']}", use_container_width=True):
                        new_status = not s.get("is_active")
                        execute_query(
                            "UPDATE irrigation_schedules SET is_active = %s WHERE id = %s AND user_id = %s",
                            (new_status, s["id"], user_id)
                        )
                        st.rerun()
                with col_del:
                    if st.button("Delete", key=f"del_{s['id']}", use_container_width=True):
                        execute_query(
                            "DELETE FROM irrigation_schedules WHERE id = %s AND user_id = %s",
                            (s["id"], user_id)
                        )
                        st.rerun()
        else:
            st.info("No irrigation schedules yet. Add one above to get started.")

    with tab2:
        st.markdown("#### Water Usage Analytics")

        if schedules:
            active_schedules = [s for s in schedules if s.get("is_active")]
            if active_schedules:
                methods = {}
                for s in active_schedules:
                    m = s.get("method", "Unknown")
                    methods[m] = methods.get(m, 0) + float(s.get("water_per_session") or 0)

                fig_pie = px.pie(
                    values=list(methods.values()),
                    names=list(methods.keys()),
                    title="Water Distribution by Method",
                    color_discrete_sequence=["#0891b2", "#16a34a", "#2563eb", "#7c3aed", "#f59e0b", "#dc2626"],
                    hole=0.4,
                )
                fig_pie.update_layout(
                    height=350,
                    margin=dict(t=40, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                )
                st.plotly_chart(fig_pie, use_container_width=True)

                crops_water = {}
                for s in active_schedules:
                    c = s.get("crop_name", "Unknown")
                    crops_water[c] = crops_water.get(c, 0) + float(s.get("water_per_session") or 0)

                fig_bar = px.bar(
                    x=list(crops_water.keys()),
                    y=list(crops_water.values()),
                    title="Water Usage by Crop",
                    labels={"x": "Crop", "y": "Water (liters)"},
                    color_discrete_sequence=["#16a34a"],
                )
                fig_bar.update_layout(
                    height=350,
                    margin=dict(t=40, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
                )
                st.plotly_chart(fig_bar, use_container_width=True)

                efficiency_data = []
                for s in active_schedules:
                    area_val = float(s.get("area_hectares") or 1)
                    water_val = float(s.get("water_per_session") or 0)
                    efficiency_data.append({
                        "Crop": s.get("crop_name", "Unknown"),
                        "Method": s.get("method", "Unknown"),
                        "Water/ha (L)": round(water_val / area_val, 1),
                        "Area (ha)": area_val
                    })

                fig_eff = px.bar(
                    efficiency_data,
                    x="Crop",
                    y="Water/ha (L)",
                    color="Method",
                    title="Water Efficiency (Liters per Hectare)",
                    color_discrete_sequence=["#0891b2", "#16a34a", "#f59e0b", "#7c3aed", "#dc2626", "#2563eb"],
                )
                fig_eff.update_layout(
                    height=350,
                    margin=dict(t=40, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
                )
                st.plotly_chart(fig_eff, use_container_width=True)
            else:
                st.info("No active schedules to analyze. Activate a schedule to see analytics.")
        else:
            st.info("No schedules found. Add irrigation schedules to see water analytics.")

    with tab3:
        st.markdown("#### Soil Moisture Data")

        moisture_data = fetch_all(
            """SELECT ir.soil_moisture, ir.soil_temperature, ir.recorded_at, d.device_name, d.location
            FROM iot_readings ir
            JOIN iot_devices d ON ir.device_id = d.id
            WHERE d.user_id = %s AND ir.soil_moisture IS NOT NULL
            ORDER BY ir.recorded_at DESC LIMIT 100""",
            (user_id,)
        )

        if moisture_data:
            fig_moisture = go.Figure()
            devices = {}
            for r in moisture_data:
                dname = r.get("device_name", "Unknown")
                if dname not in devices:
                    devices[dname] = {"x": [], "y": []}
                devices[dname]["x"].append(r["recorded_at"])
                devices[dname]["y"].append(float(r["soil_moisture"]))

            colors = ["#16a34a", "#0891b2", "#f59e0b", "#7c3aed", "#dc2626"]
            for i, (dname, data) in enumerate(devices.items()):
                fig_moisture.add_trace(go.Scatter(
                    x=data["x"], y=data["y"],
                    mode="lines+markers",
                    name=dname,
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=5),
                ))

            fig_moisture.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Low Moisture Threshold")
            fig_moisture.add_hline(y=70, line_dash="dash", line_color="blue", annotation_text="High Moisture Threshold")

            fig_moisture.update_layout(
                title="Soil Moisture Over Time (%)",
                height=400,
                margin=dict(t=40, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
                xaxis=dict(showgrid=False, title="Time"),
                yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", title="Moisture (%)", range=[0, 100]),
            )
            st.plotly_chart(fig_moisture, use_container_width=True)

            latest = moisture_data[0]
            moisture_val = float(latest.get("soil_moisture", 0))
            if moisture_val < 30:
                st.warning(f"⚠️ Low soil moisture detected ({moisture_val}%) at {html_escape(str(latest.get('device_name', '')))}. Consider irrigating soon.")
            elif moisture_val > 70:
                st.info(f"💧 Soil moisture is high ({moisture_val}%) at {html_escape(str(latest.get('device_name', '')))}. You may delay irrigation.")
            else:
                st.success(f"✅ Soil moisture is optimal ({moisture_val}%) at {html_escape(str(latest.get('device_name', '')))}.")
        else:
            st.info("No soil moisture data available. Connect IoT sensors to monitor soil moisture in real-time.")

            st.markdown("""
            <div class="modern-card">
                <h3>🌡️ How Soil Moisture Integration Works</h3>
                <p style="color: var(--text-secondary);">
                    Smart Irrigation integrates with your IoT soil moisture sensors to provide real-time data.
                    Set up sensors in the IoT Dashboard to see moisture readings here.
                </p>
                <ul style="color: var(--text-secondary);">
                    <li>Below 30% — Irrigation recommended</li>
                    <li>30-70% — Optimal moisture range</li>
                    <li>Above 70% — Delay irrigation to prevent waterlogging</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown("#### Irrigation Method Comparison")

        comparison_data = [
            {
                "Method": "Drip",
                "Water Efficiency": 95,
                "Cost ($/ha)": 1200,
                "Labor": "Low",
                "Best For": "Row crops, orchards, vineyards",
                "Pros": "Highest efficiency, reduces weeds, works on slopes",
                "Cons": "High initial cost, clogging risk, maintenance needed"
            },
            {
                "Method": "Sprinkler",
                "Water Efficiency": 75,
                "Cost ($/ha)": 800,
                "Labor": "Medium",
                "Best For": "Grains, pastures, vegetables",
                "Pros": "Good coverage, versatile, moderate cost",
                "Cons": "Wind drift, evaporation losses, leaf wetness"
            },
            {
                "Method": "Flood",
                "Water Efficiency": 50,
                "Cost ($/ha)": 200,
                "Labor": "High",
                "Best For": "Rice paddies, leveled fields",
                "Pros": "Low cost, simple setup, no equipment needed",
                "Cons": "High water waste, uneven distribution, soil erosion"
            },
            {
                "Method": "Furrow",
                "Water Efficiency": 60,
                "Cost ($/ha)": 300,
                "Labor": "High",
                "Best For": "Row crops on gentle slopes",
                "Pros": "Low cost, no energy needed, simple",
                "Cons": "Uneven watering, labor intensive, water runoff"
            },
            {
                "Method": "Center Pivot",
                "Water Efficiency": 85,
                "Cost ($/ha)": 1500,
                "Labor": "Low",
                "Best For": "Large flat fields, grains",
                "Pros": "Large area coverage, automated, uniform",
                "Cons": "Very high cost, circular pattern wastes corners"
            },
            {
                "Method": "Sub-surface",
                "Water Efficiency": 98,
                "Cost ($/ha)": 2000,
                "Labor": "Low",
                "Best For": "High-value crops, permanent installations",
                "Pros": "Maximum efficiency, no evaporation, no runoff",
                "Cons": "Highest cost, difficult repair, root intrusion"
            },
        ]

        fig_comp = px.bar(
            comparison_data,
            x="Method",
            y="Water Efficiency",
            color="Method",
            title="Water Efficiency by Method (%)",
            color_discrete_sequence=["#16a34a", "#0891b2", "#f59e0b", "#7c3aed", "#2563eb", "#0d9488"],
        )
        fig_comp.update_layout(
            height=350,
            margin=dict(t=40, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", range=[0, 105]),
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        fig_cost = px.bar(
            comparison_data,
            x="Method",
            y="Cost ($/ha)",
            color="Method",
            title="Installation Cost per Hectare ($)",
            color_discrete_sequence=["#16a34a", "#0891b2", "#f59e0b", "#7c3aed", "#2563eb", "#0d9488"],
        )
        fig_cost.update_layout(
            height=350,
            margin=dict(t=40, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        )
        st.plotly_chart(fig_cost, use_container_width=True)

        st.markdown("#### Detailed Comparison")
        for item in comparison_data:
            eff = item["Water Efficiency"]
            eff_color = "#16a34a" if eff >= 85 else "#f59e0b" if eff >= 60 else "#dc2626"
            st.markdown(f"""
            <div class="modern-card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <h3 style="margin: 0 0 0.25rem 0;">{item['Method']} Irrigation</h3>
                        <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Best for: {item['Best For']}</p>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: {eff_color};">{eff}%</div>
                        <div style="font-size: 0.75rem; color: var(--text-muted);">Efficiency</div>
                    </div>
                </div>
                <div style="margin-top: 0.75rem; display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.85rem;">
                    <span style="color: var(--text-secondary);">💰 ${item['Cost ($/ha)']}/ha</span>
                    <span style="color: var(--text-secondary);">👷 Labor: {item['Labor']}</span>
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.85rem;">
                    <span style="color: #16a34a;">✅ {item['Pros']}</span><br>
                    <span style="color: #dc2626;">⚠️ {item['Cons']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab5:
        st.markdown("#### Water Budget Calculator")

        st.markdown("""
        <div class="modern-card" style="margin-bottom: 1.5rem;">
            <h3 style="margin: 0 0 0.5rem 0;">💰 Estimate Your Water Budget</h3>
            <p style="color: var(--text-secondary); margin: 0;">Calculate your total water needs and costs based on crop requirements and irrigation method.</p>
        </div>
        """, unsafe_allow_html=True)

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            budget_crop = st.selectbox("Select Crop", [
                "Maize", "Wheat", "Rice", "Tomato", "Potato",
                "Cotton", "Sugarcane", "Soybean", "Vegetables (General)"
            ], key="budget_crop")
            budget_area = st.number_input("Farm Area (hectares)", min_value=0.1, max_value=10000.0, value=5.0, step=0.5, key="budget_area")
            budget_method = st.selectbox("Irrigation Method", [
                "Drip", "Sprinkler", "Flood", "Furrow", "Center Pivot", "Sub-surface"
            ], key="budget_method")

        with col_w2:
            water_cost = st.number_input("Water Cost ($/1000 liters)", min_value=0.01, max_value=100.0, value=0.50, step=0.1, key="water_cost")
            growing_days = st.number_input("Growing Season (days)", min_value=30, max_value=365, value=120, step=10, key="growing_days")

        crop_water_needs = {
            "Maize": 500, "Wheat": 450, "Rice": 1200, "Tomato": 600,
            "Potato": 500, "Cotton": 700, "Sugarcane": 1500,
            "Soybean": 450, "Vegetables (General)": 400
        }

        method_efficiency = {
            "Drip": 0.95, "Sprinkler": 0.75, "Flood": 0.50,
            "Furrow": 0.60, "Center Pivot": 0.85, "Sub-surface": 0.98
        }

        crop_need_mm = crop_water_needs.get(budget_crop, 500)
        efficiency = method_efficiency.get(budget_method, 0.75)

        total_water_mm = crop_need_mm / efficiency
        total_water_liters = total_water_mm * budget_area * 10000 / 1000
        total_water_m3 = total_water_liters / 1000
        total_cost = (total_water_liters / 1000) * water_cost
        daily_water = total_water_liters / growing_days
        water_saved_vs_flood = max(0, (crop_need_mm / 0.50 - total_water_mm) * budget_area * 10000 / 1000)

        st.markdown("---")
        st.markdown("#### Budget Results")

        r1, r2, r3, r4 = st.columns(4)
        results = [
            (r1, "💧", f"{total_water_m3:,.0f} m³", "Total Water Needed"),
            (r2, "📅", f"{daily_water:,.0f} L/day", "Daily Usage"),
            (r3, "💰", f"${total_cost:,.2f}", "Total Water Cost"),
            (r4, "🌿", f"{water_saved_vs_flood:,.0f} L", "Saved vs Flood"),
        ]
        for col, icon, val, label in results:
            with col:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">{icon}</div>
                    <div class="stat-value" style="font-size: 1.4rem;">{val}</div>
                    <div class="stat-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        budget_breakdown = [
            {"Category": "Crop Water Need", "Value (mm)": crop_need_mm},
            {"Category": "Adjusted for Efficiency", "Value (mm)": round(total_water_mm, 1)},
            {"Category": f"Efficiency ({budget_method})", "Value (mm)": round(efficiency * 100, 1)},
        ]

        fig_budget = go.Figure(go.Waterfall(
            x=["Crop Need (mm)", f"Efficiency Loss ({budget_method})", "Total Required (mm)"],
            y=[crop_need_mm, round(total_water_mm - crop_need_mm, 1), 0],
            measure=["absolute", "relative", "total"],
            connector=dict(line=dict(color="#16a34a")),
            increasing=dict(marker=dict(color="#dc2626")),
            totals=dict(marker=dict(color="#0891b2")),
            decreasing=dict(marker=dict(color="#16a34a")),
        ))
        fig_budget.update_layout(
            title="Water Requirement Breakdown (mm per season)",
            height=350,
            margin=dict(t=40, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        )
        st.plotly_chart(fig_budget, use_container_width=True)

        st.markdown(f"""
        <div class="modern-card">
            <h3>📊 Budget Summary</h3>
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div>
                    <div style="font-weight: 500;">Crop: {html_escape(budget_crop)} | Area: {budget_area} ha</div>
                    <div style="font-size: 0.85rem; color: var(--text-muted);">Base water need: {crop_need_mm} mm/season</div>
                </div>
            </div>
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div>
                    <div style="font-weight: 500;">Method: {html_escape(budget_method)} ({efficiency*100:.0f}% efficient)</div>
                    <div style="font-size: 0.85rem; color: var(--text-muted);">Adjusted need: {total_water_mm:.0f} mm/season</div>
                </div>
            </div>
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div>
                    <div style="font-weight: 500;">Total: {total_water_m3:,.0f} m³ over {growing_days} days</div>
                    <div style="font-size: 0.85rem; color: var(--text-muted);">Estimated cost: ${total_cost:,.2f} at ${water_cost}/1000L</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
