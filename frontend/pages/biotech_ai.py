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


CROP_VARIETIES = {
    "Maize": [
        {"name": "DKC 9141", "type": "Hybrid", "maturity": "Medium (120 days)", "yield_potential": "12-14 t/ha", "drought_tolerance": "High", "disease_resistance": "Gray Leaf Spot, Rust", "traits": "Drought tolerant, High starch content", "origin": "South Africa"},
        {"name": "WE 5323", "type": "Hybrid", "maturity": "Early (105 days)", "yield_potential": "10-12 t/ha", "drought_tolerance": "Medium", "disease_resistance": "Northern Leaf Blight", "traits": "Early maturity, Good standability", "origin": "USA"},
        {"name": "SC 506", "type": "Open-Pollinated", "maturity": "Medium (115 days)", "yield_potential": "6-8 t/ha", "drought_tolerance": "High", "disease_resistance": "Streak Virus", "traits": "Stress tolerant, Low input requirement", "origin": "Zimbabwe"},
        {"name": "PAN 6Q-745BR", "type": "Hybrid (GM)", "maturity": "Medium-Late (130 days)", "yield_potential": "14-16 t/ha", "drought_tolerance": "Medium", "disease_resistance": "Bt insect resistance", "traits": "Bt protein, Herbicide tolerant", "origin": "South Africa"},
    ],
    "Wheat": [
        {"name": "SST 806", "type": "Hybrid", "maturity": "Medium (140 days)", "yield_potential": "6-8 t/ha", "drought_tolerance": "Medium", "disease_resistance": "Stem Rust, Leaf Rust", "traits": "High protein, Good baking quality", "origin": "South Africa"},
        {"name": "Durum Gold", "type": "Cultivar", "maturity": "Late (155 days)", "yield_potential": "5-7 t/ha", "drought_tolerance": "Low", "disease_resistance": "Fusarium", "traits": "High gluten, Pasta quality", "origin": "Italy"},
        {"name": "HD 3226", "type": "Cultivar", "maturity": "Early (120 days)", "yield_potential": "5-6 t/ha", "drought_tolerance": "High", "disease_resistance": "Yellow Rust, Brown Rust", "traits": "Heat tolerant, Early harvest", "origin": "India"},
    ],
    "Tomato": [
        {"name": "Heinz 1370", "type": "Determinate", "maturity": "Mid (75 days)", "yield_potential": "80-100 t/ha", "drought_tolerance": "Low", "disease_resistance": "Verticillium Wilt", "traits": "Processing type, High lycopene", "origin": "USA"},
        {"name": "Star 9065", "type": "Indeterminate", "maturity": "Early (65 days)", "yield_potential": "60-80 t/ha", "drought_tolerance": "Medium", "disease_resistance": "TMV, Fusarium", "traits": "Fresh market, Long shelf life", "origin": "Netherlands"},
        {"name": "Roma VF", "type": "Determinate", "maturity": "Mid (76 days)", "yield_potential": "40-60 t/ha", "drought_tolerance": "Medium", "disease_resistance": "Verticillium, Fusarium", "traits": "Paste type, Compact plant", "origin": "USA"},
    ],
    "Potato": [
        {"name": "Mondial", "type": "Cultivar", "maturity": "Medium-Late (120 days)", "yield_potential": "50-70 t/ha", "drought_tolerance": "Medium", "disease_resistance": "Common Scab", "traits": "Long oval shape, Multi-purpose", "origin": "Netherlands"},
        {"name": "BP1", "type": "Cultivar", "maturity": "Medium (100 days)", "yield_potential": "40-55 t/ha", "drought_tolerance": "Medium", "disease_resistance": "Late Blight (moderate)", "traits": "Round shape, Good chip quality", "origin": "South Africa"},
        {"name": "Sifra", "type": "Cultivar", "maturity": "Medium (110 days)", "yield_potential": "45-65 t/ha", "drought_tolerance": "High", "disease_resistance": "PVY, Late Blight", "traits": "Cream flesh, Excellent storage", "origin": "Netherlands"},
    ],
}

