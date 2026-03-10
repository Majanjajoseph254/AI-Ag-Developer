import streamlit as st
import pandas as pd
from backend.db import execute_query, fetch_all


def show_market():
    st.title("🏪 Market Linkage")

    user_id = st.session_state["user"]["id"]

    tab1, tab2 = st.tabs(["Browse Listings", "Post a Listing"])

    with tab2:
        with st.form("market_listing_form"):
            crop_name = st.text_input("Crop Name", placeholder="e.g. Maize, Beans")
            location = st.text_input("Location", placeholder="e.g. Nairobi, Nakuru")
            price_per_kg = st.number_input("Price per KG (KES)", min_value=0.0, step=1.0)
            contact_info = st.text_input("Contact Info", placeholder="e.g. 0712345678")
            description = st.text_area("Description", placeholder="Describe your produce")
            submitted = st.form_submit_button("Post Listing", use_container_width=True)

            if submitted:
                if not crop_name or not location or not contact_info:
                    st.error("Please fill in crop name, location, and contact info.")
                else:
                    execute_query(
                        """INSERT INTO market (user_id, crop_name, location, price_per_kg,
                           contact_info, description, posted_at)
                           VALUES (%s, %s, %s, %s, %s, %s, NOW())""",
                        (user_id, crop_name, location, price_per_kg, contact_info, description),
                    )
                    st.success("Listing posted successfully!")
                    st.rerun()

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            search_crop = st.text_input("Search by crop", placeholder="e.g. Maize")
        with col2:
            search_location = st.text_input("Search by location", placeholder="e.g. Nairobi")

        query = "SELECT m.*, u.name as seller_name FROM market m JOIN users u ON m.user_id = u.id"
        params = []
        conditions = []

        if search_crop:
            conditions.append("LOWER(m.crop_name) LIKE LOWER(%s)")
            params.append(f"%{search_crop}%")
        if search_location:
            conditions.append("LOWER(m.location) LIKE LOWER(%s)")
            params.append(f"%{search_location}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY m.posted_at DESC"

        listings = fetch_all(query, tuple(params) if params else None)

        if not listings:
            st.info("No listings found. Be the first to post!")
        else:
            for listing in listings:
                with st.container():
                    st.markdown("---")
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"### 🌿 {listing['crop_name']}")
                        st.markdown(f"📍 **Location:** {listing['location']}")
                        st.markdown(f"💰 **Price:** KES {listing['price_per_kg']}/kg")
                        st.markdown(f"👤 **Seller:** {listing['seller_name']}")
                        if listing.get("description"):
                            st.markdown(f"📝 {listing['description']}")
                        st.markdown(f"📞 **Contact:** {listing['contact_info']}")
                        if listing.get("posted_at"):
                            st.caption(f"Posted: {listing['posted_at']}")
                    with col_b:
                        if listing["user_id"] == user_id:
                            if st.button("🗑️ Delete", key=f"del_{listing['id']}"):
                                execute_query(
                                    "DELETE FROM market WHERE id = %s AND user_id = %s",
                                    (listing["id"], user_id),
                                )
                                st.success("Listing deleted.")
                                st.rerun()
