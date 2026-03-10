import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
from html import escape as html_escape
from backend.db import fetch_all, fetch_one


def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def show_dashboard():
    user = st.session_state.get("user", {})
    user_id = user.get("id")
    name = html_escape(user.get("name", "Farmer"))

    hero_b64 = get_image_base64("assets/images/hero_banner.png")
    if hero_b64:
        st.markdown(f"""
        <div style="position: relative; border-radius: 20px; overflow: hidden; margin-bottom: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
            <img src="data:image/png;base64,{hero_b64}" style="width: 100%; height: 220px; object-fit: cover; display: block;">
            <div style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(6,78,59,0.85) 0%, rgba(4,120,87,0.7) 50%, rgba(5,150,105,0.5) 100%); display: flex; flex-direction: column; justify-content: center; padding: 2rem 2.5rem;">
                <h1 style="color: white; font-family: 'Poppins', sans-serif; font-size: 1.8rem; margin: 0 0 0.25rem 0;">Welcome back, {name}</h1>
                <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin: 0;">Here's an overview of your farm activity and insights</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="hero-section">
            <h1 style="color: white;">Welcome back, {name}</h1>
            <p>Here's an overview of your farm activity and insights</p>
        </div>
        """, unsafe_allow_html=True)

    total_crops = fetch_one("SELECT COUNT(*) as count FROM crops WHERE user_id = %s", (user_id,))
    active_listings = fetch_one("SELECT COUNT(*) as count FROM market WHERE user_id = %s", (user_id,))
    diseases_detected = fetch_one(
        "SELECT COUNT(*) as count FROM crops WHERE user_id = %s AND disease_detected IS NOT NULL AND disease_detected != ''",
        (user_id,),
    )
    iot_devices = fetch_one("SELECT COUNT(*) as count FROM iot_devices WHERE user_id = %s AND is_active = true", (user_id,))

    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "🌱", total_crops["count"] if total_crops else 0, "Crops Logged"),
        (c2, "🛒", active_listings["count"] if active_listings else 0, "Market Listings"),
        (c3, "🔬", diseases_detected["count"] if diseases_detected else 0, "Diseases Found"),
        (c4, "📡", iot_devices["count"] if iot_devices else 0, "Active Sensors"),
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

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Crop Distribution")
        crop_dist = fetch_all(
            "SELECT crop_name, COUNT(*) as count FROM crops WHERE user_id = %s AND crop_name IS NOT NULL GROUP BY crop_name ORDER BY count DESC",
            (user_id,),
        )
        if crop_dist:
            fig = px.pie(
                values=[r["count"] for r in crop_dist],
                names=[r["crop_name"] for r in crop_dist],
                color_discrete_sequence=["#16a34a", "#059669", "#0d9488", "#0891b2", "#2563eb", "#7c3aed"],
                hole=0.4,
            )
            fig.update_layout(
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No crops logged yet. Start by adding crops in Crop Monitoring.")

    with col_right:
        st.markdown("#### Disease Detection Trend")
        disease_trend = fetch_all(
            "SELECT DATE(date_logged) as log_date, COUNT(*) as count FROM crops WHERE user_id = %s AND disease_detected IS NOT NULL AND disease_detected != '' GROUP BY DATE(date_logged) ORDER BY log_date",
            (user_id,),
        )
        if disease_trend:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[r["log_date"] for r in disease_trend],
                y=[r["count"] for r in disease_trend],
                mode="lines+markers",
                name="Diseases",
                line=dict(color="#dc2626", width=2.5),
                marker=dict(size=8),
                fill="tozeroy",
                fillcolor="rgba(220, 38, 38, 0.08)",
            ))
            fig.update_layout(
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No disease detections yet. Try the Crop Diagnosis feature.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Quick Access")

    feature_images = {
        "Crop Diagnosis": ("assets/images/crop_maize.png", "AI-powered disease detection from crop photos"),
        "Market": ("assets/images/market_produce.png", "Real-time prices and connect with buyers"),
        "IoT Dashboard": ("assets/images/iot_sensor.png", "Monitor your smart sensors in real-time"),
        "Weather": ("assets/images/weather_station.png", "Localized forecasts and weather alerts"),
    }

    cols = st.columns(4)
    for i, (page_name, (img_path, desc)) in enumerate(feature_images.items()):
        with cols[i]:
            img_b64 = get_image_base64(img_path)
            if img_b64:
                st.markdown(f"""
                <div class="feature-card">
                    <img src="data:image/png;base64,{img_b64}" alt="{page_name}">
                    <div class="card-body">
                        <h3>{page_name}</h3>
                        <p>{desc}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="feature-card">
                    <div style="height: 160px; background: linear-gradient(135deg, var(--primary-100), var(--primary-200)); display: flex; align-items: center; justify-content: center; font-size: 3rem;">🌱</div>
                    <div class="card-body">
                        <h3>{page_name}</h3>
                        <p>{desc}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            if st.button(f"Open {page_name}", use_container_width=True, key=f"quick_{page_name}"):
                st.session_state["page"] = page_name
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Recent Activity")
    recent = fetch_all(
        "SELECT crop_name, growth_stage, disease_detected, date_logged FROM crops WHERE user_id = %s ORDER BY date_logged DESC LIMIT 8",
        (user_id,),
    )
    if recent:
        for r in recent:
            disease_text = f" &mdash; Disease: <strong>{html_escape(r['disease_detected'])}</strong>" if r.get("disease_detected") else ""
            stage_text = f" | Stage: {html_escape(r['growth_stage'])}" if r.get("growth_stage") else ""
            date_text = r["date_logged"].strftime("%b %d, %Y at %H:%M") if r.get("date_logged") else ""
            crop_name = html_escape(r.get("crop_name", "Unknown"))
            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div>
                    <div style="font-weight: 500;">🌱 {crop_name}{stage_text}{disease_text}</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">{date_text}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activity. Start logging your crops!")