BIOTECH_INNOVATIONS = [
    {
        "title": "Genetically Modified (GM) Crops",
        "icon": "🧬",
        "description": "Engineered crops with specific traits like pest resistance (Bt crops), herbicide tolerance, and enhanced nutritional content (Golden Rice).",
        "examples": "Bt Cotton, Roundup Ready Soya, Golden Rice, Arctic Apple",
        "benefits": "Reduced pesticide use, Higher yields, Enhanced nutrition",
        "status": "Commercially available",
    },
    {
        "title": "CRISPR Gene Editing",
        "icon": "✂️",
        "description": "Precise genome editing technology allowing targeted modifications without introducing foreign DNA. Faster and cheaper than traditional GM.",
        "examples": "Non-browning mushrooms, Drought-tolerant maize, High-oleic soybean",
        "benefits": "Precision, Speed, No foreign DNA, Lower regulatory burden",
        "status": "Emerging - First products approved",
    },
    {
        "title": "Tissue Culture & Micropropagation",
        "icon": "🧫",
        "description": "Lab-based plant multiplication producing disease-free, genetically identical plantlets from small tissue samples.",
        "examples": "Banana tissue culture, Potato minitubers, Orchid propagation",
        "benefits": "Disease-free plants, Rapid multiplication, Genetic uniformity",
        "status": "Widely adopted",
    },
    {
        "title": "Marker-Assisted Selection (MAS)",
        "icon": "🔬",
        "description": "Using DNA markers to identify desirable traits in breeding programs, accelerating traditional breeding by 50-70%.",
        "examples": "Submergence-tolerant rice (Sub1), Disease-resistant wheat lines",
        "benefits": "Faster breeding cycles, Precision trait selection, Cost effective",
        "status": "Widely adopted",
    },
    {
        "title": "Biological Nitrogen Fixation",
        "icon": "🦠",
        "description": "Engineering non-legume crops to fix atmospheric nitrogen, reducing fertilizer dependency and environmental impact.",
        "examples": "Nitrogen-fixing cereals (research), Enhanced rhizobium inoculants",
        "benefits": "Reduced fertilizer costs, Lower emissions, Soil health",
        "status": "Research phase",
    },
    {
        "title": "RNA Interference (RNAi)",
        "icon": "🧪",
        "description": "Silencing specific genes to confer pest resistance or improve crop quality without adding new genes.",
        "examples": "Non-browning Arctic Apple, Virus-resistant papaya, Low-acrylamide potato",
        "benefits": "Targeted gene silencing, Pest resistance, Quality improvement",
        "status": "Limited commercial use",
    },
]

SOIL_TYPES = ["Sandy", "Sandy Loam", "Loam", "Clay Loam", "Clay", "Silt Loam", "Peat"]
CLIMATE_ZONES = ["Tropical", "Subtropical", "Temperate", "Arid/Semi-Arid", "Mediterranean", "Highland/Montane"]

