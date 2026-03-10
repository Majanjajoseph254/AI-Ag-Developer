import streamlit as st
from html import escape as html_escape
from backend.auth import update_user_profile, change_user_password, get_user_by_id
from backend.db import fetch_all, fetch_one


def show_profile():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    fresh_user = get_user_by_id(user_id)
    if fresh_user:
        user = fresh_user

    safe_name = html_escape(user.get("name", "U"))
    safe_role = html_escape(user.get("role", "farmer"))
    safe_email = html_escape(user.get("email", ""))
    initials = "".join([w[0].upper() for w in safe_name.split()[:2]])

    st.markdown(f"""
    <div class="page-header">
        <h1>My Profile</h1>
        <p>Manage your account settings and preferences</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 2], gap="large")

    with col_left:
        st.markdown(f"""
        <div class="profile-section" style="text-align: center;">
            <div class="profile-avatar">{initials}</div>
            <h3 style="border: none; text-align: center; padding-bottom: 0;">{safe_name}</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem;">{safe_role.capitalize()}</p>
            <p style="color: var(--text-muted); font-size: 0.85rem;">{safe_email}</p>
        </div>
        """, unsafe_allow_html=True)

        total_crops = fetch_one("SELECT COUNT(*) as count FROM crops WHERE user_id = %s", (user_id,))
        total_posts = fetch_one("SELECT COUNT(*) as count FROM community_posts WHERE user_id = %s", (user_id,))
        total_listings = fetch_one("SELECT COUNT(*) as count FROM market WHERE user_id = %s", (user_id,))

        st.markdown(f"""
        <div class="profile-section">
            <h3>Activity Summary</h3>
            <div style="display: flex; justify-content: space-around; text-align: center;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-dark);">{total_crops['count'] if total_crops else 0}</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">Crops</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-dark);">{total_posts['count'] if total_posts else 0}</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">Posts</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-dark);">{total_listings['count'] if total_listings else 0}</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">Listings</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        badges = fetch_all("SELECT badge_name, description, earned_at FROM badges WHERE user_id = %s ORDER BY earned_at DESC", (user_id,))
        if badges:
            badge_html = "".join([f'<span class="badge-pill">{html_escape(b["badge_name"])}</span>' for b in badges])
            st.markdown(f"""
            <div class="profile-section">
                <h3>Badges</h3>
                {badge_html}
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        tab_info, tab_security = st.tabs(["Personal Information", "Security"])

        with tab_info:
            with st.form("profile_form"):
                st.markdown("##### Edit Profile")
                col_n, col_e = st.columns(2)
                with col_n:
                    name = st.text_input("Full Name", value=user.get("name", ""))
                with col_e:
                    email = st.text_input("Email", value=user.get("email", ""))

                col_p, col_l = st.columns(2)
                with col_p:
                    phone = st.text_input("Phone Number", value=user.get("phone", "") or "", placeholder="+254 7XX XXX XXX")
                with col_l:
                    location = st.text_input("Location", value=user.get("location", "") or "", placeholder="e.g., Kiambu County")

                role = st.selectbox(
                    "Role",
                    ["farmer", "buyer", "agronomist"],
                    index=["farmer", "buyer", "agronomist"].index(user.get("role", "farmer")) if user.get("role", "farmer") in ["farmer", "buyer", "agronomist"] else 0,
                    format_func=lambda x: x.capitalize(),
                )

                bio = st.text_area("Bio", value=user.get("bio", "") or "", placeholder="Tell us about yourself and your farming experience...", height=100)

                save_btn = st.form_submit_button("Save Changes", use_container_width=True)

                if save_btn:
                    if not name or not email:
                        st.error("Name and email are required.")
                    else:
                        try:
                            updated_user = update_user_profile(user_id, name, email, phone or None, location or None, bio or None, role)
                            if updated_user:
                                st.session_state["user"] = updated_user
                                st.success("Profile updated successfully!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error updating profile: {e}")

        with tab_security:
            st.markdown("##### Change Password")
            with st.form("password_form"):
                current_pw = st.text_input("Current Password", type="password", placeholder="Enter current password")
                col_np, col_cp = st.columns(2)
                with col_np:
                    new_pw = st.text_input("New Password", type="password", placeholder="Enter new password")
                with col_cp:
                    confirm_pw = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")

                change_btn = st.form_submit_button("Update Password", use_container_width=True)

                if change_btn:
                    if not current_pw or not new_pw or not confirm_pw:
                        st.error("Please fill in all password fields.")
                    elif new_pw != confirm_pw:
                        st.error("New passwords do not match.")
                    elif len(new_pw) < 6:
                        st.error("New password must be at least 6 characters.")
                    else:
                        success, message = change_user_password(user_id, current_pw, new_pw)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

            st.markdown("---")
            st.markdown("##### Account Information")
            joined = user.get("created_at")
            joined_str = joined.strftime("%B %d, %Y") if joined else "N/A"
            st.markdown(f"""
            <div style="background: var(--primary-50); padding: 1rem; border-radius: 10px; border: 1px solid var(--primary-100);">
                <p style="margin: 0; font-size: 0.9rem;"><strong>Member since:</strong> {joined_str}</p>
                <p style="margin: 0.25rem 0 0; font-size: 0.9rem;"><strong>Account ID:</strong> #{user_id}</p>
            </div>
            """, unsafe_allow_html=True)
