import streamlit as st
import base64
import os
from backend.auth import authenticate_user


def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def show_login():
    hero_b64 = get_image_base64("assets/images/hero_banner.png")

    col_hero, col_form = st.columns([1.2, 1], gap="large")

    with col_hero:
        if hero_b64:
            st.markdown(f"""
            <div style="position: relative; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.15);">
                <img src="data:image/png;base64,{hero_b64}" style="width: 100%; height: 520px; object-fit: cover; display: block;">
                <div style="position: absolute; bottom: 0; left: 0; right: 0; padding: 2.5rem; background: linear-gradient(transparent, rgba(0,0,0,0.7));">
                    <h2 style="color: white; font-family: 'Poppins', sans-serif; font-size: 1.8rem; margin-bottom: 0.5rem;">Empowering Kenyan Farmers</h2>
                    <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin: 0;">AI-powered crop disease detection, market insights, and smart farming tools</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="hero-section" style="min-height: 400px; display: flex; flex-direction: column; justify-content: center;">
                <h1 style="color: white; font-size: 2.5rem;">Empowering Kenyan Farmers</h1>
                <p style="color: rgba(255,255,255,0.9);">AI-powered crop disease detection, market insights, and smart farming tools</p>
            </div>
            """, unsafe_allow_html=True)

    with col_form:
        st.markdown("""
        <div class="brand-header">
            <h1>AgriShield AI</h1>
            <p>Smart farming starts here</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="social-btn" style="opacity: 0.6; cursor: default;">
            <svg viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            Google &mdash; Coming Soon
        </div>
        <div class="social-btn" style="opacity: 0.6; cursor: default;">
            <svg viewBox="0 0 24 24"><path fill="#333" d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
            GitHub &mdash; Coming Soon
        </div>
        <div class="social-btn" style="opacity: 0.6; cursor: default;">
            <svg viewBox="0 0 24 24"><path fill="#000" d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
            Apple &mdash; Coming Soon
        </div>

        <div class="divider-text">or sign in with email</div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

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

        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("<p style='color: var(--text-secondary); font-size: 0.9rem;'>Don't have an account?</p>", unsafe_allow_html=True)
        with col_b:
            if st.button("Create Account", use_container_width=True):
                st.session_state["page"] = "Signup"
                st.rerun()