RECOMMENDATIONS = {
    ("Tropical", "Sandy"): {"crops": ["Cassava", "Sweet Potato", "Groundnut"], "notes": "Sandy soils in tropical zones drain quickly. Choose drought-tolerant root crops. Add organic matter to improve water retention."},
    ("Tropical", "Sandy Loam"): {"crops": ["Maize", "Tomato", "Cowpea"], "notes": "Good drainage with decent moisture retention. Ideal for diverse cropping. Consider intercropping legumes with cereals."},
    ("Tropical", "Loam"): {"crops": ["Rice", "Maize", "Banana"], "notes": "Excellent soil for most tropical crops. Rich nutrient base supports high-yield varieties."},
    ("Tropical", "Clay Loam"): {"crops": ["Rice", "Sugar Cane", "Taro"], "notes": "High moisture retention suits paddy crops. Good for irrigated agriculture."},
    ("Tropical", "Clay"): {"crops": ["Rice", "Sugar Cane"], "notes": "Heavy soils best for flooded/paddy systems. Drainage management critical."},
    ("Tropical", "Silt Loam"): {"crops": ["Vegetables", "Maize", "Beans"], "notes": "Fertile alluvial soils ideal for vegetable production and cereal crops."},
    ("Tropical", "Peat"): {"crops": ["Oil Palm", "Pineapple"], "notes": "Acidic organic soils. Lime application needed. Avoid drainage that causes subsidence."},
    ("Subtropical", "Sandy"): {"crops": ["Groundnut", "Millet", "Watermelon"], "notes": "Light soils warm quickly. Good for early season planting. Mulching recommended."},
    ("Subtropical", "Sandy Loam"): {"crops": ["Citrus", "Maize", "Soybean"], "notes": "Well-balanced soil for subtropical fruit and grain production."},
    ("Subtropical", "Loam"): {"crops": ["Wheat", "Maize", "Tomato", "Potato"], "notes": "Versatile soil supporting diverse cropping systems. Rotation recommended."},
    ("Subtropical", "Clay Loam"): {"crops": ["Wheat", "Cotton", "Sunflower"], "notes": "Good for winter cereals and summer oilseeds. Manage compaction."},
    ("Subtropical", "Clay"): {"crops": ["Rice", "Wheat"], "notes": "Heavy soils suit irrigated cereals. Conservation tillage beneficial."},
    ("Subtropical", "Silt Loam"): {"crops": ["Vegetables", "Wheat", "Barley"], "notes": "Highly productive for mixed farming systems."},
    ("Subtropical", "Peat"): {"crops": ["Blueberry", "Cranberry"], "notes": "Acidic conditions suit acid-loving crops. Limited cropping options."},
    ("Temperate", "Sandy"): {"crops": ["Potato", "Carrot", "Rye"], "notes": "Light soils warm up early in spring. Good for root vegetables."},
    ("Temperate", "Sandy Loam"): {"crops": ["Barley", "Potato", "Beet"], "notes": "Excellent for root crops and small grains. Easy to work."},
    ("Temperate", "Loam"): {"crops": ["Wheat", "Maize", "Rapeseed", "Potato"], "notes": "Premier agricultural soil. Supports most temperate crops at high yields."},
    ("Temperate", "Clay Loam"): {"crops": ["Wheat", "Oats", "Beans"], "notes": "Strong nutrient holding capacity. Good for winter cereals."},
    ("Temperate", "Clay"): {"crops": ["Wheat", "Grassland"], "notes": "Heavy, slow-draining soils. Best for permanent pasture or adapted cereals."},
    ("Temperate", "Silt Loam"): {"crops": ["Wheat", "Sugar Beet", "Vegetables"], "notes": "High fertility loess soils. Excellent for intensive cropping."},
    ("Temperate", "Peat"): {"crops": ["Grassland", "Vegetables (raised beds)"], "notes": "Organic soils with high water table. Managed drainage essential."},
    ("Arid/Semi-Arid", "Sandy"): {"crops": ["Millet", "Sorghum", "Date Palm"], "notes": "Extreme water conservation needed. Drip irrigation essential. Choose xerophytic crops."},
    ("Arid/Semi-Arid", "Sandy Loam"): {"crops": ["Sorghum", "Cowpea", "Sesame"], "notes": "Better moisture retention than pure sand. Mulching critical."},
    ("Arid/Semi-Arid", "Loam"): {"crops": ["Wheat (irrigated)", "Chickpea", "Olive"], "notes": "Productive under irrigation. Water-use efficiency is key."},
    ("Arid/Semi-Arid", "Clay Loam"): {"crops": ["Wheat", "Barley", "Lentil"], "notes": "Good moisture storage. Suitable for dryland cereals and pulses."},
    ("Arid/Semi-Arid", "Clay"): {"crops": ["Sorghum", "Cotton (irrigated)"], "notes": "Vertic clays crack when dry. Good self-mulching but difficult to manage."},
    ("Arid/Semi-Arid", "Silt Loam"): {"crops": ["Wheat", "Alfalfa"], "notes": "Good water holding in irrigated systems."},
    ("Arid/Semi-Arid", "Peat"): {"crops": ["Limited options"], "notes": "Rare combination. Organic matter decomposes rapidly in arid conditions."},
    ("Mediterranean", "Sandy"): {"crops": ["Grape", "Olive", "Almond"], "notes": "Free-draining soils suit perennial tree crops and vines."},
    ("Mediterranean", "Sandy Loam"): {"crops": ["Tomato", "Grape", "Citrus"], "notes": "Ideal for Mediterranean horticulture. Good drainage with moisture retention."},
    ("Mediterranean", "Loam"): {"crops": ["Wheat", "Olive", "Tomato", "Pepper"], "notes": "Versatile soil for diverse Mediterranean agriculture."},
    ("Mediterranean", "Clay Loam"): {"crops": ["Wheat", "Sunflower", "Chickpea"], "notes": "Good for winter cereals and summer crops under careful water management."},
    ("Mediterranean", "Clay"): {"crops": ["Wheat", "Olive (established)"], "notes": "Heavy soils suit deep-rooted perennials and winter cereals."},
    ("Mediterranean", "Silt Loam"): {"crops": ["Vegetables", "Wheat", "Vine crops"], "notes": "Highly productive for irrigated vegetable production."},
    ("Mediterranean", "Peat"): {"crops": ["Vegetables (raised)"], "notes": "Uncommon. Manage water table carefully."},
    ("Highland/Montane", "Sandy"): {"crops": ["Potato", "Barley"], "notes": "Cool temperatures and light soils. Short growing season crops."},
    ("Highland/Montane", "Sandy Loam"): {"crops": ["Potato", "Pea", "Barley"], "notes": "Good for cool-season crops. Watch for frost damage."},
    ("Highland/Montane", "Loam"): {"crops": ["Wheat", "Potato", "Tea", "Coffee"], "notes": "Excellent highland agricultural soil. Terracing may be needed."},
    ("Highland/Montane", "Clay Loam"): {"crops": ["Tea", "Pyrethrum", "Wheat"], "notes": "Good moisture retention at altitude. Suitable for perennial crops."},
    ("Highland/Montane", "Clay"): {"crops": ["Grassland", "Potato"], "notes": "Cold, wet soils. Limited cropping. Best for pasture."},
    ("Highland/Montane", "Silt Loam"): {"crops": ["Vegetables", "Wheat", "Flowers"], "notes": "Productive highland soils for diverse cropping."},
    ("Highland/Montane", "Peat"): {"crops": ["Grassland"], "notes": "Bog/moorland soils. Very limited agricultural use."},
}


