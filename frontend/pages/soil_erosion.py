import streamlit as st

SOIL_TYPES = {
    "Clay": {
        "description": "Fine-grained, holds water well but drains poorly",
        "erosion_factor": 0.3,
        "icon": "🟤"
    },
    "Loam": {
        "description": "Balanced mix of sand, silt, and clay - ideal for farming",
        "erosion_factor": 0.5,
        "icon": "🟫"
    },
    "Sandy": {
        "description": "Coarse-grained, drains quickly but poor water retention",
        "erosion_factor": 0.7,
        "icon": "🟡"
    },
    "Silt": {
        "description": "Medium-grained, fertile but easily eroded",
        "erosion_factor": 0.8,
        "icon": "🟠"
    },
    "Sandy Loam": {
        "description": "Mostly sand with some silt and clay, moderate drainage",
        "erosion_factor": 0.6,
        "icon": "🟨"
    },
    "Clay Loam": {
        "description": "Mix of clay and loam, good fertility but can be heavy",
        "erosion_factor": 0.4,
        "icon": "🟫"
    },
    "Peat": {
        "description": "Rich in organic matter, acidic, common in wetlands",
        "erosion_factor": 0.2,
        "icon": "⬛"
    },
}

SLOPE_TYPES = {
    "Flat (0-2%)": {"factor": 0.1, "description": "Nearly level terrain"},
    "Gentle (2-8%)": {"factor": 0.3, "description": "Slight incline, manageable"},
    "Moderate (8-15%)": {"factor": 0.6, "description": "Noticeable slope, needs attention"},
    "Steep (15-30%)": {"factor": 0.85, "description": "Significant slope, high erosion risk"},
    "Very Steep (>30%)": {"factor": 1.0, "description": "Extreme slope, severe erosion risk"},
}

RAINFALL_LEVELS = {
    "Low (<500mm/year)": 0.2,
    "Moderate (500-1000mm/year)": 0.5,
    "High (1000-1500mm/year)": 0.7,
    "Very High (>1500mm/year)": 1.0,
}

VEGETATION_COVER = {
    "None (bare soil)": 1.0,
    "Sparse (<30%)": 0.7,
    "Moderate (30-70%)": 0.4,
    "Dense (>70%)": 0.1,
}


def _calculate_erosion_risk(soil_factor, slope_factor, rainfall_factor, vegetation_factor):
    score = (soil_factor * 0.25 + slope_factor * 0.35 + rainfall_factor * 0.25 + vegetation_factor * 0.15) * 100
    return min(round(score, 1), 100)


def _get_risk_level(score):
    if score < 20:
        return "Low", "🟢", "success"
    elif score < 40:
        return "Moderate", "🟡", "warning"
    elif score < 60:
        return "High", "🟠", "warning"
    else:
        return "Very High", "🔴", "error"


def _get_recommendations(soil_type, slope, risk_score):
    recommendations = []

    if risk_score >= 40:
        recommendations.append({
            "title": "🌿 Cover Crops",
            "description": "Plant cover crops like clover, vetch, or desmodium between growing seasons to protect soil from rain impact and reduce runoff.",
            "priority": "High"
        })

    if "Steep" in slope or "Moderate" in slope:
        recommendations.append({
            "title": "🏔️ Terracing",
            "description": "Build terraces along contour lines to slow water flow and reduce soil loss on slopes. Use stone or grass strips as barriers.",
            "priority": "High"
        })

    if risk_score >= 30:
        recommendations.append({
            "title": "🌾 Mulching",
            "description": "Apply organic mulch (crop residues, straw, grass) to protect soil surface. Use 5-10cm thickness for best results.",
            "priority": "Medium"
        })

    if soil_type in ("Sandy", "Silt", "Sandy Loam"):
        recommendations.append({
            "title": "🪵 Windbreaks",
            "description": "Plant trees or hedgerows perpendicular to prevailing winds. Use species like Grevillea, Casuarina, or Napier grass.",
            "priority": "Medium"
        })

    if risk_score >= 20:
        recommendations.append({
            "title": "🔄 Contour Farming",
            "description": "Plow and plant along contour lines rather than up-down the slope. This reduces water speed and soil erosion.",
            "priority": "Medium"
        })

    if soil_type in ("Sandy", "Sandy Loam"):
        recommendations.append({
            "title": "🧱 Soil Amendment",
            "description": "Add organic matter (compost, manure) to improve soil structure and water-holding capacity. Apply 5-10 tonnes per acre annually.",
            "priority": "Medium"
        })

    if "Steep" in slope:
        recommendations.append({
            "title": "🚰 Drainage Channels",
            "description": "Construct drainage channels to direct excess water safely. Line channels with stones or grass to prevent further erosion.",
            "priority": "High"
        })

    recommendations.append({
        "title": "🔬 Regular Soil Testing",
        "description": "Test soil every season to monitor nutrient levels and pH. Healthy soil with good structure resists erosion better.",
        "priority": "Low"
    })

    recommendations.append({
        "title": "🌳 Agroforestry",
        "description": "Integrate trees with crops to reduce erosion, improve soil fertility, and provide additional income from fruit/timber.",
        "priority": "Low"
    })

    return recommendations


