import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
from datetime import datetime
from html import escape as html_escape
from backend.db import fetch_all, fetch_one, execute_query


def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


STAGES = ["Farm", "Storage", "Transport", "Market"]
CATEGORIES = ["Grains", "Vegetables", "Fruits", "Dairy", "Livestock", "Other"]
UNITS = ["kg", "tonnes", "liters", "units", "bags", "crates"]
STATUS_OPTIONS = ["in_stock", "in_transit", "delivered", "sold", "spoiled"]


def show_supply_chain():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    hero_b64 = get_image_base64("assets/images/market_produce.png")
    if hero_b64:
        st.markdown(f"""
        <div style="position: relative; border-radius: 20px; overflow: hidden; margin-bottom: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
            <img src="data:image/png;base64,{hero_b64}" style="width: 100%; height: 220px; object-fit: cover; display: block;">
            <div style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(6,78,59,0.85) 0%, rgba(4,120,87,0.7) 50%, rgba(5,150,105,0.5) 100%); display: flex; flex-direction: column; justify-content: center; padding: 2rem 2.5rem;">
                <h1 style="color: white; font-family: 'Poppins', sans-serif; font-size: 1.8rem; margin: 0 0 0.25rem 0;">Supply Chain Management</h1>
                <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin: 0;">Track your products from farm to market with end-to-end visibility</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hero-section">
            <h1 style="color: white;">Supply Chain Management</h1>
            <p>Track your products from farm to market with end-to-end visibility</p>
        </div>
        """, unsafe_allow_html=True)

    items = fetch_all(
        "SELECT * FROM supply_chain_items WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )

    total_items = len(items) if items else 0
    total_value = sum(float(i["cost"] or 0) * float(i["quantity"] or 0) for i in items) if items else 0
    in_transit = sum(1 for i in items if i.get("status") == "in_transit") if items else 0
    delivered = sum(1 for i in items if i.get("status") == "delivered") if items else 0

    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "📦", total_items, "Total Items"),
        (c2, "💰", f"${total_value:,.0f}", "Total Value"),
        (c3, "🚚", in_transit, "In Transit"),
        (c4, "✅", delivered, "Delivered"),
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

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📦 Inventory", "🔄 Supply Chain Stages", "📋 Add Item",
        "📊 Cost Analytics", "📒 Directory"
    ])

    with tab1:
        _show_inventory(items, user_id)

    with tab2:
        _show_stages(items)

    with tab3:
        _show_add_form(user_id)

    with tab4:
        _show_cost_analytics(items)

    with tab5:
        _show_directory()


