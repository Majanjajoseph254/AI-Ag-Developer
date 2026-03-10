import streamlit as st

st.set_page_config(
    page_title="AgriShield AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

from frontend.styles import apply_modern_theme
apply_modern_theme()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "Login"

from frontend.pages.login import show_login
from frontend.pages.signup import show_signup
from frontend.pages.dashboard import show_dashboard
from frontend.pages.crop_diagnosis import show_crop_diagnosis
from frontend.pages.crop_monitoring import show_crop_monitoring
from frontend.pages.market import show_market
from frontend.pages.weather import show_weather
from frontend.pages.chatbot import show_chatbot
from frontend.pages.community import show_community
from frontend.pages.soil_erosion import show_soil_erosion
from frontend.pages.iot_dashboard import show_iot_dashboard
from frontend.pages.profile import show_profile
from frontend.components.navbar import show_navbar

if st.session_state["logged_in"] and st.session_state["user"]:
    show_navbar()

    page = st.session_state.get("page", "Dashboard")

    if page == "Dashboard":
        show_dashboard()
    elif page == "Crop Diagnosis":
        show_crop_diagnosis()
    elif page == "Crop Monitoring":
        show_crop_monitoring()
    elif page == "Market":
        show_market()
    elif page == "Weather":
        show_weather()
    elif page == "IoT Dashboard":
        show_iot_dashboard()
    elif page == "Chatbot":
        show_chatbot()
    elif page == "Soil & Erosion":
        show_soil_erosion()
    elif page == "Community":
        show_community()
    elif page == "Profile":
        show_profile()
    else:
        show_dashboard()
else:
    page = st.session_state.get("page", "Login")
    if page == "Signup":
        show_signup()
    else:
        show_login()
