import streamlit as st
from backend.auth import authenticate_user


def show_login():
    st.markdown("<h1 style='text-align: center;'>🌾 AgriShield AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Welcome Back</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    user = authenticate_user(email, password)
                    if user:
                        st.session_state["user"] = user
                        st.session_state["logged_in"] = True
                        st.session_state["page"] = "Dashboard"
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

        st.markdown("---")
        st.markdown("Don't have an account?")
        if st.button("Sign Up", use_container_width=True):
            st.session_state["page"] = "Signup"
            st.rerun()
