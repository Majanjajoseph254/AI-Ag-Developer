import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
import uuid
import hashlib
from datetime import datetime
from html import escape as html_escape
from backend.db import fetch_all, fetch_one, execute_query, execute_returning


def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def generate_batch_id():
    return f"BATCH-{uuid.uuid4().hex[:8].upper()}"


def generate_tx_hash(data_str):
    return "0x" + hashlib.sha256(data_str.encode()).hexdigest()[:40]


STAGES = ["Harvested", "Processed", "Transported", "Sold"]
STAGE_ICONS = {
    "Harvested": "🌾",
    "Processed": "🏭",
    "Transported": "🚛",
    "Sold": "🛒",
}


def show_blockchain():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    hero_b64 = get_image_base64("assets/images/farm_aerial.png")
    if hero_b64:
        st.markdown(f"""
        <div style="position: relative; border-radius: 20px; overflow: hidden; margin-bottom: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
            <img src="data:image/png;base64,{hero_b64}" style="width: 100%; height: 220px; object-fit: cover; display: block;">
            <div style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(6,78,59,0.85) 0%, rgba(4,120,87,0.7) 50%, rgba(5,150,105,0.5) 100%); display: flex; flex-direction: column; justify-content: center; padding: 2rem 2.5rem;">
                <h1 style="color: white; font-family: 'Poppins', sans-serif; font-size: 1.8rem; margin: 0 0 0.25rem 0;">🔗 Blockchain Traceability</h1>
                <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin: 0;">Track your produce from farm to table with transparent, verifiable records</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hero-section">
            <h1 style="color: white;">🔗 Blockchain Traceability</h1>
            <p>Track your produce from farm to table with transparent, verifiable records</p>
        </div>
        """, unsafe_allow_html=True)

    total_batches_row = fetch_one(
        "SELECT COUNT(DISTINCT batch_id) as count FROM blockchain_records WHERE user_id = %s", (user_id,)
    )
    verified_row = fetch_one(
        "SELECT COUNT(*) as count FROM blockchain_records WHERE user_id = %s AND verified = true", (user_id,)
    )
    total_records_row = fetch_one(
        "SELECT COUNT(*) as count FROM blockchain_records WHERE user_id = %s", (user_id,)
    )
    sold_row = fetch_one(
        "SELECT COUNT(DISTINCT batch_id) as count FROM blockchain_records WHERE user_id = %s AND stage = 'Sold'", (user_id,)
    )

    total_batches = total_batches_row["count"] if total_batches_row else 0
    verified_count = verified_row["count"] if verified_row else 0
    total_records = total_records_row["count"] if total_records_row else 0
    sold_count = sold_row["count"] if sold_row else 0

    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "📦", total_batches, "Total Batches"),
        (c2, "✅", verified_count, "Verified Records"),
        (c3, "📝", total_records, "Total Transactions"),
        (c4, "🛒", sold_count, "Completed (Sold)"),
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

    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Batch Record", "📋 Transaction Ledger", "🔍 Batch Timeline", "📊 Analytics"])

    with tab1:
        st.markdown("#### Add New Batch Record")
        st.markdown('<div class="modern-card" style="margin-bottom: 1rem;">', unsafe_allow_html=True)

        with st.form("add_blockchain_record", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                use_existing = st.checkbox("Use existing Batch ID")
                if use_existing:
                    existing_batches = fetch_all(
                        "SELECT DISTINCT batch_id FROM blockchain_records WHERE user_id = %s ORDER BY batch_id",
                        (user_id,),
                    )
                    batch_options = [r["batch_id"] for r in existing_batches] if existing_batches else []
                    if batch_options:
                        batch_id = st.selectbox("Select Batch ID", batch_options)
                    else:
                        st.info("No existing batches found. A new one will be generated.")
                        batch_id = None
                else:
                    batch_id = None

                crop_name = st.text_input("Crop Name", placeholder="e.g. Maize, Tomato, Wheat")
            with col_b:
                stage = st.selectbox("Stage", STAGES)
                location = st.text_input("Location", placeholder="e.g. Farm A, Processing Plant, Market")

            notes = st.text_area("Notes (optional)", placeholder="Additional details about this stage...")
            verified = st.checkbox("Mark as Verified")

            submitted = st.form_submit_button("Add Record", use_container_width=True)
            if submitted:
                if not crop_name.strip():
                    st.error("Please enter a crop name.")
                else:
                    final_batch_id = batch_id if batch_id else generate_batch_id()
                    tx_data = f"{final_batch_id}-{crop_name}-{stage}-{location}-{datetime.now().isoformat()}"
                    tx_hash = generate_tx_hash(tx_data)

                    execute_query(
                        """INSERT INTO blockchain_records (user_id, batch_id, crop_name, stage, location, verified, tx_hash, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                        (user_id, final_batch_id, crop_name.strip(), stage, location.strip(), verified, tx_hash, notes.strip()),
                    )
                    st.success(f"Record added! Batch ID: **{final_batch_id}** | TX: `{tx_hash[:18]}...`")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("#### Transaction Ledger")
        records = fetch_all(
            """SELECT id, batch_id, crop_name, stage, location, verified, tx_hash, notes, created_at
            FROM blockchain_records WHERE user_id = %s ORDER BY created_at DESC""",
            (user_id,),
        )

        if records:
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                stage_filter = st.selectbox("Filter by Stage", ["All"] + STAGES, key="ledger_stage_filter")
            with filter_col2:
                verified_filter = st.selectbox("Filter by Verification", ["All", "Verified", "Unverified"], key="ledger_verified_filter")

            filtered = records
            if stage_filter != "All":
                filtered = [r for r in filtered if r["stage"] == stage_filter]
            if verified_filter == "Verified":
                filtered = [r for r in filtered if r["verified"]]
            elif verified_filter == "Unverified":
                filtered = [r for r in filtered if not r["verified"]]

            if filtered:
                for r in filtered:
                    batch_id_safe = html_escape(str(r["batch_id"]))
                    crop_safe = html_escape(str(r["crop_name"]))
                    stage_safe = html_escape(str(r["stage"]))
                    location_safe = html_escape(str(r["location"] or "N/A"))
                    tx_safe = html_escape(str(r["tx_hash"] or ""))
                    notes_safe = html_escape(str(r["notes"] or ""))
                    verified_badge = '<span style="background: #dcfce7; color: #16a34a; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">✅ Verified</span>' if r["verified"] else '<span style="background: #fef3c7; color: #d97706; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">⏳ Pending</span>'
                    stage_icon = STAGE_ICONS.get(r["stage"], "📦")
                    date_str = r["created_at"].strftime("%b %d, %Y at %H:%M") if r.get("created_at") else ""
                    notes_html = f'<div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">📝 {notes_safe}</div>' if notes_safe else ""

                    st.markdown(f"""
                    <div class="activity-item" style="padding: 1rem 0;">
                        <div style="font-size: 1.5rem; margin-top: 0.25rem;">{stage_icon}</div>
                        <div style="flex: 1;">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                                <div>
                                    <span style="font-weight: 600; font-size: 1rem;">{crop_safe}</span>
                                    <span style="color: var(--text-muted); font-size: 0.85rem;"> — {stage_safe}</span>
                                </div>
                                {verified_badge}
                            </div>
                            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 2px;">
                                <strong>Batch:</strong> {batch_id_safe} &nbsp;|&nbsp; <strong>Location:</strong> {location_safe}
                            </div>
                            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px; font-family: monospace;">
                                TX: {tx_safe}
                            </div>
                            {notes_html}
                            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">{date_str}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                col_v1, col_v2 = st.columns([3, 1])
                with col_v2:
                    with st.expander("Verify / Update Records"):
                        unverified = [r for r in records if not r["verified"]]
                        if unverified:
                            record_options = {f"{r['batch_id']} - {r['crop_name']} ({r['stage']})": r["id"] for r in unverified}
                            selected = st.selectbox("Select record to verify", list(record_options.keys()))
                            if st.button("✅ Verify Record", use_container_width=True):
                                execute_query(
                                    "UPDATE blockchain_records SET verified = true WHERE id = %s AND user_id = %s",
                                    (record_options[selected], user_id),
                                )
                                st.success("Record verified!")
                                st.rerun()
                        else:
                            st.info("All records are verified!")
            else:
                st.info("No records match the selected filters.")
        else:
            st.info("No transaction records yet. Add your first batch record above.")

    with tab3:
        st.markdown("#### Batch History Timeline")
        batches = fetch_all(
            "SELECT DISTINCT batch_id FROM blockchain_records WHERE user_id = %s ORDER BY batch_id",
            (user_id,),
        )

        if batches:
            batch_options = [b["batch_id"] for b in batches]
            selected_batch = st.selectbox("Select Batch", batch_options, key="timeline_batch")

            batch_records = fetch_all(
                """SELECT batch_id, crop_name, stage, location, verified, tx_hash, notes, created_at
                FROM blockchain_records WHERE user_id = %s AND batch_id = %s ORDER BY created_at ASC""",
                (user_id, selected_batch),
            )

            if batch_records:
                crop_name_display = html_escape(batch_records[0]["crop_name"])
                st.markdown(f"""
                <div class="modern-card" style="margin-bottom: 1rem;">
                    <h3 style="margin: 0 0 0.5rem 0;">📦 Batch: {html_escape(str(selected_batch))}</h3>
                    <p style="margin: 0; color: var(--text-secondary);">Crop: <strong>{crop_name_display}</strong> &nbsp;|&nbsp; {len(batch_records)} stage(s) recorded</p>
                </div>
                """, unsafe_allow_html=True)

                stage_order = {s: i for i, s in enumerate(STAGES)}
                completed_stages = {r["stage"] for r in batch_records}

                progress_items = ""
                for stage_name in STAGES:
                    icon = STAGE_ICONS[stage_name]
                    if stage_name in completed_stages:
                        rec = next((r for r in batch_records if r["stage"] == stage_name), None)
                        date_text = rec["created_at"].strftime("%b %d, %Y %H:%M") if rec and rec.get("created_at") else ""
                        loc_text = html_escape(str(rec["location"] or "")) if rec else ""
                        verified_text = "✅ Verified" if rec and rec["verified"] else "⏳ Pending"
                        color = "#16a34a"
                        bg = "#f0fdf4"
                        border_color = "#16a34a"
                    else:
                        date_text = ""
                        loc_text = ""
                        verified_text = "Not reached"
                        color = "#94a3b8"
                        bg = "#f8fafc"
                        border_color = "#e2e8f0"

                    progress_items += f"""
                    <div style="display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 0.75rem;">
                        <div style="width: 40px; height: 40px; border-radius: 50%; background: {bg}; border: 2px solid {border_color}; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0;">{icon}</div>
                        <div style="flex: 1; padding-bottom: 0.75rem; border-bottom: 1px solid var(--border);">
                            <div style="font-weight: 600; color: {color};">{html_escape(stage_name)}</div>
                            <div style="font-size: 0.8rem; color: var(--text-secondary);">{loc_text} {(' — ' + date_text) if date_text else ''}</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted);">{verified_text}</div>
                        </div>
                    </div>
                    """

                st.markdown(f"""
                <div class="modern-card">
                    <h4 style="margin: 0 0 1rem 0;">Journey Timeline</h4>
                    {progress_items}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No batches found. Add a batch record to see the timeline.")

    with tab4:
        st.markdown("#### Supply Chain Transparency Metrics")

        if total_records > 0:
            verification_rate = (verified_count / total_records * 100) if total_records else 0

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-value">{verification_rate:.1f}%</div>
                    <div class="stat-label">Verification Rate</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                completion_rate = (sold_count / total_batches * 100) if total_batches else 0
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">🏁</div>
                    <div class="stat-value">{completion_rate:.1f}%</div>
                    <div class="stat-label">Completion Rate</div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                avg_stages = total_records / total_batches if total_batches else 0
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">📈</div>
                    <div class="stat-value">{avg_stages:.1f}</div>
                    <div class="stat-label">Avg Stages/Batch</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.markdown("##### Records by Stage")
                stage_data = fetch_all(
                    "SELECT stage, COUNT(*) as count FROM blockchain_records WHERE user_id = %s GROUP BY stage ORDER BY count DESC",
                    (user_id,),
                )
                if stage_data:
                    fig = px.bar(
                        x=[r["stage"] for r in stage_data],
                        y=[r["count"] for r in stage_data],
                        color=[r["stage"] for r in stage_data],
                        color_discrete_sequence=["#16a34a", "#059669", "#0d9488", "#0891b2"],
                        labels={"x": "Stage", "y": "Count"},
                    )
                    fig.update_layout(
                        height=300,
                        margin=dict(t=20, b=20, l=20, r=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter"),
                        showlegend=False,
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with col_chart2:
                st.markdown("##### Verification Status")
                unverified_count = total_records - verified_count
                fig = px.pie(
                    values=[verified_count, unverified_count],
                    names=["Verified", "Pending"],
                    color_discrete_sequence=["#16a34a", "#f59e0b"],
                    hole=0.45,
                )
                fig.update_layout(
                    height=300,
                    margin=dict(t=20, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15),
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### Crop Distribution in Supply Chain")
            crop_data = fetch_all(
                "SELECT crop_name, COUNT(*) as count FROM blockchain_records WHERE user_id = %s GROUP BY crop_name ORDER BY count DESC",
                (user_id,),
            )
            if crop_data:
                fig = px.pie(
                    values=[r["count"] for r in crop_data],
                    names=[r["crop_name"] for r in crop_data],
                    color_discrete_sequence=["#16a34a", "#059669", "#0d9488", "#0891b2", "#2563eb", "#7c3aed"],
                    hole=0.4,
                )
                fig.update_layout(
                    height=300,
                    margin=dict(t=20, b=20, l=20, r=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15),
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available yet. Start adding batch records to see analytics.")
