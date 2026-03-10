import streamlit as st
import json
from backend.crop_recognition import classify_plant, identify_crop, extract_features
from backend.ai_disease import analyze_image
from backend.db import execute_query
from datetime import datetime


def _save_recognition_log(user_id, is_plant, plant_confidence, crop_type, crop_confidence, features):
    try:
        execute_query(
            """INSERT INTO crop_recognition_logs 
               (user_id, is_plant, plant_confidence, predicted_crop, crop_confidence, image_features, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                user_id,
                is_plant,
                plant_confidence,
                crop_type,
                crop_confidence,
                json.dumps(features) if features else None,
                datetime.now(),
            ),
        )
    except Exception as e:
        st.toast(f"Could not save recognition log: {e}", icon="⚠️")


def show_crop_diagnosis():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    st.title("🔬 Crop Disease Diagnosis")
    st.markdown("Upload or capture a photo of your crop to detect potential diseases using AI analysis.")

    st.markdown("### 📸 Provide a Crop Image")
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
        st.session_state["diagnosis_image_bytes"] = image_bytes
        st.image(image_bytes, caption="Captured/Uploaded Image", width=300)

        if st.button("🔍 Analyze Image", type="primary", use_container_width=True):
            with st.spinner("Step 1/3: Detecting plant in image..."):
                plant_result = classify_plant(image_bytes)

            if plant_result.get("error"):
                st.error(plant_result["error"])
                return

            st.session_state["plant_result"] = plant_result
            st.session_state.pop("crop_result", None)
            st.session_state.pop("diagnosis_result", None)
            st.session_state.pop("selected_crop_override", None)

            if plant_result["is_plant"]:
                with st.spinner("Step 2/3: Identifying crop type..."):
                    crop_result = identify_crop(image_bytes)
                st.session_state["crop_result"] = crop_result

                detected_crop = crop_result["crop_type"]
                with st.spinner("Step 3/3: Analyzing for diseases..."):
                    disease_result = analyze_image(image_bytes, detected_crop)
                st.session_state["diagnosis_result"] = disease_result
                st.session_state["analysis_crop_type"] = detected_crop

            features = plant_result.get("features", {})
            _save_recognition_log(
                user_id,
                plant_result["is_plant"],
                plant_result["confidence"],
                st.session_state.get("crop_result", {}).get("crop_type"),
                st.session_state.get("crop_result", {}).get("confidence"),
                features,
            )

    plant_result = st.session_state.get("plant_result")
    if plant_result is None:
        return

    st.markdown("---")
    st.subheader("🔬 Analysis Pipeline")

    st.markdown("#### Step 1: Plant Detection")
    if plant_result["is_plant"]:
        st.success(f"✅ This image **contains a plant** (Confidence: {plant_result['confidence']*100:.1f}%)")
        st.progress(plant_result["confidence"], text=f"Plant confidence: {plant_result['confidence']*100:.1f}%")
    else:
        st.warning(
            f"⚠️ This image **does not appear to contain a plant/crop** "
            f"(Confidence: {plant_result['confidence']*100:.1f}%). "
            f"Please upload a different image showing a plant or crop for diagnosis."
        )
        st.progress(plant_result["confidence"], text=f"Non-plant confidence: {plant_result['confidence']*100:.1f}%")

        with st.expander("🔍 Recognition Details"):
            features = plant_result.get("features", {})
            if features:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**Color Features**")
                    st.write(f"R mean: {features.get('r_mean', 'N/A')}")
                    st.write(f"G mean: {features.get('g_mean', 'N/A')}")
                    st.write(f"B mean: {features.get('b_mean', 'N/A')}")
                    st.write(f"Green ratio: {features.get('green_ratio', 'N/A')}")
                with col2:
                    st.markdown("**Texture Features**")
                    st.write(f"Edge density: {features.get('edge_density', 'N/A')}")
                    st.write(f"Contrast: {features.get('contrast', 'N/A')}")
                    st.write(f"Uniformity: {features.get('uniformity', 'N/A')}")
                with col3:
                    st.markdown("**Shape & HSV Features**")
                    st.write(f"Hue mean: {features.get('hue_mean', 'N/A')}")
                    st.write(f"Saturation mean: {features.get('sat_mean', 'N/A')}")
                    st.write(f"Aspect ratio: {features.get('aspect_ratio', 'N/A')}")
                    st.write(f"Symmetry: {features.get('symmetry', 'N/A')}")
        return

    crop_result = st.session_state.get("crop_result")
    if crop_result is None:
        return

    st.markdown("#### Step 2: Crop Identification")
    detected_crop = crop_result["crop_type"]
    st.info(f"🌱 Identified crop: **{detected_crop.capitalize()}** (Confidence: {crop_result['confidence']*100:.1f}%)")
    st.progress(crop_result["confidence"], text=f"Crop ID confidence: {crop_result['confidence']*100:.1f}%")

    all_preds = crop_result.get("all_predictions", [])
    if all_preds:
        cols = st.columns(len(all_preds))
        for i, pred in enumerate(all_preds):
            with cols[i]:
                conf_pct = pred["confidence"] * 100
                st.metric(pred["crop_type"].capitalize(), f"{conf_pct:.1f}%")

    crop_types = ["maize", "tomatoes", "potatoes", "wheat"]
    default_idx = crop_types.index(detected_crop) if detected_crop in crop_types else 0

    selected_crop = st.selectbox(
        "Crop type (auto-detected, you can override)",
        crop_types,
        index=default_idx,
        format_func=lambda x: x.capitalize(),
        key="crop_type_selector",
    )

    if selected_crop != st.session_state.get("analysis_crop_type"):
        if st.button("🔄 Re-analyze with selected crop type"):
            stored_bytes = st.session_state.get("diagnosis_image_bytes", image_bytes)
            if stored_bytes:
                with st.spinner(f"Re-analyzing for {selected_crop.capitalize()}..."):
                    disease_result = analyze_image(stored_bytes, selected_crop)
                st.session_state["diagnosis_result"] = disease_result
                st.session_state["analysis_crop_type"] = selected_crop
                st.rerun()
            else:
                st.error("Image no longer available. Please upload the image again.")

    st.markdown("#### Step 3: Disease Analysis")

    if "diagnosis_result" in st.session_state:
        result = st.session_state["diagnosis_result"]
        predictions = result.get("predictions", [])
        analysis_crop = st.session_state.get("analysis_crop_type", detected_crop)

        if not result.get("success", True):
            st.error(result.get("error", "Analysis failed"))
            return

        if predictions:
            st.success(
                f"Analysis complete for **{analysis_crop.capitalize()}**! "
                f"Found {len(predictions)} potential disease(s)."
            )

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

            with st.expander("🔍 Recognition Details"):
                features = plant_result.get("features", {})
                if features:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("**Color Features**")
                        st.write(f"R mean: {features.get('r_mean', 'N/A')}")
                        st.write(f"G mean: {features.get('g_mean', 'N/A')}")
                        st.write(f"B mean: {features.get('b_mean', 'N/A')}")
                        st.write(f"R std: {features.get('r_std', 'N/A')}")
                        st.write(f"G std: {features.get('g_std', 'N/A')}")
                        st.write(f"B std: {features.get('b_std', 'N/A')}")
                        st.write(f"Green ratio: {features.get('green_ratio', 'N/A')}")
                    with col2:
                        st.markdown("**Texture Features**")
                        st.write(f"Edge density: {features.get('edge_density', 'N/A')}")
                        st.write(f"Contrast: {features.get('contrast', 'N/A')}")
                        st.write(f"Uniformity: {features.get('uniformity', 'N/A')}")
                    with col3:
                        st.markdown("**Shape & HSV Features**")
                        st.write(f"Hue mean: {features.get('hue_mean', 'N/A')}")
                        st.write(f"Hue std: {features.get('hue_std', 'N/A')}")
                        st.write(f"Saturation mean: {features.get('sat_mean', 'N/A')}")
                        st.write(f"Saturation std: {features.get('sat_std', 'N/A')}")
                        st.write(f"Aspect ratio: {features.get('aspect_ratio', 'N/A')}")
                        st.write(f"Symmetry: {features.get('symmetry', 'N/A')}")

                st.markdown("**Model Outputs:**")
                st.write(f"Plant classification: {'Plant' if plant_result['is_plant'] else 'Non-plant'} ({plant_result['confidence']*100:.1f}%)")
                if crop_result:
                    st.write(f"Crop identification: {crop_result['crop_type'].capitalize()} ({crop_result['confidence']*100:.1f}%)")
                    for p in crop_result.get("all_predictions", []):
                        st.write(f"  - {p['crop_type'].capitalize()}: {p['confidence']*100:.1f}%")

            st.markdown("---")
            st.subheader("💾 Save Diagnosis")

            top_pred = predictions[0]
            if st.button("💾 Save Top Diagnosis to Crop Log", use_container_width=True):
                try:
                    execute_query(
                        """INSERT INTO crops (user_id, crop_name, disease_detected, treatment, date_logged)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (
                            user_id,
                            analysis_crop,
                            top_pred["disease_name"],
                            top_pred["treatment"],
                            datetime.now(),
                        ),
                    )
                    st.success(f"Diagnosis saved: **{top_pred['disease_name']}** for {analysis_crop.capitalize()}")
                    del st.session_state["diagnosis_result"]
                    st.session_state.pop("plant_result", None)
                    st.session_state.pop("crop_result", None)
                    st.session_state.pop("analysis_crop_type", None)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save diagnosis: {e}")
