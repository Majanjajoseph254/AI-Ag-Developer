import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from backend.db import fetch_all, fetch_one


def show_dashboard():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    st.title(f"Welcome, {user.get('name', 'Farmer')}! 🌾")
    st.markdown("Here's your AgriShield AI dashboard overview.")

    total_crops = fetch_one(
        "SELECT COUNT(*) as count FROM crops WHERE user_id = %s", (user_id,)
    )
    active_listings = fetch_one(
        "SELECT COUNT(*) as count FROM market WHERE user_id = %s", (user_id,)
    )
    diseases_detected = fetch_one(
        "SELECT COUNT(*) as count FROM crops WHERE user_id = %s AND disease_detected IS NOT NULL AND disease_detected != ''",
        (user_id,),
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Crops Logged", total_crops["count"] if total_crops else 0)
    with col2:
        st.metric("Active Market Listings", active_listings["count"] if active_listings else 0)
    with col3:
        st.metric("Diseases Detected", diseases_detected["count"] if diseases_detected else 0)

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Crop Distribution")
        crop_dist = fetch_all(
            "SELECT crop_name, COUNT(*) as count FROM crops WHERE user_id = %s AND crop_name IS NOT NULL GROUP BY crop_name ORDER BY count DESC",
            (user_id,),
        )
        if crop_dist:
            fig = px.pie(
                values=[r["count"] for r in crop_dist],
                names=[r["crop_name"] for r in crop_dist],
                title="Your Crops",
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No crops logged yet. Start by adding crops in Crop Monitoring.")

    with col_right:
        st.subheader("Disease Detection Trend")
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
                line=dict(color="#e74c3c"),
            ))
            fig.update_layout(
                title="Diseases Detected Over Time",
                xaxis_title="Date",
                yaxis_title="Count",
                height=350,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No disease detections yet. Try the Crop Diagnosis feature.")

    st.divider()

    st.subheader("Recent Activity")
    recent = fetch_all(
        "SELECT crop_name, growth_stage, disease_detected, date_logged FROM crops WHERE user_id = %s ORDER BY date_logged DESC LIMIT 10",
        (user_id,),
    )
    if recent:
        for r in recent:
            disease_text = f" — Disease: **{r['disease_detected']}**" if r.get("disease_detected") else ""
            stage_text = f" | Stage: {r['growth_stage']}" if r.get("growth_stage") else ""
            date_text = r["date_logged"].strftime("%Y-%m-%d %H:%M") if r.get("date_logged") else ""
            st.markdown(f"- 🌱 **{r.get('crop_name', 'Unknown')}**{stage_text}{disease_text} — _{date_text}_")
    else:
        st.info("No recent activity. Start logging your crops!")

    st.divider()

    st.subheader("Quick Actions")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    with qcol1:
        if st.button("🔬 Crop Diagnosis", use_container_width=True):
            st.session_state["page"] = "Crop Diagnosis"
            st.rerun()
    with qcol2:
        if st.button("📊 Crop Monitoring", use_container_width=True):
            st.session_state["page"] = "Crop Monitoring"
            st.rerun()
    with qcol3:
        if st.button("🛒 Market", use_container_width=True):
            st.session_state["page"] = "Market"
            st.rerun()
    with qcol4:
        if st.button("🌤️ Weather", use_container_width=True):
            st.session_state["page"] = "Weather"
            st.rerun()
