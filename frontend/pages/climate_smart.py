import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
from html import escape as html_escape


def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def show_climate_smart():
    user = st.session_state.get("user", {})
    name = html_escape(user.get("name", "Farmer"))

    hero_b64 = get_image_base64("assets/images/hero_banner.png")
    if hero_b64:
        st.markdown(f"""
        <div style="position: relative; border-radius: 20px; overflow: hidden; margin-bottom: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
            <img src="data:image/png;base64,{hero_b64}" style="width: 100%; height: 220px; object-fit: cover; display: block;">
            <div style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(6,78,59,0.85) 0%, rgba(4,120,87,0.7) 50%, rgba(5,150,105,0.5) 100%); display: flex; flex-direction: column; justify-content: center; padding: 2rem 2.5rem;">
                <h1 style="color: white; font-family: 'Poppins', sans-serif; font-size: 1.8rem; margin: 0 0 0.25rem 0;">🌍 Climate-Smart Practices</h1>
                <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin: 0;">Tools and guidance for sustainable, climate-resilient farming</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hero-section">
            <h1 style="color: white;">🌍 Climate-Smart Practices</h1>
            <p>Tools and guidance for sustainable, climate-resilient farming</p>
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧮 Carbon Calculator",
        "🌾 Recommendations",
        "📅 Seasonal Calendar",
        "💧 Water Conservation",
        "🌳 Agroforestry"
    ])

    with tab1:
        _render_carbon_calculator()

    with tab2:
        _render_recommendations()

    with tab3:
        _render_seasonal_calendar()

    with tab4:
        _render_water_conservation()

    with tab5:
        _render_agroforestry()


def _render_carbon_calculator():
    st.markdown("#### Carbon Footprint Calculator")
    st.markdown("""
    <div class="modern-card" style="margin-bottom: 1.5rem;">
        <p style="margin: 0;">Estimate your farm's annual carbon emissions based on key inputs. Understanding your footprint is the first step toward reducing it.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        farm_size = st.number_input("Farm Size (hectares)", min_value=0.1, max_value=10000.0, value=10.0, step=0.5, key="cs_farm_size")
        livestock_count = st.number_input("Number of Livestock", min_value=0, max_value=50000, value=20, step=1, key="cs_livestock")
        livestock_type = st.selectbox("Livestock Type", ["Cattle", "Sheep/Goats", "Poultry", "Pigs", "None"], key="cs_livestock_type")

    with col2:
        fertilizer_kg = st.number_input("Synthetic Fertilizer Used (kg/year)", min_value=0.0, max_value=100000.0, value=500.0, step=10.0, key="cs_fertilizer")
        fuel_liters = st.number_input("Fuel Consumption (liters/year)", min_value=0.0, max_value=100000.0, value=1000.0, step=50.0, key="cs_fuel")
        electricity_kwh = st.number_input("Electricity Usage (kWh/year)", min_value=0.0, max_value=500000.0, value=5000.0, step=100.0, key="cs_electricity")

    if st.button("Calculate Carbon Footprint", type="primary", key="cs_calc_btn"):
        livestock_factors = {
            "Cattle": 2.3,
            "Sheep/Goats": 0.5,
            "Poultry": 0.02,
            "Pigs": 0.7,
            "None": 0.0,
        }
        livestock_emissions = livestock_count * livestock_factors.get(livestock_type, 0) 
        fertilizer_emissions = fertilizer_kg * 0.00566
        fuel_emissions = fuel_liters * 0.00268
        electricity_emissions = electricity_kwh * 0.000233
        land_use_emissions = farm_size * 0.5

        total_emissions = livestock_emissions + fertilizer_emissions + fuel_emissions + electricity_emissions + land_use_emissions

        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        results = [
            (c1, "🐄", f"{livestock_emissions:.2f}", "Livestock (t CO₂e)"),
            (c2, "🧪", f"{fertilizer_emissions:.2f}", "Fertilizer (t CO₂e)"),
            (c3, "⛽", f"{fuel_emissions:.2f}", "Fuel (t CO₂e)"),
            (c4, "⚡", f"{electricity_emissions:.2f}", "Electricity (t CO₂e)"),
        ]
        for col, icon, val, label in results:
            with col:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">{icon}</div>
                    <div class="stat-value">{html_escape(str(val))}</div>
                    <div class="stat-label">{html_escape(label)}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="modern-card" style="text-align: center; border-left: 4px solid var(--primary);">
            <div style="font-size: 0.9rem; color: var(--text-secondary);">Total Estimated Annual Emissions</div>
            <div style="font-family: 'Poppins', sans-serif; font-size: 2.5rem; font-weight: 700; color: var(--primary-dark);">{total_emissions:.2f}</div>
            <div style="font-size: 0.9rem; color: var(--text-secondary);">tonnes CO₂ equivalent per year</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        categories = ["Livestock", "Fertilizer", "Fuel", "Electricity", "Land Use"]
        values = [livestock_emissions, fertilizer_emissions, fuel_emissions, electricity_emissions, land_use_emissions]

        fig = px.pie(
            values=values,
            names=categories,
            color_discrete_sequence=["#dc2626", "#f59e0b", "#3b82f6", "#8b5cf6", "#16a34a"],
            hole=0.45,
            title="Emissions Breakdown",
        )
        fig.update_layout(
            height=400,
            margin=dict(t=40, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15),
        )
        st.plotly_chart(fig, use_container_width=True)

        fig_bar = px.bar(
            x=categories,
            y=values,
            color=categories,
            color_discrete_sequence=["#dc2626", "#f59e0b", "#3b82f6", "#8b5cf6", "#16a34a"],
            title="Emissions by Category",
            labels={"x": "Category", "y": "Tonnes CO₂e"},
        )
        fig_bar.update_layout(
            height=350,
            margin=dict(t=40, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        per_hectare = total_emissions / farm_size if farm_size > 0 else 0
        if per_hectare < 2:
            rating = "Excellent"
            color = "#16a34a"
        elif per_hectare < 5:
            rating = "Good"
            color = "#f59e0b"
        elif per_hectare < 10:
            rating = "Average"
            color = "#f97316"
        else:
            rating = "High"
            color = "#dc2626"

        st.markdown(f"""
        <div class="modern-card" style="border-left: 4px solid {color};">
            <h3 style="margin-top: 0;">Farm Rating: <span style="color: {color};">{rating}</span></h3>
            <p style="margin: 0;">Your per-hectare emissions: <strong>{per_hectare:.2f} t CO₂e/ha</strong>. 
            {"Great job! Your farm has low emissions." if per_hectare < 2 else "Consider the recommendations tab for ways to reduce emissions." if per_hectare < 5 else "Review the recommendations and agroforestry tabs for emission reduction strategies."}</p>
        </div>
        """, unsafe_allow_html=True)


def _render_recommendations():
    st.markdown("#### Climate-Adaptive Farming Recommendations")

    region = st.selectbox("Select Your Region", [
        "Tropical",
        "Subtropical",
        "Temperate",
        "Arid/Semi-Arid",
        "Mediterranean",
        "Highland/Montane"
    ], key="cs_region")

    recommendations = {
        "Tropical": {
            "crops": ["Rice (flood-tolerant varieties)", "Cassava", "Sweet Potato", "Plantain", "Cocoa", "Oil Palm"],
            "practices": [
                "Use agroforestry systems to provide shade and reduce soil temperature",
                "Implement integrated pest management to reduce chemical inputs",
                "Practice mulching to conserve soil moisture and reduce evaporation",
                "Adopt System of Rice Intensification (SRI) for paddy fields",
                "Use cover crops during fallow periods to prevent erosion",
                "Install rainwater harvesting systems for dry spells",
            ],
            "icon": "🌴",
        },
        "Subtropical": {
            "crops": ["Citrus Fruits", "Sugarcane", "Cotton", "Tea", "Mango", "Avocado"],
            "practices": [
                "Use drip irrigation to optimize water use efficiency",
                "Implement conservation tillage to preserve soil carbon",
                "Plant windbreaks to reduce crop damage from strong winds",
                "Adopt crop rotation with nitrogen-fixing legumes",
                "Use organic mulches to maintain soil moisture",
                "Practice intercropping for biodiversity and risk mitigation",
            ],
            "icon": "🍊",
        },
        "Temperate": {
            "crops": ["Wheat", "Barley", "Potatoes", "Apples", "Grapes", "Soybeans"],
            "practices": [
                "Use no-till or minimum tillage to build soil organic matter",
                "Implement crop rotation with at least 3 different crop families",
                "Plant cover crops over winter to prevent nutrient leaching",
                "Use precision agriculture tools for optimized input application",
                "Establish hedgerows for biodiversity and carbon sequestration",
                "Practice integrated nutrient management with soil testing",
            ],
            "icon": "🌾",
        },
        "Arid/Semi-Arid": {
            "crops": ["Sorghum", "Millet", "Dates", "Drought-tolerant Maize", "Chickpeas", "Jojoba"],
            "practices": [
                "Use drought-resistant crop varieties and landraces",
                "Implement water harvesting techniques (zai pits, half-moons)",
                "Practice conservation agriculture with permanent soil cover",
                "Use deficit irrigation strategies to maximize water productivity",
                "Build stone bunds and terraces to capture runoff",
                "Establish community seed banks with drought-tolerant varieties",
            ],
            "icon": "🏜️",
        },
        "Mediterranean": {
            "crops": ["Olives", "Grapes", "Almonds", "Tomatoes", "Wheat", "Lavender"],
            "practices": [
                "Use regulated deficit irrigation for tree crops",
                "Implement fire-resistant agroforestry designs",
                "Practice dry farming techniques where possible",
                "Use reflective mulches to reduce soil temperature",
                "Plant drought-adapted cover crop species",
                "Implement integrated water resource management",
            ],
            "icon": "🫒",
        },
        "Highland/Montane": {
            "crops": ["Potatoes", "Quinoa", "Barley", "Coffee (Arabica)", "Tea", "Temperate Fruits"],
            "practices": [
                "Build terraces to prevent soil erosion on slopes",
                "Use contour farming to reduce water runoff",
                "Implement silvopasture systems for livestock areas",
                "Plant cold-resistant windbreak species",
                "Use raised beds for improved drainage",
                "Practice composting to improve thin mountain soils",
            ],
            "icon": "🏔️",
        },
    }

    rec = recommendations[region]

    st.markdown(f"""
    <div class="modern-card" style="border-left: 4px solid var(--primary); margin-bottom: 1.5rem;">
        <h3 style="margin-top: 0;">{html_escape(rec["icon"])} {html_escape(region)} Region Recommendations</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 🌱 Recommended Climate-Smart Crops")
        for crop in rec["crops"]:
            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div style="font-weight: 500;">{html_escape(crop)}</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("##### 🛠️ Best Practices")
        for practice in rec["practices"]:
            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div>{html_escape(practice)}</div>
            </div>
            """, unsafe_allow_html=True)


def _render_seasonal_calendar():
    st.markdown("#### Seasonal Planting Calendar")
    st.markdown("""
    <div class="modern-card" style="margin-bottom: 1.5rem;">
        <p style="margin: 0;">Plan your planting schedule with climate-smart timing. This calendar shows optimal planting and harvesting windows for common crops.</p>
    </div>
    """, unsafe_allow_html=True)

    climate_zone = st.selectbox("Select Climate Zone", [
        "Northern Hemisphere Temperate",
        "Southern Hemisphere Temperate",
        "Tropical Wet",
        "Tropical Dry",
    ], key="cs_climate_zone")

    calendars = {
        "Northern Hemisphere Temperate": [
            {"crop": "Wheat (Winter)", "plant": "Sep-Oct", "harvest": "Jun-Jul", "months": [0,0,0,0,0,1,1,0,2,2,0,0]},
            {"crop": "Wheat (Spring)", "plant": "Mar-Apr", "harvest": "Aug-Sep", "months": [0,0,2,2,0,0,0,1,1,0,0,0]},
            {"crop": "Maize/Corn", "plant": "Apr-May", "harvest": "Sep-Oct", "months": [0,0,0,2,2,0,0,0,1,1,0,0]},
            {"crop": "Potatoes", "plant": "Mar-Apr", "harvest": "Jul-Sep", "months": [0,0,2,2,0,0,1,1,1,0,0,0]},
            {"crop": "Soybeans", "plant": "May-Jun", "harvest": "Sep-Oct", "months": [0,0,0,0,2,2,0,0,1,1,0,0]},
            {"crop": "Tomatoes", "plant": "Apr-May", "harvest": "Jul-Sep", "months": [0,0,0,2,2,0,1,1,1,0,0,0]},
            {"crop": "Cover Crops", "plant": "Sep-Oct", "harvest": "Mar-Apr", "months": [3,3,3,1,0,0,0,0,2,2,3,3]},
        ],
        "Southern Hemisphere Temperate": [
            {"crop": "Wheat (Winter)", "plant": "Apr-May", "harvest": "Nov-Dec", "months": [0,0,0,2,2,0,0,0,0,0,1,1]},
            {"crop": "Wheat (Spring)", "plant": "Aug-Sep", "harvest": "Jan-Feb", "months": [1,1,0,0,0,0,0,2,2,0,0,0]},
            {"crop": "Maize/Corn", "plant": "Oct-Nov", "harvest": "Mar-Apr", "months": [0,0,1,1,0,0,0,0,0,2,2,0]},
            {"crop": "Potatoes", "plant": "Sep-Oct", "harvest": "Jan-Mar", "months": [1,1,1,0,0,0,0,0,2,2,0,0]},
            {"crop": "Soybeans", "plant": "Nov-Dec", "harvest": "Apr-May", "months": [0,0,0,1,1,0,0,0,0,0,2,2]},
            {"crop": "Tomatoes", "plant": "Oct-Nov", "harvest": "Jan-Mar", "months": [1,1,1,0,0,0,0,0,0,2,2,0]},
        ],
        "Tropical Wet": [
            {"crop": "Rice (Main)", "plant": "Jun-Jul", "harvest": "Oct-Nov", "months": [0,0,0,0,0,2,2,0,0,1,1,0]},
            {"crop": "Rice (Second)", "plant": "Nov-Dec", "harvest": "Mar-Apr", "months": [0,0,1,1,0,0,0,0,0,0,2,2]},
            {"crop": "Cassava", "plant": "Mar-Apr", "harvest": "Dec-Feb", "months": [1,1,2,2,0,0,0,0,0,0,0,1]},
            {"crop": "Maize", "plant": "Mar-Apr", "harvest": "Jul-Aug", "months": [0,0,2,2,0,0,1,1,0,0,0,0]},
            {"crop": "Sweet Potato", "plant": "Apr-May", "harvest": "Aug-Oct", "months": [0,0,0,2,2,0,0,1,1,1,0,0]},
        ],
        "Tropical Dry": [
            {"crop": "Sorghum", "plant": "Jun-Jul", "harvest": "Oct-Nov", "months": [0,0,0,0,0,2,2,0,0,1,1,0]},
            {"crop": "Millet", "plant": "Jun-Jul", "harvest": "Sep-Oct", "months": [0,0,0,0,0,2,2,0,1,1,0,0]},
            {"crop": "Groundnuts", "plant": "Jun-Jul", "harvest": "Oct-Nov", "months": [0,0,0,0,0,2,2,0,0,1,1,0]},
            {"crop": "Cowpeas", "plant": "Jul-Aug", "harvest": "Oct-Nov", "months": [0,0,0,0,0,0,2,2,0,1,1,0]},
            {"crop": "Maize", "plant": "May-Jun", "harvest": "Sep-Oct", "months": [0,0,0,0,2,2,0,0,1,1,0,0]},
        ],
    }

    cal_data = calendars[climate_zone]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    crops = [c["crop"] for c in cal_data]
    z_values = [c["months"] for c in cal_data]

    color_map = {0: "#f8faf9", 1: "#16a34a", 2: "#3b82f6", 3: "#f59e0b"}
    custom_colorscale = [
        [0.0, "#f1f5f9"],
        [0.33, "#3b82f6"],
        [0.66, "#16a34a"],
        [1.0, "#f59e0b"],
    ]

    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=months,
        y=crops,
        colorscale=custom_colorscale,
        showscale=False,
        hovertemplate="Crop: %{y}<br>Month: %{x}<br><extra></extra>",
    ))

    fig.update_layout(
        height=max(250, len(crops) * 50 + 100),
        margin=dict(t=20, b=20, l=150, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        xaxis=dict(side="top"),
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="stat-card">
            <div style="width: 20px; height: 20px; background: #3b82f6; border-radius: 4px; display: inline-block; vertical-align: middle;"></div>
            <span style="margin-left: 0.5rem; font-weight: 500;">Planting Window</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="stat-card">
            <div style="width: 20px; height: 20px; background: #16a34a; border-radius: 4px; display: inline-block; vertical-align: middle;"></div>
            <span style="margin-left: 0.5rem; font-weight: 500;">Harvest Window</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="stat-card">
            <div style="width: 20px; height: 20px; background: #f59e0b; border-radius: 4px; display: inline-block; vertical-align: middle;"></div>
            <span style="margin-left: 0.5rem; font-weight: 500;">Growing Period</span>
        </div>
        """, unsafe_allow_html=True)


def _render_water_conservation():
    st.markdown("#### Water Conservation Tips & Strategies")

    strategies = [
        {
            "title": "Drip Irrigation",
            "icon": "💧",
            "savings": "30-60%",
            "description": "Delivers water directly to plant roots through a network of tubes and emitters. Minimizes evaporation and runoff.",
            "tips": [
                "Use pressure-compensating emitters for uneven terrain",
                "Install filters to prevent clogging",
                "Schedule irrigation during early morning or evening",
                "Monitor soil moisture to avoid over-watering",
            ],
        },
        {
            "title": "Mulching",
            "icon": "🍂",
            "savings": "20-35%",
            "description": "Covering soil with organic or inorganic materials reduces evaporation, suppresses weeds, and improves soil health.",
            "tips": [
                "Apply 5-10 cm of organic mulch around crops",
                "Use straw, wood chips, or compost as mulch material",
                "Replenish mulch as it decomposes",
                "Keep mulch away from plant stems to prevent rot",
            ],
        },
        {
            "title": "Rainwater Harvesting",
            "icon": "🌧️",
            "savings": "40-70%",
            "description": "Collecting and storing rainwater for irrigation use during dry periods. Reduces dependence on groundwater.",
            "tips": [
                "Install gutters and downspouts on farm buildings",
                "Build farm ponds or cisterns for storage",
                "Use first-flush diverters to improve water quality",
                "Calculate your catchment area to size storage correctly",
            ],
        },
        {
            "title": "Deficit Irrigation",
            "icon": "📊",
            "savings": "15-30%",
            "description": "Applying less water than the full crop requirement during drought-tolerant growth stages to save water with minimal yield impact.",
            "tips": [
                "Identify crop growth stages tolerant to water stress",
                "Monitor plant water status indicators",
                "Combine with soil moisture sensors for precision",
                "Best suited for tree crops and deep-rooted plants",
            ],
        },
    ]

    for strategy in strategies:
        st.markdown(f"""
        <div class="modern-card" style="margin-bottom: 1rem; border-left: 4px solid var(--primary);">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                <span style="font-size: 2rem;">{strategy["icon"]}</span>
                <div>
                    <h3 style="margin: 0;">{html_escape(strategy["title"])}</h3>
                    <span style="color: var(--primary); font-weight: 600;">Water Savings: {html_escape(strategy["savings"])}</span>
                </div>
            </div>
            <p style="margin-bottom: 0.75rem;">{html_escape(strategy["description"])}</p>
        </div>
        """, unsafe_allow_html=True)

        for tip in strategy["tips"]:
            st.markdown(f"""
            <div class="activity-item" style="padding-left: 1rem;">
                <div class="activity-dot"></div>
                <div>{html_escape(tip)}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("##### Water Savings Comparison")
    methods = [s["title"] for s in strategies]
    min_savings = [int(s["savings"].split("-")[0]) for s in strategies]
    max_savings = [int(s["savings"].split("-")[1].replace("%", "")) for s in strategies]
    avg_savings = [(mn + mx) / 2 for mn, mx in zip(min_savings, max_savings)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=methods,
        y=avg_savings,
        marker_color=["#3b82f6", "#16a34a", "#f59e0b", "#8b5cf6"],
        text=[f"{s}%" for s in [s["savings"] for s in strategies]],
        textposition="outside",
    ))
    fig.update_layout(
        height=350,
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        yaxis=dict(title="Average Water Savings (%)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_agroforestry():
    st.markdown("#### Agroforestry Guidance")
    st.markdown("""
    <div class="modern-card" style="margin-bottom: 1.5rem;">
        <p style="margin: 0;">Agroforestry integrates trees and shrubs with crops and livestock to create more diverse, productive, and sustainable land-use systems. Trees sequester carbon, improve soil health, and provide additional income streams.</p>
    </div>
    """, unsafe_allow_html=True)

    systems = [
        {
            "name": "Alley Cropping",
            "icon": "🌿",
            "description": "Rows of trees planted between alleys of crops. Trees provide nutrients, shade, and wind protection.",
            "trees": "Leucaena, Gliricidia, Sesbania, Paulownia",
            "crops": "Maize, Beans, Vegetables, Grains",
            "carbon_seq": "2-5 t CO₂/ha/year",
            "benefits": ["Nitrogen fixation from legume trees", "Wind erosion reduction", "Additional timber/fodder income"],
        },
        {
            "name": "Silvopasture",
            "icon": "🐄",
            "description": "Combining trees with livestock grazing areas. Trees provide shade for animals and improve pasture quality.",
            "trees": "Oak, Pine, Acacia, Poplar",
            "crops": "Improved Pasture Grasses, Clover",
            "carbon_seq": "3-8 t CO₂/ha/year",
            "benefits": ["Reduced heat stress for livestock", "Improved animal welfare", "Diversified income from timber"],
        },
        {
            "name": "Forest Farming",
            "icon": "🍄",
            "description": "Growing specialty crops under the canopy of managed forests. Ideal for shade-loving products.",
            "trees": "Hardwoods (Oak, Maple, Walnut)",
            "crops": "Mushrooms, Medicinal Herbs, Shade Coffee, Cacao",
            "carbon_seq": "5-12 t CO₂/ha/year",
            "benefits": ["High-value specialty products", "Biodiversity conservation", "Minimal soil disturbance"],
        },
        {
            "name": "Riparian Buffers",
            "icon": "🌊",
            "description": "Planting trees and shrubs along waterways to protect water quality and provide habitat corridors.",
            "trees": "Willow, Alder, Native Species",
            "crops": "Not applicable (conservation purpose)",
            "carbon_seq": "3-7 t CO₂/ha/year",
            "benefits": ["Water quality protection", "Flood risk reduction", "Wildlife habitat corridors"],
        },
    ]

    for system in systems:
        with st.expander(f"{system['icon']} {system['name']} — Carbon Sequestration: {system['carbon_seq']}"):
            st.markdown(f"""
            <div class="modern-card">
                <p>{html_escape(system["description"])}</p>
                <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 0.75rem;">
                    <div>
                        <strong>Recommended Trees:</strong><br>
                        <span style="color: var(--text-secondary);">{html_escape(system["trees"])}</span>
                    </div>
                    <div>
                        <strong>Compatible Crops:</strong><br>
                        <span style="color: var(--text-secondary);">{html_escape(system["crops"])}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**Key Benefits:**")
            for benefit in system["benefits"]:
                st.markdown(f"""
                <div class="activity-item">
                    <div class="activity-dot"></div>
                    <div>{html_escape(benefit)}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Carbon Sequestration Potential by System")

    system_names = [s["name"] for s in systems]
    min_seq = [int(s["carbon_seq"].split("-")[0]) for s in systems]
    max_seq = [int(s["carbon_seq"].split("-")[1].split(" ")[0]) for s in systems]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Minimum",
        x=system_names,
        y=min_seq,
        marker_color="rgba(22, 163, 74, 0.5)",
    ))
    fig.add_trace(go.Bar(
        name="Maximum",
        x=system_names,
        y=max_seq,
        marker_color="#16a34a",
    ))
    fig.update_layout(
        barmode="group",
        height=350,
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        yaxis=dict(title="t CO₂/ha/year", showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
    )
    st.plotly_chart(fig, use_container_width=True)
