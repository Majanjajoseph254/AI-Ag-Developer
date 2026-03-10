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


def show_crop_improvement():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    hero_b64 = get_image_base64("assets/images/crop_tomato.png")
    if hero_b64:
        st.markdown(f"""
        <div style="position: relative; border-radius: 20px; overflow: hidden; margin-bottom: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
            <img src="data:image/png;base64,{hero_b64}" style="width: 100%; height: 220px; object-fit: cover; display: block;">
            <div style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(6,78,59,0.85) 0%, rgba(4,120,87,0.7) 50%, rgba(5,150,105,0.5) 100%); display: flex; flex-direction: column; justify-content: center; padding: 2rem 2.5rem;">
                <h1 style="color: white; font-family: 'Poppins', sans-serif; font-size: 1.8rem; margin: 0 0 0.25rem 0;">🌾 Crop Improvement</h1>
                <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin: 0;">Track variety trials, compare yields, and optimize your crop selection</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hero-section">
            <h1 style="color: white;">🌾 Crop Improvement</h1>
            <p>Track variety trials, compare yields, and optimize your crop selection</p>
        </div>
        """, unsafe_allow_html=True)

    trials = fetch_all(
        "SELECT * FROM crop_improvements WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )

    total_trials = len(trials) if trials else 0
    crop_types = len(set(t["crop_type"] for t in trials)) if trials else 0
    avg_yield = 0
    best_variety = "N/A"
    if trials:
        yields_with_area = [t for t in trials if t.get("yield_kg") and t.get("area_hectares") and float(t["area_hectares"]) > 0]
        if yields_with_area:
            avg_yield = sum(float(t["yield_kg"]) / float(t["area_hectares"]) for t in yields_with_area) / len(yields_with_area)
            best = max(yields_with_area, key=lambda t: float(t["yield_kg"]) / float(t["area_hectares"]))
            best_variety = best["variety_name"]

    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "🧪", total_trials, "Total Trials"),
        (c2, "🌿", crop_types, "Crop Types"),
        (c3, "📊", f"{avg_yield:.0f} kg/ha", "Avg Yield"),
        (c4, "🏆", html_escape(str(best_variety)), "Top Variety"),
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

    tab1, tab2, tab3, tab4 = st.tabs(["📝 Log Trial", "📊 Yield Comparison", "🌱 Seed Guide", "📚 Best Practices"])

    with tab1:
        st.markdown("#### Record a Variety Trial")
        with st.form("add_trial_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                variety_name = st.text_input("Variety Name", placeholder="e.g., DUMA 43")
                crop_type = st.selectbox("Crop Type", ["Maize", "Wheat", "Rice", "Tomato", "Potato", "Soybean", "Sorghum", "Millet", "Cassava", "Bean", "Other"])
                planting_date = st.date_input("Planting Date", value=date.today())
                harvest_date = st.date_input("Harvest Date (optional)", value=None)
                soil_type = st.selectbox("Soil Type", ["Loamy", "Clay", "Sandy", "Silt", "Peat", "Chalky", "Laterite"])
            with col_b:
                yield_kg = st.number_input("Yield (kg)", min_value=0.0, step=10.0)
                area_hectares = st.number_input("Area (hectares)", min_value=0.01, step=0.1, value=1.0)
                fertilizer = st.text_input("Fertilizer Used", placeholder="e.g., DAP, CAN, Manure")
                irrigation_method = st.selectbox("Irrigation Method", ["Rainfed", "Drip", "Sprinkler", "Flood", "Furrow", "Center Pivot"])
                notes = st.text_area("Notes", placeholder="Observations about this trial...")

            submitted = st.form_submit_button("Log Trial", use_container_width=True)
            if submitted:
                if not variety_name or not crop_type:
                    st.error("Please provide variety name and crop type.")
                else:
                    execute_query(
                        """INSERT INTO crop_improvements 
                        (user_id, variety_name, crop_type, planting_date, harvest_date, yield_kg, area_hectares, soil_type, fertilizer, irrigation_method, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (user_id, variety_name, crop_type, planting_date, harvest_date if harvest_date else None,
                         yield_kg if yield_kg > 0 else None, area_hectares, soil_type, fertilizer, irrigation_method, notes)
                    )
                    st.success(f"Trial for '{variety_name}' logged successfully!")
                    st.rerun()

        if trials:
            st.markdown("#### Trial History")
            for t in trials:
                v_name = html_escape(t["variety_name"])
                c_type = html_escape(t["crop_type"])
                s_type = html_escape(t.get("soil_type") or "N/A")
                irr = html_escape(t.get("irrigation_method") or "N/A")
                fert = html_escape(t.get("fertilizer") or "N/A")
                y_kg = f"{float(t['yield_kg']):.0f} kg" if t.get("yield_kg") else "Pending"
                area = f"{float(t['area_hectares']):.2f} ha" if t.get("area_hectares") else "N/A"
                p_date = t["planting_date"].strftime("%b %d, %Y") if t.get("planting_date") else "N/A"
                h_date = t["harvest_date"].strftime("%b %d, %Y") if t.get("harvest_date") else "Pending"
                trial_notes = html_escape(t.get("notes") or "")

                yield_per_ha = ""
                if t.get("yield_kg") and t.get("area_hectares") and float(t["area_hectares"]) > 0:
                    yph = float(t["yield_kg"]) / float(t["area_hectares"])
                    yield_per_ha = f" ({yph:.0f} kg/ha)"

                st.markdown(f"""
                <div class="modern-card" style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <h3 style="margin: 0 0 0.25rem 0;">🌾 {v_name} <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 400;">({c_type})</span></h3>
                            <div style="display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.85rem; color: var(--text-secondary);">
                                <span>📅 Planted: {p_date}</span>
                                <span>🗓️ Harvest: {h_date}</span>
                                <span>📐 Area: {area}</span>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-family: 'Poppins', sans-serif; font-size: 1.3rem; font-weight: 700; color: var(--primary-dark);">{y_kg}{yield_per_ha}</div>
                        </div>
                    </div>
                    <div style="margin-top: 0.75rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
                        <span style="background: var(--primary-100); color: var(--primary-dark); padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem;">🌍 {s_type}</span>
                        <span style="background: #dbeafe; color: #1e40af; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem;">💧 {irr}</span>
                        <span style="background: #fef3c7; color: #92400e; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem;">🧪 {fert}</span>
                    </div>
                    {"<div style='margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-secondary);'>📝 " + trial_notes + "</div>" if trial_notes else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No trials recorded yet. Use the form above to log your first variety trial.")

    with tab2:
        st.markdown("#### Yield Comparison Charts")
        if trials:
            yield_data = [t for t in trials if t.get("yield_kg") and t.get("area_hectares") and float(t["area_hectares"]) > 0]
            if yield_data:
                chart_data = []
                for t in yield_data:
                    chart_data.append({
                        "Variety": t["variety_name"],
                        "Crop": t["crop_type"],
                        "Yield (kg/ha)": float(t["yield_kg"]) / float(t["area_hectares"]),
                        "Total Yield (kg)": float(t["yield_kg"]),
                        "Area (ha)": float(t["area_hectares"]),
                    })

                fig = px.bar(
                    chart_data,
                    x="Variety",
                    y="Yield (kg/ha)",
                    color="Crop",
                    title="Yield per Hectare by Variety",
                    color_discrete_sequence=["#16a34a", "#0891b2", "#7c3aed", "#dc2626", "#f59e0b", "#059669"],
                )
                fig.update_layout(
                    height=400,
                    margin=dict(t=40, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
                )
                st.plotly_chart(fig, use_container_width=True)

                crop_groups = {}
                for t in yield_data:
                    crop = t["crop_type"]
                    yph = float(t["yield_kg"]) / float(t["area_hectares"])
                    if crop not in crop_groups:
                        crop_groups[crop] = []
                    crop_groups[crop].append({"variety": t["variety_name"], "yield_per_ha": yph})

                if len(crop_groups) > 0:
                    st.markdown("#### Yield by Crop Type")
                    for crop, varieties in crop_groups.items():
                        fig2 = px.bar(
                            varieties,
                            x="variety",
                            y="yield_per_ha",
                            title=f"{crop} - Variety Comparison",
                            color_discrete_sequence=["#16a34a"],
                            labels={"variety": "Variety", "yield_per_ha": "Yield (kg/ha)"},
                        )
                        fig2.update_layout(
                            height=300,
                            margin=dict(t=40, b=20, l=20, r=20),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter"),
                            showlegend=False,
                            xaxis=dict(showgrid=False),
                            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
                        )
                        st.plotly_chart(fig2, use_container_width=True)

                planting_data = [t for t in yield_data if t.get("planting_date")]
                if planting_data:
                    st.markdown("#### Historical Yield Analysis")
                    hist_data = []
                    for t in planting_data:
                        hist_data.append({
                            "Date": t["planting_date"],
                            "Variety": t["variety_name"],
                            "Yield (kg/ha)": float(t["yield_kg"]) / float(t["area_hectares"]),
                        })
                    fig3 = px.scatter(
                        hist_data,
                        x="Date",
                        y="Yield (kg/ha)",
                        color="Variety",
                        size="Yield (kg/ha)",
                        title="Yield Over Time",
                        color_discrete_sequence=["#16a34a", "#0891b2", "#7c3aed", "#dc2626", "#f59e0b"],
                    )
                    fig3.update_layout(
                        height=350,
                        margin=dict(t=40, b=20, l=20, r=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter"),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
                    )
                    st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No yield data available yet. Log trials with yield information to see comparisons.")
        else:
            st.info("No trials recorded yet. Log variety trials to see yield comparison charts.")

    with tab3:
        st.markdown("#### Seed Selection Guide")
        st.markdown("Use this reference to choose the best varieties for your conditions.")

        seed_database = {
            "Maize": [
                {"variety": "DUMA 43", "maturity": "120-130 days", "yield_potential": "8,000-10,000 kg/ha", "traits": "Drought tolerant, disease resistant", "best_for": "Lowland, medium altitude"},
                {"variety": "H614D", "maturity": "150-180 days", "yield_potential": "10,000-12,000 kg/ha", "traits": "High yield, good storage", "best_for": "Highland areas"},
                {"variety": "WH507", "maturity": "110-120 days", "yield_potential": "7,000-9,000 kg/ha", "traits": "Early maturing, drought escape", "best_for": "Semi-arid regions"},
                {"variety": "KH600-23A", "maturity": "135-150 days", "yield_potential": "9,000-11,000 kg/ha", "traits": "Stalk borer resistant", "best_for": "Medium to high altitude"},
            ],
            "Wheat": [
                {"variety": "Kenya Fahari", "maturity": "100-120 days", "yield_potential": "4,000-5,500 kg/ha", "traits": "Rust resistant, good baking quality", "best_for": "Highland areas"},
                {"variety": "Eagle 10", "maturity": "90-110 days", "yield_potential": "3,500-5,000 kg/ha", "traits": "Short stature, lodging resistant", "best_for": "Irrigated lowlands"},
                {"variety": "Kwale", "maturity": "95-105 days", "yield_potential": "3,000-4,500 kg/ha", "traits": "Heat tolerant, early maturing", "best_for": "Warm regions"},
            ],
            "Tomato": [
                {"variety": "Anna F1", "maturity": "65-75 days", "yield_potential": "40,000-60,000 kg/ha", "traits": "Bacterial wilt tolerant, determinate", "best_for": "Open field cultivation"},
                {"variety": "Rio Grande", "maturity": "75-80 days", "yield_potential": "30,000-45,000 kg/ha", "traits": "Processing type, firm fruit", "best_for": "Processing and fresh market"},
                {"variety": "Kilele F1", "maturity": "70-80 days", "yield_potential": "50,000-70,000 kg/ha", "traits": "High yield, virus tolerant", "best_for": "Greenhouse and open field"},
            ],
            "Rice": [
                {"variety": "Basmati 370", "maturity": "130-150 days", "yield_potential": "4,000-5,000 kg/ha", "traits": "Aromatic, long grain", "best_for": "Irrigated paddies"},
                {"variety": "NERICA 1", "maturity": "90-100 days", "yield_potential": "3,500-5,000 kg/ha", "traits": "Upland adapted, drought tolerant", "best_for": "Rainfed upland areas"},
                {"variety": "IR 2793", "maturity": "120-135 days", "yield_potential": "5,000-7,000 kg/ha", "traits": "High yield, flood tolerant", "best_for": "Lowland irrigated"},
            ],
            "Potato": [
                {"variety": "Shangi", "maturity": "90-120 days", "yield_potential": "25,000-40,000 kg/ha", "traits": "Early bulking, good taste", "best_for": "Fresh market"},
                {"variety": "Dutch Robijn", "maturity": "100-120 days", "yield_potential": "20,000-30,000 kg/ha", "traits": "Red skin, late blight tolerant", "best_for": "Highland areas"},
                {"variety": "Kenya Mpya", "maturity": "100-110 days", "yield_potential": "30,000-45,000 kg/ha", "traits": "High yield, processing quality", "best_for": "Processing (chips/crisps)"},
            ],
        }

        selected_crop = st.selectbox("Select Crop", list(seed_database.keys()), key="seed_guide_crop")
        varieties = seed_database[selected_crop]

        for v in varieties:
            v_name = html_escape(v["variety"])
            maturity = html_escape(v["maturity"])
            yp = html_escape(v["yield_potential"])
            traits = html_escape(v["traits"])
            best = html_escape(v["best_for"])

            st.markdown(f"""
            <div class="modern-card" style="margin-bottom: 1rem;">
                <h3 style="margin: 0 0 0.5rem 0;">🌱 {v_name}</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.9rem;">
                    <div><strong>⏱️ Maturity:</strong> {maturity}</div>
                    <div><strong>📊 Yield Potential:</strong> {yp}</div>
                    <div><strong>🧬 Key Traits:</strong> {traits}</div>
                    <div><strong>🌍 Best For:</strong> {best}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Improvement Recommendations")
        st.markdown("Get personalized variety recommendations based on your conditions.")

        with st.form("recommendation_form"):
            rc1, rc2 = st.columns(2)
            with rc1:
                rec_crop = st.selectbox("Crop Type", list(seed_database.keys()), key="rec_crop")
                rec_soil = st.selectbox("Soil Type", ["Loamy", "Clay", "Sandy", "Silt", "Laterite"], key="rec_soil")
            with rc2:
                rec_rainfall = st.selectbox("Annual Rainfall", ["< 500mm (Low)", "500-1000mm (Medium)", "1000-1500mm (High)", "> 1500mm (Very High)"], key="rec_rain")
                rec_altitude = st.selectbox("Altitude", ["Lowland (< 1000m)", "Medium (1000-1800m)", "Highland (> 1800m)"], key="rec_alt")

            rec_submit = st.form_submit_button("Get Recommendations", use_container_width=True)

        if rec_submit:
            st.markdown(f"""
            <div class="modern-card" style="border-left: 4px solid var(--primary);">
                <h3 style="margin: 0 0 0.75rem 0;">📋 Recommendations for {html_escape(rec_crop)}</h3>
                <div style="font-size: 0.9rem; line-height: 1.8;">
                    <p><strong>Soil ({html_escape(rec_soil)}):</strong> 
                    {"Well-suited for most varieties. Ensure good drainage." if rec_soil == "Loamy" else
                     "Improve drainage with organic matter. Choose waterlogging-tolerant varieties." if rec_soil == "Clay" else
                     "Add compost to improve water retention. Choose drought-tolerant varieties." if rec_soil == "Sandy" else
                     "Good moisture retention. Monitor for compaction." if rec_soil == "Silt" else
                     "Add lime to correct pH. Supplement with organic matter."}</p>
                    <p><strong>Rainfall ({html_escape(rec_rainfall)}):</strong>
                    {"Consider irrigation supplementation. Choose early-maturing, drought-tolerant varieties." if "Low" in rec_rainfall else
                     "Good range for most crops. Consider water harvesting during dry spells." if "Medium" in rec_rainfall else
                     "Adequate moisture. Focus on disease-resistant varieties (fungal pressure)." if "High" in rec_rainfall else
                     "Ensure good drainage. Choose varieties resistant to waterlogging and fungal diseases."}</p>
                    <p><strong>Altitude ({html_escape(rec_altitude)}):</strong>
                    {"Select heat-tolerant, early-maturing varieties." if "Lowland" in rec_altitude else
                     "Wide variety selection available. Balance maturity with altitude-specific pests." if "Medium" in rec_altitude else
                     "Choose cold-tolerant, longer-maturing varieties for higher yields."}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**Suggested Varieties:**")
            rec_varieties = seed_database.get(rec_crop, [])
            for v in rec_varieties:
                st.markdown(f"""
                <div class="activity-item">
                    <div class="activity-dot"></div>
                    <div>
                        <div style="font-weight: 500;">🌱 {html_escape(v['variety'])} — {html_escape(v['yield_potential'])}</div>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">{html_escape(v['traits'])} | Best for: {html_escape(v['best_for'])}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab4:
        st.markdown("#### Best Practices Library")

        practices = [
            {
                "title": "Crop Rotation",
                "icon": "🔄",
                "description": "Alternate crops each season to break pest cycles, improve soil health, and boost yields. Follow cereals with legumes to fix nitrogen naturally.",
                "tips": ["Rotate maize with beans or soybeans", "Avoid planting same family crops consecutively", "Include a cover crop in the rotation"],
            },
            {
                "title": "Integrated Pest Management",
                "icon": "🐛",
                "description": "Combine biological, cultural, and chemical methods to manage pests effectively while minimizing environmental impact.",
                "tips": ["Scout fields weekly for early detection", "Use resistant varieties as first line of defense", "Apply pesticides only when thresholds are exceeded"],
            },
            {
                "title": "Soil Health Management",
                "icon": "🌍",
                "description": "Maintain and improve soil fertility through organic matter addition, minimal tillage, and proper nutrient management.",
                "tips": ["Test soil every season before planting", "Apply compost or manure to build organic matter", "Minimize tillage to preserve soil structure"],
            },
            {
                "title": "Water Management",
                "icon": "💧",
                "description": "Optimize water use through efficient irrigation, rainwater harvesting, and soil moisture monitoring.",
                "tips": ["Use drip irrigation for 30-50% water savings", "Mulch to reduce evaporation by up to 70%", "Schedule irrigation based on soil moisture readings"],
            },
            {
                "title": "Seed Selection & Treatment",
                "icon": "🌱",
                "description": "Choose certified seed varieties suited to your conditions and treat seeds before planting to prevent early-season diseases.",
                "tips": ["Buy certified seeds from registered dealers", "Treat seeds with appropriate fungicides", "Match variety maturity to your growing season"],
            },
            {
                "title": "Post-Harvest Handling",
                "icon": "📦",
                "description": "Reduce losses through proper drying, storage, and handling to maximize the value of your harvest.",
                "tips": ["Dry grain to 13% moisture before storage", "Use hermetic storage bags to prevent insect damage", "Grade and sort produce before marketing"],
            },
        ]

        for i in range(0, len(practices), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(practices):
                    p = practices[i + j]
                    tips_html = "".join(f"<li>{html_escape(tip)}</li>" for tip in p["tips"])
                    with col:
                        st.markdown(f"""
                        <div class="modern-card" style="margin-bottom: 1rem; height: 100%;">
                            <h3 style="margin: 0 0 0.5rem 0;">{p['icon']} {html_escape(p['title'])}</h3>
                            <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.75rem;">{html_escape(p['description'])}</p>
                            <ul style="font-size: 0.85rem; color: var(--text-secondary); padding-left: 1.2rem; margin: 0;">
                                {tips_html}
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
