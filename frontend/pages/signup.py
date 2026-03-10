import streamlit as st
from backend.auth import create_user
from backend.db import fetch_one


def show_signup():
    st.markdown("<h1 style='text-align: center;'>🌾 AgriShield AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Create Account</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("signup_form"):
            name = st.text_input("Full Name", placeholder="Enter your full name")
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            role = st.selectbox("Role", ["farmer", "buyer", "agronomist"])
            submitted = st.form_submit_button("Sign Up", use_container_width=True)

            if submitted:
                if not name or not email or not password or not confirm_password:
                    st.error("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    existing = fetch_one("SELECT id FROM users WHERE email = %s", (email,))
                    if existing:
                        st.error("An account with this email already exists.")
                    else:
                        try:
                            create_user(name, email, password, role)
                            st.success("Account created successfully! Please log in.")
                            st.session_state["page"] = "Login"
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating account: {e}")

        st.markdown("---")
        st.markdown("Already have an account?")
        if st.button("Back to Login", use_container_width=True):
            st.session_state["page"] = "Login"
            st.rerun()