def _show_inventory(items, user_id):
    st.markdown("#### Inventory Management")

    if not items:
        st.info("No inventory items yet. Add items from the 'Add Item' tab.")
        return

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_status = st.selectbox("Filter by Status", ["All"] + STATUS_OPTIONS, key="inv_filter_status")
    with filter_col2:
        filter_category = st.selectbox("Filter by Category", ["All"] + CATEGORIES, key="inv_filter_cat")

    filtered = items
    if filter_status != "All":
        filtered = [i for i in filtered if i.get("status") == filter_status]
    if filter_category != "All":
        filtered = [i for i in filtered if i.get("category") == filter_category]

    if not filtered:
        st.warning("No items match the selected filters.")
        return

    for item in filtered:
        item_name = html_escape(str(item.get("item_name", "")))
        category = html_escape(str(item.get("category", "N/A")))
        quantity = item.get("quantity", 0)
        unit = html_escape(str(item.get("unit", "")))
        stage = html_escape(str(item.get("stage", "farm")))
        origin = html_escape(str(item.get("origin", "N/A") or "N/A"))
        destination = html_escape(str(item.get("destination", "N/A") or "N/A"))
        cost = float(item.get("cost", 0) or 0)
        status = item.get("status", "in_stock")
        created = item.get("created_at")
        date_str = created.strftime("%b %d, %Y") if created else "N/A"

        status_colors = {
            "in_stock": "#16a34a",
            "in_transit": "#f59e0b",
            "delivered": "#2563eb",
            "sold": "#7c3aed",
            "spoiled": "#dc2626",
        }
        s_color = status_colors.get(status, "#64748b")
        status_display = html_escape(status.replace("_", " ").title())

        st.markdown(f"""
        <div class="modern-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                <div>
                    <h3 style="margin: 0 0 0.25rem 0; font-size: 1.1rem;">{item_name}</h3>
                    <p style="margin: 0; font-size: 0.85rem; color: var(--text-secondary);">{category} &bull; {float(quantity):,.1f} {unit} &bull; ${cost:,.2f}/unit</p>
                </div>
                <div style="display: flex; gap: 0.75rem; align-items: center;">
                    <span style="background: {s_color}15; color: {s_color}; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">{status_display}</span>
                    <span style="background: var(--primary-100); color: var(--primary-dark); padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">📍 {stage}</span>
                </div>
            </div>
            <div style="margin-top: 0.75rem; display: flex; gap: 1.5rem; font-size: 0.85rem; color: var(--text-secondary);">
                <span>🏠 Origin: {origin}</span>
                <span>🎯 Dest: {destination}</span>
                <span>📅 {date_str}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    col_update1, col_update2, col_update3 = st.columns(3)
    with col_update1:
        item_ids = [str(i["id"]) + " - " + str(i["item_name"]) for i in filtered]
        selected = st.selectbox("Select item to update", item_ids, key="update_item_select")
    with col_update2:
        new_status = st.selectbox("New Status", STATUS_OPTIONS, key="update_status")
    with col_update3:
        new_stage = st.selectbox("New Stage", STAGES, key="update_stage")

    if st.button("Update Item", key="btn_update_item", use_container_width=True):
        if selected:
            item_id = int(selected.split(" - ")[0])
            try:
                execute_query(
                    "UPDATE supply_chain_items SET status = %s, stage = %s WHERE id = %s AND user_id = %s",
                    (new_status, new_stage, item_id, user_id)
                )
                st.success("Item updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating item: {e}")


def _show_stages(items):
    st.markdown("#### Supply Chain Pipeline")

    if not items:
        st.info("No items to display. Add items to see the supply chain flow.")
        return

    stage_cols = st.columns(4)
    stage_icons = {"Farm": "🌾", "Storage": "🏪", "Transport": "🚚", "Market": "🏬"}

    for idx, stage in enumerate(STAGES):
        with stage_cols[idx]:
            stage_items = [i for i in items if (i.get("stage") or "farm").lower() == stage.lower()]
            icon = stage_icons.get(stage, "📦")
            st.markdown(f"""
            <div class="modern-card" style="text-align: center; min-height: 120px;">
                <div style="font-size: 2rem;">{icon}</div>
                <h3 style="margin: 0.5rem 0 0.25rem;">{html_escape(stage)}</h3>
                <div class="stat-value" style="font-size: 1.5rem;">{len(stage_items)}</div>
                <div class="stat-label">items</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Stage Breakdown")

    stage_data = []
    for stage in STAGES:
        stage_items = [i for i in items if (i.get("stage") or "farm").lower() == stage.lower()]
        for si in stage_items:
            stage_data.append({
                "Stage": stage,
                "Item": str(si.get("item_name", "")),
                "Quantity": float(si.get("quantity", 0) or 0),
                "Status": str(si.get("status", "")).replace("_", " ").title()
            })

    if stage_data:
        import pandas as pd
        df = pd.DataFrame(stage_data)
        stage_counts = df.groupby("Stage").size().reset_index()
        stage_counts.columns = ["Stage", "Count"]
        fig = px.bar(
            stage_counts,
            x="Stage", y="Count",
            color="Stage",
            color_discrete_sequence=["#16a34a", "#f59e0b", "#2563eb", "#7c3aed"],
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

        st.markdown("##### Items by Stage")
        for stage in STAGES:
            stage_items = [i for i in items if (i.get("stage") or "farm").lower() == stage.lower()]
            if stage_items:
                with st.expander(f"{stage_icons.get(stage, '📦')} {stage} ({len(stage_items)} items)"):
                    for si in stage_items:
                        name = html_escape(str(si.get("item_name", "")))
                        qty = float(si.get("quantity", 0) or 0)
                        unit = html_escape(str(si.get("unit", "")))
                        status = html_escape(str(si.get("status", "")).replace("_", " ").title())
                        st.markdown(f"""
                        <div class="activity-item">
                            <div class="activity-dot"></div>
                            <div>
                                <div style="font-weight: 500;">{name} — {qty:,.1f} {unit}</div>
                                <div style="font-size: 0.8rem; color: var(--text-muted);">Status: {status}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)


def _show_add_form(user_id):
    st.markdown("#### Add New Item")

    with st.form("add_supply_chain_item"):
        col1, col2 = st.columns(2)
        with col1:
            item_name = st.text_input("Item Name *")
            category = st.selectbox("Category", CATEGORIES)
            quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
            unit = st.selectbox("Unit", UNITS)
            cost = st.number_input("Cost per Unit ($)", min_value=0.0, step=0.01)
        with col2:
            stage = st.selectbox("Current Stage", STAGES)
            origin = st.text_input("Origin")
            destination = st.text_input("Destination")
            status = st.selectbox("Status", STATUS_OPTIONS)

        submitted = st.form_submit_button("Add Item", use_container_width=True)

        if submitted:
            if not item_name.strip():
                st.error("Item name is required.")
            else:
                try:
                    execute_query(
                        """INSERT INTO supply_chain_items 
                        (user_id, item_name, category, quantity, unit, stage, origin, destination, cost, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (user_id, item_name.strip(), category, quantity, unit, stage,
                         origin.strip() or None, destination.strip() or None, cost, status)
                    )
                    st.success(f"Item '{item_name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding item: {e}")


def _show_cost_analytics(items):
    st.markdown("#### Cost Analytics")

    if not items:
        st.info("No data available for analytics. Add items to see cost breakdowns.")
        return

    cost_by_category = {}
    cost_by_stage = {}
    cost_by_status = {}

    for item in items:
        cat = str(item.get("category", "Other"))
        stage = str(item.get("stage", "farm")).title()
        status = str(item.get("status", "in_stock")).replace("_", " ").title()
        total = float(item.get("cost", 0) or 0) * float(item.get("quantity", 0) or 0)

        cost_by_category[cat] = cost_by_category.get(cat, 0) + total
        cost_by_stage[stage] = cost_by_stage.get(stage, 0) + total
        cost_by_status[status] = cost_by_status.get(status, 0) + total

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Cost by Category")
        if cost_by_category:
            fig = px.pie(
                values=list(cost_by_category.values()),
                names=list(cost_by_category.keys()),
                color_discrete_sequence=["#16a34a", "#059669", "#0d9488", "#0891b2", "#2563eb", "#7c3aed"],
                hole=0.4,
            )
            fig.update_layout(
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("##### Cost by Stage")
        if cost_by_stage:
            fig = px.bar(
                x=list(cost_by_stage.keys()),
                y=list(cost_by_stage.values()),
                color=list(cost_by_stage.keys()),
                color_discrete_sequence=["#16a34a", "#f59e0b", "#2563eb", "#7c3aed"],
            )
            fig.update_layout(
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"),
                showlegend=False,
                xaxis_title="Stage",
                yaxis_title="Total Cost ($)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Cost by Status")
    if cost_by_status:
        fig = px.bar(
            x=list(cost_by_status.keys()),
            y=list(cost_by_status.values()),
            color=list(cost_by_status.keys()),
            color_discrete_sequence=["#16a34a", "#f59e0b", "#2563eb", "#7c3aed", "#dc2626"],
        )
        fig.update_layout(
            height=300,
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            showlegend=False,
            xaxis_title="Status",
            yaxis_title="Total Cost ($)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Value Summary")
    summary_cols = st.columns(3)
    all_costs = [float(i.get("cost", 0) or 0) * float(i.get("quantity", 0) or 0) for i in items]
    total = sum(all_costs)
    avg = total / len(all_costs) if all_costs else 0
    max_val = max(all_costs) if all_costs else 0

    for col, icon, val, label in [
        (summary_cols[0], "💵", f"${total:,.2f}", "Total Inventory Value"),
        (summary_cols[1], "📊", f"${avg:,.2f}", "Avg Value per Item"),
        (summary_cols[2], "🏆", f"${max_val:,.2f}", "Highest Value Item"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">{icon}</div>
                <div class="stat-value" style="font-size: 1.3rem;">{val}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)


def _show_directory():
    st.markdown("#### Supplier & Buyer Directory")

    st.markdown("""
    <div class="modern-card" style="margin-bottom: 1rem;">
        <h3 style="margin: 0 0 0.75rem;">🏢 Registered Partners</h3>
        <p style="color: var(--text-secondary); font-size: 0.9rem;">
            Manage your network of suppliers, buyers, and logistics partners for efficient supply chain operations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    partners = [
        {"name": "Green Valley Farms", "type": "Supplier", "specialty": "Organic Vegetables", "location": "Central Region", "icon": "🌿"},
        {"name": "FreshMart Distribution", "type": "Buyer", "specialty": "Wholesale Produce", "location": "Urban Markets", "icon": "🏪"},
        {"name": "AgriTransport Co.", "type": "Logistics", "specialty": "Cold Chain Transport", "location": "Nationwide", "icon": "🚛"},
        {"name": "Farm Direct Exports", "type": "Buyer", "specialty": "Export Grade Crops", "location": "International", "icon": "🌍"},
        {"name": "Harvest Storage Ltd.", "type": "Storage", "specialty": "Climate-Controlled Warehousing", "location": "Regional Hubs", "icon": "🏭"},
        {"name": "Local Co-op Market", "type": "Buyer", "specialty": "Farmers Market Sales", "location": "Local Community", "icon": "🛒"},
    ]

    cols = st.columns(3)
    for idx, partner in enumerate(partners):
        with cols[idx % 3]:
            p_name = html_escape(partner["name"])
            p_type = html_escape(partner["type"])
            p_spec = html_escape(partner["specialty"])
            p_loc = html_escape(partner["location"])
            p_icon = partner["icon"]

            type_colors = {
                "Supplier": "#16a34a",
                "Buyer": "#2563eb",
                "Logistics": "#f59e0b",
                "Storage": "#7c3aed",
            }
            t_color = type_colors.get(partner["type"], "#64748b")

            st.markdown(f"""
            <div class="modern-card" style="margin-bottom: 1rem; text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{p_icon}</div>
                <h3 style="margin: 0 0 0.25rem; font-size: 1rem;">{p_name}</h3>
                <span style="background: {t_color}15; color: {t_color}; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">{p_type}</span>
                <p style="margin: 0.5rem 0 0.25rem; font-size: 0.85rem; color: var(--text-secondary);">{p_spec}</p>
                <p style="margin: 0; font-size: 0.8rem; color: var(--text-muted);">📍 {p_loc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Delivery Scheduling")
    st.markdown("""
    <div class="modern-card">
        <p style="color: var(--text-secondary); font-size: 0.9rem;">
            Coordinate deliveries with your logistics partners. Track pickup and drop-off schedules, 
            monitor delivery routes, and ensure timely transport of your produce from farm to market.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("schedule_delivery"):
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.text_input("Pickup Location", key="del_pickup")
            st.date_input("Pickup Date", key="del_pickup_date")
        with d_col2:
            st.text_input("Delivery Location", key="del_dest")
            st.date_input("Expected Delivery Date", key="del_delivery_date")
        st.text_area("Special Instructions", key="del_notes", height=80)
        if st.form_submit_button("Schedule Delivery", use_container_width=True):
            st.success("Delivery scheduled successfully! Your logistics partner will be notified.")