def show_biotech_ai():
    hero_b64 = get_image_base64("assets/images/crop_maize.png")
    if hero_b64:
        st.markdown(f"""
        <div style="position: relative; border-radius: 20px; overflow: hidden; margin-bottom: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
            <img src="data:image/png;base64,{hero_b64}" style="width: 100%; height: 220px; object-fit: cover; display: block;">
            <div style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(6,78,59,0.85) 0%, rgba(4,120,87,0.7) 50%, rgba(5,150,105,0.5) 100%); display: flex; flex-direction: column; justify-content: center; padding: 2rem 2.5rem;">
                <h1 style="color: white; font-family: 'Poppins', sans-serif; font-size: 1.8rem; margin: 0 0 0.25rem 0;">🧬 Biotechnology & AI</h1>
                <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin: 0;">Explore crop genetics, AI-powered recommendations, and cutting-edge agricultural biotechnology</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hero-section">
            <h1 style="color: white;">🧬 Biotechnology & AI</h1>
            <p>Explore crop genetics, AI-powered recommendations, and cutting-edge agricultural biotechnology</p>
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌾 Variety Database",
        "🤖 AI Crop Recommendations",
        "🔬 Biotech Innovations",
        "⚖️ Seed Comparison",
        "📈 Yield Predictor",
    ])

    with tab1:
        _render_variety_database()

    with tab2:
        _render_ai_recommendations()

    with tab3:
        _render_biotech_innovations()

    with tab4:
        _render_seed_comparison()

    with tab5:
        _render_yield_predictor()


def _render_variety_database():
    st.markdown("### Crop Genetic Information Database")
    st.markdown("Browse comprehensive variety data for major crops including traits, resistance profiles, and yield potential.")

    selected_crop = st.selectbox("Select Crop", list(CROP_VARIETIES.keys()), key="variety_crop")
    varieties = CROP_VARIETIES[selected_crop]

    for v in varieties:
        name_escaped = html_escape(v["name"])
        type_escaped = html_escape(v["type"])
        st.markdown(f"""
        <div class="modern-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <h3 style="margin: 0; color: var(--primary-dark);">🌱 {name_escaped}</h3>
                <span style="background: var(--primary-100); color: var(--primary-dark); padding: 0.2rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">{type_escaped}</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.75rem;">
                <div><strong style="color: var(--text-secondary); font-size: 0.85rem;">Maturity</strong><br>{html_escape(v["maturity"])}</div>
                <div><strong style="color: var(--text-secondary); font-size: 0.85rem;">Yield Potential</strong><br>{html_escape(v["yield_potential"])}</div>
                <div><strong style="color: var(--text-secondary); font-size: 0.85rem;">Drought Tolerance</strong><br>{html_escape(v["drought_tolerance"])}</div>
                <div><strong style="color: var(--text-secondary); font-size: 0.85rem;">Origin</strong><br>{html_escape(v["origin"])}</div>
            </div>
            <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid var(--border);">
                <strong style="color: var(--text-secondary); font-size: 0.85rem;">Disease Resistance:</strong> {html_escape(v["disease_resistance"])}<br>
                <strong style="color: var(--text-secondary); font-size: 0.85rem;">Key Traits:</strong> {html_escape(v["traits"])}
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_ai_recommendations():
    st.markdown("### AI-Powered Crop Recommendations")
    st.markdown("Get personalized crop suggestions based on your soil type and climate zone.")

    col1, col2 = st.columns(2)
    with col1:
        climate = st.selectbox("Climate Zone", CLIMATE_ZONES, key="rec_climate")
    with col2:
        soil = st.selectbox("Soil Type", SOIL_TYPES, key="rec_soil")

    col3, col4 = st.columns(2)
    with col3:
        rainfall = st.slider("Annual Rainfall (mm)", 100, 3000, 800, 50, key="rec_rainfall")
    with col4:
        ph = st.slider("Soil pH", 3.5, 9.5, 6.5, 0.1, key="rec_ph")

    if st.button("🤖 Get AI Recommendations", use_container_width=True, key="btn_recommend"):
        rec = RECOMMENDATIONS.get((climate, soil))
        if rec:
            crops_list = rec["crops"]
            notes = rec["notes"]
        else:
            crops_list = ["Maize", "Beans", "Sorghum"]
            notes = "General recommendation. Consider consulting local agricultural extension services for specific guidance."

        rainfall_note = ""
        if rainfall < 400:
            rainfall_note = "⚠️ Low rainfall zone: prioritize drought-tolerant and short-season varieties. Drip irrigation strongly recommended."
        elif rainfall > 1500:
            rainfall_note = "💧 High rainfall zone: ensure good drainage. Consider raised beds and disease-resistant varieties."

        ph_note = ""
        if ph < 5.5:
            ph_note = "⚠️ Acidic soil: consider liming to raise pH. Acid-tolerant crops like cassava, tea, or blueberry may perform better."
        elif ph > 7.5:
            ph_note = "⚠️ Alkaline soil: iron and zinc deficiencies possible. Consider acidifying amendments and tolerant varieties."

        st.markdown("---")
        st.markdown("### 🎯 Recommended Crops")

        cols = st.columns(len(crops_list))
        crop_icons = {"Maize": "🌽", "Wheat": "🌾", "Rice": "🍚", "Potato": "🥔", "Tomato": "🍅", "Cassava": "🫘",
                       "Sorghum": "🌾", "Millet": "🌾", "Cotton": "🧵", "Soybean": "🫘", "Groundnut": "🥜",
                       "Banana": "🍌", "Coffee": "☕", "Tea": "🍵", "Grape": "🍇", "Olive": "🫒",
                       "Citrus": "🍊", "Sugar Cane": "🎋", "Sunflower": "🌻", "Barley": "🌾"}
        for i, crop in enumerate(crops_list):
            with cols[i]:
                icon = crop_icons.get(crop, "🌱")
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">{icon}</div>
                    <div class="stat-value" style="font-size: 1.2rem;">{html_escape(crop)}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="modern-card" style="margin-top: 1rem;">
            <h4 style="margin-top: 0;">📋 Agronomic Notes</h4>
            <p>{html_escape(notes)}</p>
        </div>
        """, unsafe_allow_html=True)

        if rainfall_note:
            st.info(rainfall_note)
        if ph_note:
            st.warning(ph_note)


def _render_biotech_innovations():
    st.markdown("### Biotechnology Innovations Showcase")
    st.markdown("Discover cutting-edge technologies transforming modern agriculture.")

    for i in range(0, len(BIOTECH_INNOVATIONS), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(BIOTECH_INNOVATIONS):
                inn = BIOTECH_INNOVATIONS[i + j]
                status_color = {"Commercially available": "#16a34a", "Widely adopted": "#0891b2", "Emerging - First products approved": "#f59e0b", "Research phase": "#8b5cf6", "Limited commercial use": "#ec4899"}.get(inn["status"], "#64748b")
                with col:
                    st.markdown(f"""
                    <div class="modern-card" style="margin-bottom: 1rem; min-height: 280px;">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{inn["icon"]}</div>
                        <h3 style="margin: 0 0 0.5rem 0;">{html_escape(inn["title"])}</h3>
                        <span style="background: {status_color}; color: white; padding: 0.15rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{html_escape(inn["status"])}</span>
                        <p style="margin-top: 0.75rem; font-size: 0.9rem; color: var(--text-secondary);">{html_escape(inn["description"])}</p>
                        <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid var(--border);">
                            <strong style="font-size: 0.8rem; color: var(--text-secondary);">Examples:</strong>
                            <span style="font-size: 0.85rem;"> {html_escape(inn["examples"])}</span>
                        </div>
                        <div style="margin-top: 0.4rem;">
                            <strong style="font-size: 0.8rem; color: var(--text-secondary);">Benefits:</strong>
                            <span style="font-size: 0.85rem;"> {html_escape(inn["benefits"])}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


def _render_seed_comparison():
    st.markdown("### Seed Variety Comparison Tool")
    st.markdown("Compare varieties side-by-side to make informed planting decisions.")

    crop = st.selectbox("Select Crop to Compare", list(CROP_VARIETIES.keys()), key="compare_crop")
    varieties = CROP_VARIETIES[crop]
    variety_names = [v["name"] for v in varieties]

    selected = st.multiselect("Select Varieties to Compare (2-4)", variety_names, default=variety_names[:2], key="compare_vars")

    if len(selected) < 2:
        st.warning("Please select at least 2 varieties to compare.")
        return

    selected_data = [v for v in varieties if v["name"] in selected]

    drought_map = {"High": 3, "Medium": 2, "Low": 1}

    def parse_yield(y):
        try:
            parts = y.replace(" t/ha", "").split("-")
            return (float(parts[0]) + float(parts[1])) / 2
        except (ValueError, IndexError):
            return 0

    def parse_maturity(m):
        try:
            days = m.split("(")[1].replace(" days)", "")
            return int(days)
        except (ValueError, IndexError):
            return 0

    comparison_data = []
    for v in selected_data:
        comparison_data.append({
            "Variety": v["name"],
            "Type": v["type"],
            "Maturity (days)": parse_maturity(v["maturity"]),
            "Avg Yield (t/ha)": parse_yield(v["yield_potential"]),
            "Drought Score": drought_map.get(v["drought_tolerance"], 1),
        })

    fig_yield = go.Figure()
    for d in comparison_data:
        fig_yield.add_trace(go.Bar(
            x=[d["Variety"]],
            y=[d["Avg Yield (t/ha)"]],
            name=d["Variety"],
            text=[f'{d["Avg Yield (t/ha)"]:.1f}'],
            textposition="auto",
        ))
    fig_yield.update_layout(
        title="Yield Potential Comparison",
        yaxis_title="Average Yield (t/ha)",
        height=350,
        margin=dict(t=40, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        showlegend=False,
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
    )
    fig_yield.update_traces(marker_color=["#16a34a", "#059669", "#0d9488", "#0891b2"][:len(comparison_data)])
    st.plotly_chart(fig_yield, use_container_width=True)

    fig_radar = go.Figure()
    categories = ["Yield", "Drought Tolerance", "Early Maturity"]
    for d in comparison_data:
        max_yield = max(x["Avg Yield (t/ha)"] for x in comparison_data) or 1
        max_mat = max(x["Maturity (days)"] for x in comparison_data) or 1
        values = [
            (d["Avg Yield (t/ha)"] / max_yield) * 5,
            d["Drought Score"] * (5 / 3),
            ((max_mat - d["Maturity (days)"]) / max_mat) * 5 + 1 if max_mat > 0 else 3,
        ]
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            name=d["Variety"],
            fill="toself",
            opacity=0.6,
        ))
    fig_radar.update_layout(
        title="Multi-Trait Comparison",
        height=400,
        margin=dict(t=40, b=20, l=60, r=60),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        polar=dict(radialaxis=dict(visible=True, range=[0, 5.5])),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("#### Detailed Comparison")
    for v in selected_data:
        st.markdown(f"""
        <div class="modern-card" style="margin-bottom: 0.75rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; color: var(--primary-dark);">{html_escape(v["name"])}</h4>
                <span style="font-size: 0.85rem; color: var(--text-secondary);">{html_escape(v["type"])} | {html_escape(v["origin"])}</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; margin-top: 0.5rem; font-size: 0.9rem;">
                <div>📅 <strong>Maturity:</strong> {html_escape(v["maturity"])}</div>
                <div>📊 <strong>Yield:</strong> {html_escape(v["yield_potential"])}</div>
                <div>💧 <strong>Drought:</strong> {html_escape(v["drought_tolerance"])}</div>
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-secondary);">
                🛡️ <strong>Resistance:</strong> {html_escape(v["disease_resistance"])} | 🧬 <strong>Traits:</strong> {html_escape(v["traits"])}
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_yield_predictor():
    st.markdown("### Yield Prediction Calculator")
    st.markdown("Estimate potential crop yields based on environmental and management factors.")

    col1, col2 = st.columns(2)
    with col1:
        pred_crop = st.selectbox("Crop", list(CROP_VARIETIES.keys()), key="pred_crop")
        variety_names = [v["name"] for v in CROP_VARIETIES[pred_crop]]
        pred_variety = st.selectbox("Variety", variety_names, key="pred_variety")
        farm_size = st.number_input("Farm Size (hectares)", min_value=0.1, max_value=10000.0, value=10.0, step=0.5, key="pred_size")
    with col2:
        pred_soil = st.selectbox("Soil Type", SOIL_TYPES, key="pred_soil")
        irrigation = st.selectbox("Irrigation Method", ["Rainfed", "Drip", "Sprinkler", "Flood/Furrow", "Center Pivot"], key="pred_irrigation")
        fertilizer = st.selectbox("Fertilizer Management", ["None", "Low (organic only)", "Moderate (balanced NPK)", "High (intensive)"], key="pred_fert")

    col5, col6 = st.columns(2)
    with col5:
        pred_rainfall = st.slider("Expected Rainfall (mm/season)", 100, 2000, 600, 50, key="pred_rain")
    with col6:
        pred_temp = st.slider("Average Temperature (°C)", 5, 45, 25, 1, key="pred_temp")

    if st.button("📈 Predict Yield", use_container_width=True, key="btn_predict"):
        variety_data = next((v for v in CROP_VARIETIES[pred_crop] if v["name"] == pred_variety), CROP_VARIETIES[pred_crop][0])

        def parse_yield_range(y):
            try:
                parts = y.replace(" t/ha", "").split("-")
                return float(parts[0]), float(parts[1])
            except (ValueError, IndexError):
                return 5.0, 10.0

        low, high = parse_yield_range(variety_data["yield_potential"])
        base_yield = (low + high) / 2

        soil_factor = {"Loam": 1.0, "Sandy Loam": 0.9, "Clay Loam": 0.92, "Silt Loam": 0.95, "Sandy": 0.75, "Clay": 0.8, "Peat": 0.7}.get(pred_soil, 0.85)
        irr_factor = {"Rainfed": 0.75, "Drip": 1.05, "Sprinkler": 0.95, "Flood/Furrow": 0.85, "Center Pivot": 1.0}.get(irrigation, 0.85)
        fert_factor = {"None": 0.55, "Low (organic only)": 0.75, "Moderate (balanced NPK)": 1.0, "High (intensive)": 1.1}.get(fertilizer, 0.85)

        rain_factor = 1.0
        if pred_rainfall < 300:
            rain_factor = 0.5
        elif pred_rainfall < 500:
            rain_factor = 0.75
        elif pred_rainfall < 800:
            rain_factor = 0.9
        elif pred_rainfall > 1500:
            rain_factor = 0.85

        temp_optimal = {"Maize": 25, "Wheat": 18, "Tomato": 24, "Potato": 18}
        optimal = temp_optimal.get(pred_crop, 22)
        temp_diff = abs(pred_temp - optimal)
        temp_factor = max(0.5, 1.0 - (temp_diff * 0.03))

        predicted = base_yield * soil_factor * irr_factor * fert_factor * rain_factor * temp_factor
        total_production = predicted * farm_size
        predicted_low = predicted * 0.85
        predicted_high = predicted * 1.15

        st.markdown("---")
        st.markdown("### 🎯 Yield Prediction Results")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">🌾</div>
                <div class="stat-value">{predicted:.1f}</div>
                <div class="stat-label">t/ha (predicted)</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">📦</div>
                <div class="stat-value">{total_production:.0f}</div>
                <div class="stat-label">Total tonnes</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            efficiency = (predicted / high) * 100 if high > 0 else 0
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-value">{efficiency:.0f}%</div>
                <div class="stat-label">Yield Efficiency</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">📐</div>
                <div class="stat-value">{predicted_low:.1f}-{predicted_high:.1f}</div>
                <div class="stat-label">Range (t/ha)</div>
            </div>
            """, unsafe_allow_html=True)

        factors = ["Soil", "Irrigation", "Fertilizer", "Rainfall", "Temperature"]
        factor_values = [soil_factor, irr_factor, fert_factor, rain_factor, temp_factor]
        factor_colors = ["#16a34a" if f >= 0.9 else "#f59e0b" if f >= 0.7 else "#dc2626" for f in factor_values]

        fig_factors = go.Figure(go.Bar(
            x=factors,
            y=[v * 100 for v in factor_values],
            marker_color=factor_colors,
            text=[f"{v*100:.0f}%" for v in factor_values],
            textposition="auto",
        ))
        fig_factors.update_layout(
            title="Factor Impact Analysis",
            yaxis_title="Factor Score (%)",
            height=350,
            margin=dict(t=40, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            yaxis=dict(range=[0, 120], showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        )
        fig_factors.add_hline(y=90, line_dash="dash", line_color="green", annotation_text="Optimal (90%+)")
        st.plotly_chart(fig_factors, use_container_width=True)

        suggestions = []
        if soil_factor < 0.85:
            suggestions.append("🪨 **Soil:** Consider soil amendments (compost, lime, gypsum) to improve soil quality for this crop.")
        if irr_factor < 0.9:
            suggestions.append("💧 **Irrigation:** Upgrading to drip irrigation could improve water-use efficiency and yields.")
        if fert_factor < 0.8:
            suggestions.append("🧪 **Fertilizer:** Balanced NPK application based on soil test results can significantly boost yields.")
        if rain_factor < 0.85:
            suggestions.append("🌧️ **Rainfall:** Consider supplemental irrigation or drought-tolerant varieties for your rainfall conditions.")
        if temp_factor < 0.85:
            suggestions.append(f"🌡️ **Temperature:** Current temperature deviates from optimal ({optimal}°C). Consider protected cultivation or season adjustment.")

        if suggestions:
            st.markdown("#### 💡 Improvement Suggestions")
            for s in suggestions:
                st.markdown(s)
        else:
            st.success("✅ Your conditions are well-optimized for this crop variety. Maintain current practices for best results.")
