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

        pages = [
            ("🏠", "Dashboard"),
            ("🔬", "Crop Diagnosis"),
            ("🌱", "Crop Monitoring"),
            ("🛒", "Market"),
            ("🌤️", "Weather"),
            ("📡", "IoT Dashboard"),
            ("🤖", "Chatbot"),
            ("🌍", "Soil & Erosion"),
            ("👥", "Community"),
        ]

        current_page = st.session_state.get("page", "Dashboard")

        for icon, page_name in pages:
            is_active = current_page == page_name
            if st.button(
                f"{icon}  {page_name}",
                use_container_width=True,
                key=f"nav_{page_name}",
                type="primary" if is_active else "secondary",
            ):
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
