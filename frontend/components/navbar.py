import streamlit as st
from html import escape as html_escape


def show_navbar():
    with st.sidebar:
        user = st.session_state.get("user", {})
        name = html_escape(user.get("name", "User"))
        role = html_escape(user.get("role", "farmer"))
        initials = "".join([w[0].upper() for w in name.split()[:2]])

        st.markdown(f"""
        <div class="sidebar-profile">
            <div class="sidebar-avatar">{initials}</div>
            <div class="sidebar-name">{name}</div>
            <div class="sidebar-role">{role}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        current_page = st.session_state.get("page", "Dashboard")

        st.markdown("<p style='font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.6; margin-bottom: 0.25rem;'>Main</p>", unsafe_allow_html=True)
        main_pages = [
            ("🏠", "Dashboard"),
            ("🔬", "Crop Diagnosis"),
            ("🌱", "Crop Monitoring"),
            ("🛒", "Market"),
            ("🌤️", "Weather"),
            ("📡", "IoT Dashboard"),
        ]
        for icon, page_name in main_pages:
            is_active = current_page == page_name
            if st.button(f"{icon}  {page_name}", use_container_width=True, key=f"nav_{page_name}", type="primary" if is_active else "secondary"):
                st.session_state["page"] = page_name
                st.rerun()

        st.markdown("<p style='font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.6; margin: 0.75rem 0 0.25rem;'>Smart Farming</p>", unsafe_allow_html=True)
        smart_pages = [
            ("💧", "Smart Irrigation"),
            ("🤖", "Robotics"),
            ("🧬", "Biotech & AI"),
            ("🌿", "Climate Smart"),
            ("📈", "Crop Improvement"),
        ]
        for icon, page_name in smart_pages:
            is_active = current_page == page_name
            if st.button(f"{icon}  {page_name}", use_container_width=True, key=f"nav_{page_name}", type="primary" if is_active else "secondary"):
                st.session_state["page"] = page_name
                st.rerun()

        st.markdown("<p style='font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.6; margin: 0.75rem 0 0.25rem;'>Operations</p>", unsafe_allow_html=True)
        ops_pages = [
            ("🔗", "Blockchain"),
            ("📦", "Supply Chain"),
            ("👷", "Labour"),
            ("♻️", "Sustainability"),
        ]
        for icon, page_name in ops_pages:
            is_active = current_page == page_name
            if st.button(f"{icon}  {page_name}", use_container_width=True, key=f"nav_{page_name}", type="primary" if is_active else "secondary"):
                st.session_state["page"] = page_name
                st.rerun()

        st.markdown("<p style='font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.6; margin: 0.75rem 0 0.25rem;'>Community</p>", unsafe_allow_html=True)
        community_pages = [
            ("🤖", "Chatbot"),
            ("🌍", "Soil & Erosion"),
            ("👥", "Community"),
        ]
        for icon, page_name in community_pages:
            is_active = current_page == page_name
            if st.button(f"{icon}  {page_name}", use_container_width=True, key=f"nav_{page_name}", type="primary" if is_active else "secondary"):
                st.session_state["page"] = page_name
                st.rerun()

        st.markdown("---")

        col_profile, col_logout = st.columns(2)
        with col_profile:
            if st.button("👤 Profile", use_container_width=True, key="nav_profile"):
                st.session_state["page"] = "Profile"
                st.rerun()
        with col_logout:
            if st.button("🚪 Logout", use_container_width=True, key="nav_logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["page"] = "Login"
                st.rerun()
