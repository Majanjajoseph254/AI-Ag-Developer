import streamlit as st


def show_navbar():
    with st.sidebar:
        user = st.session_state.get("user", {})
        st.markdown(f"### 👤 {user.get('name', 'User')}")
        st.markdown(f"*Role: {user.get('role', 'farmer').capitalize()}*")
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

        for icon, page_name in pages:
            if st.button(f"{icon} {page_name}", use_container_width=True, key=f"nav_{page_name}"):
                st.session_state["page"] = page_name
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            keys_to_keep = set()
            for key in list(st.session_state.keys()):
                if key not in keys_to_keep:
                    del st.session_state[key]
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.session_state["page"] = "Login"
            st.rerun()
