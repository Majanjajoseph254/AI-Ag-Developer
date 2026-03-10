import streamlit as st
import base64
import os
from backend.auth import create_user
from backend.db import fetch_one


def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def show_signup():
    farm_b64 = get_image_base64("assets/images/farm_aerial.png")

    col_form, col_hero = st.columns([1, 1.2], gap="large")

    with col_form:
        st.markdown("""
        <div class="brand-header">
            <h1>Join AgriShield AI</h1>
            <p>Create your free account today</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="social-btn" style="opacity: 0.6; cursor: default;">
            <svg viewBox="0 0 24 24" width="20" height="20"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            Google &mdash; Coming Soon
        </div>
        <div class="social-btn" style="opacity: 0.6; cursor: default;">
            <svg viewBox="0 0 24 24" width="20" height="20"><path fill="#333" d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
            GitHub &mdash; Coming Soon
        </div>

        <div class="divider-text">or sign up with email</div>
        """, unsafe_allow_html=True)

        with st.form("signup_form"):
            name = st.text_input("Full Name", placeholder="Enter your full name")
            email = st.text_input("Email", placeholder="Enter your email")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                password = st.text_input("Password", type="password", placeholder="Create password")
            with col_p2:
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
            role = st.selectbox("I am a...", ["farmer", "buyer", "agronomist"], format_func=lambda x: x.capitalize())
            submitted = st.form_submit_button("Create Account", use_container_width=True)

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
                            st.success("Account created! Please sign in.")
                            st.session_state["page"] = "Login"
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating account: {e}")

        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("<p style='color: var(--text-secondary); font-size: 0.9rem;'>Already have an account?</p>", unsafe_allow_html=True)
        with col_b:
            if st.button("Sign In", use_container_width=True):
                st.session_state["page"] = "Login"
                st.rerun()

    with col_hero:
        if farm_b64:
            st.markdown(f"""
            <div style="position: relative; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.15);">
                <img src="data:image/png;base64,{farm_b64}" style="width: 100%; height: 580px; object-fit: cover; display: block;">
                <div style="position: absolute; bottom: 0; left: 0; right: 0; padding: 2.5rem; background: linear-gradient(transparent, rgba(0,0,0,0.7));">
                    <h2 style="color: white; font-family: 'Poppins', sans-serif; font-size: 1.5rem; margin-bottom: 0.5rem;">Join 10,000+ Farmers</h2>
                    <p style="color: rgba(255,255,255,0.9); font-size: 0.95rem; margin: 0;">Access AI tools, market prices, and community support</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
