import streamlit as st
from backend.ai_disease import analyze_image
from backend.db import execute_query
from datetime import datetime


def show_crop_diagnosis():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    st.title("🔬 Crop Disease Diagnosis")
    st.markdown("Upload or capture a photo of your crop to detect potential diseases using AI analysis.")

    crop_type = st.selectbox(
        "Select Crop Type",
        ["maize", "tomatoes", "potatoes", "wheat"],
        format_func=lambda x: x.capitalize(),
    )

    st.markdown("### Provide a Crop Image")
    tab1, tab2 = st.tabs(["📷 Camera", "📁 Upload File"])

    image_bytes = None

    with tab1:
        camera_image = st.camera_input("Take a photo of the affected crop")
        if camera_image:
            image_bytes = camera_image.getvalue()

    with tab2:
        uploaded_file = st.file_uploader(
            "Upload a crop image",
            type=["jpg", "jpeg", "png"],
            key="diagnosis_uploader",
        )
        if uploaded_file:
            image_bytes = uploaded_file.getvalue()

    if image_bytes:
        st.image(image_bytes, caption="Captured/Uploaded Image", width=300)

        if st.button("🔍 Analyze Image", type="primary", use_container_width=True):
            with st.spinner("Analyzing image for diseases..."):
                result = analyze_image(image_bytes, crop_type)

            if not result["success"]:
                st.error(result["error"])
                return

            st.session_state["diagnosis_result"] = result

    if "diagnosis_result" in st.session_state:
        result = st.session_state["diagnosis_result"]
        predictions = result.get("predictions", [])

        if predictions:
            st.success(f"Analysis complete for **{result.get('crop_type', crop_type).capitalize()}**! Found {len(predictions)} potential disease(s).")
            st.markdown("---")

            for i, pred in enumerate(predictions):
                severity = pred["severity"]
                severity_colors = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢",
                }
                severity_icon = severity_colors.get(severity, "⚪")

                with st.expander(
                    f"#{i+1} — {pred['disease_name']} ({pred['confidence']*100:.0f}% confidence)",
                    expanded=(i == 0),
                ):
                    st.progress(pred["confidence"], text=f"Confidence: {pred['confidence']*100:.1f}%")

                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown(f"**Severity:**")
                    with col2:
                        st.markdown(f"{severity_icon} **{severity.upper()}**")

                    st.markdown(f"**Treatment:**\n{pred['treatment']}")
                    st.markdown(f"**Prevention:**\n{pred['prevention']}")

            st.markdown("---")
            st.subheader("Save Diagnosis")

            top_pred = predictions[0]
            if st.button("💾 Save Top Diagnosis to Crop Log", use_container_width=True):
                try:
                    execute_query(
                        """INSERT INTO crops (user_id, crop_name, disease_detected, treatment, date_logged)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (
                            user_id,
                            result.get("crop_type", crop_type),
                            top_pred["disease_name"],
                            top_pred["treatment"],
                            datetime.now(),
                        ),
                    )
                    st.success(f"Diagnosis saved: **{top_pred['disease_name']}** for {result.get('crop_type', crop_type).capitalize()}")
                    del st.session_state["diagnosis_result"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save diagnosis: {e}")
