import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from backend.db import execute_query, fetch_all


def show_crop_monitoring():
    st.title("🌱 Crop Monitoring")

    user_id = st.session_state["user"]["id"]

    tab1, tab2 = st.tabs(["Log New Crop", "My Crops"])

    with tab1:
        with st.form("crop_log_form"):
            crop_name = st.text_input("Crop Name", placeholder="e.g. Maize, Tomatoes")
            planting_date = st.date_input("Planting Date", value=date.today())
            growth_stage = st.selectbox(
                "Growth Stage",
                ["Seedling", "Vegetative", "Flowering", "Fruiting", "Harvest"],
            )
            fertilizer_used = st.text_input("Fertilizer Used", placeholder="e.g. DAP, CAN, NPK")
            pesticide_used = st.text_input("Pesticide Used", placeholder="e.g. None, Neem oil")
            notes = st.text_area("Notes", placeholder="Any observations about your crop")
            submitted = st.form_submit_button("Save Crop Log", use_container_width=True)

            if submitted:
                if not crop_name:
                    st.error("Please enter a crop name.")
                else:
                    execute_query(
                        """INSERT INTO crops (user_id, crop_name, planting_date, growth_stage,
                           fertilizer_used, pesticide_used, notes, date_logged)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())""",
                        (user_id, crop_name, planting_date, growth_stage,
                         fertilizer_used, pesticide_used, notes),
                    )
                    st.success(f"Crop '{crop_name}' logged successfully!")
                    st.rerun()

    with tab2:
        crops = fetch_all(
            "SELECT * FROM crops WHERE user_id = %s ORDER BY date_logged DESC", (user_id,)
        )

        if not crops:
            st.info("No crops logged yet. Start by adding your first crop!")
        else:
            df = pd.DataFrame(crops)
            display_cols = ["crop_name", "growth_stage", "planting_date", "fertilizer_used",
                            "pesticide_used", "disease_detected", "notes", "date_logged"]
            available_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[available_cols], use_container_width=True, hide_index=True)

            st.subheader("📊 Growth Stage Distribution")
            stage_counts = df["growth_stage"].value_counts().reset_index()
            stage_counts.columns = ["Growth Stage", "Count"]
            stage_order = ["Seedling", "Vegetative", "Flowering", "Fruiting", "Harvest"]
            stage_counts["Growth Stage"] = pd.Categorical(
                stage_counts["Growth Stage"], categories=stage_order, ordered=True
            )
            stage_counts = stage_counts.sort_values("Growth Stage")
            fig = px.bar(
                stage_counts,
                x="Growth Stage",
                y="Count",
                color="Growth Stage",
                color_discrete_sequence=px.colors.qualitative.Set2,
                title="Crops by Growth Stage",
            )
            st.plotly_chart(fig, use_container_width=True)

            diseases = df[df["disease_detected"].notna() & (df["disease_detected"] != "")]
            if not diseases.empty:
                st.subheader("🦠 Disease Trend")
                disease_counts = diseases["disease_detected"].value_counts().reset_index()
                disease_counts.columns = ["Disease", "Count"]
                fig2 = px.pie(
                    disease_counts,
                    names="Disease",
                    values="Count",
                    title="Detected Diseases",
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                )
                st.plotly_chart(fig2, use_container_width=True)