def show_soil_erosion():
    st.title("🌍 Soil & Erosion Assessment")
    st.markdown("Assess erosion risk for your farm and get tailored recommendations to protect your soil.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Farm Conditions")

        soil_type = st.selectbox("Soil Type", list(SOIL_TYPES.keys()))
        soil_info = SOIL_TYPES[soil_type]
        st.caption(f"{soil_info['icon']} {soil_info['description']}")

        slope = st.selectbox("Farm Slope", list(SLOPE_TYPES.keys()))
        slope_info = SLOPE_TYPES[slope]
        st.caption(slope_info["description"])

        rainfall = st.selectbox("Annual Rainfall", list(RAINFALL_LEVELS.keys()))

        vegetation = st.selectbox("Current Vegetation Cover", list(VEGETATION_COVER.keys()))

    with col2:
        st.subheader("Additional Information")
        farm_size = st.number_input("Farm Size (acres)", min_value=0.1, max_value=1000.0, value=2.0, step=0.5)
        has_terracing = st.checkbox("Existing terracing?")
        has_cover_crops = st.checkbox("Currently using cover crops?")
        has_mulching = st.checkbox("Currently using mulch?")

    if st.button("🔍 Assess Erosion Risk", type="primary", use_container_width=True):
        soil_factor = soil_info["erosion_factor"]
        slope_factor = SLOPE_TYPES[slope]["factor"]
        rainfall_factor = RAINFALL_LEVELS[rainfall]
        vegetation_factor = VEGETATION_COVER[vegetation]

        if has_terracing:
            slope_factor *= 0.5
        if has_cover_crops:
            vegetation_factor *= 0.5
        if has_mulching:
            soil_factor *= 0.7

        risk_score = _calculate_erosion_risk(soil_factor, slope_factor, rainfall_factor, vegetation_factor)
        risk_level, risk_icon, risk_type = _get_risk_level(risk_score)

        st.divider()
        st.subheader("📊 Erosion Risk Assessment Results")

        result_col1, result_col2, result_col3 = st.columns(3)
        with result_col1:
            st.metric("Risk Score", f"{risk_score}/100")
        with result_col2:
            st.metric("Risk Level", f"{risk_icon} {risk_level}")
        with result_col3:
            estimated_loss = round(risk_score * 0.5 * farm_size, 1)
            st.metric("Est. Soil Loss", f"{estimated_loss} tonnes/year")

        st.progress(risk_score / 100)

        if risk_type == "error":
            st.error(f"⚠️ Your farm has a **{risk_level}** erosion risk. Immediate action is recommended to prevent significant soil loss and crop damage.")
        elif risk_type == "warning":
            st.warning(f"⚠️ Your farm has a **{risk_level}** erosion risk. Consider implementing the recommendations below to protect your soil.")
        else:
            st.success(f"✅ Your farm has a **{risk_level}** erosion risk. Continue good practices to maintain soil health.")

        st.divider()
        st.subheader("📋 Recommendations")

        recommendations = _get_recommendations(soil_type, slope, risk_score)
        for rec in recommendations:
            priority_colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
            priority_icon = priority_colors.get(rec["priority"], "🟢")
            with st.expander(f"{rec['title']} — Priority: {priority_icon} {rec['priority']}"):
                st.markdown(rec["description"])

        st.divider()
        st.subheader("📊 Risk Factor Breakdown")
        factors = {
            "Soil Type": soil_factor * 100,
            "Slope": slope_factor * 100,
            "Rainfall": rainfall_factor * 100,
            "Vegetation": vegetation_factor * 100
        }
        for factor_name, factor_value in factors.items():
            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.markdown(f"**{factor_name}**")
            with col_b:
                st.progress(min(factor_value / 100, 1.0))
                st.caption(f"{round(factor_value, 1)}% contribution")
