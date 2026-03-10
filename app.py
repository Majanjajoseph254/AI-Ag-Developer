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
from frontend.pages.blockchain import show_blockchain
from frontend.pages.climate_smart import show_climate_smart
from frontend.pages.biotech_ai import show_biotech_ai
from frontend.pages.robotics import show_robotics
from frontend.pages.smart_irrigation import show_smart_irrigation
from frontend.pages.labour import show_labour
from frontend.pages.sustainability import show_sustainability
from frontend.pages.supply_chain import show_supply_chain
from frontend.pages.crop_improvement import show_crop_improvement
from frontend.components.navbar import show_navbar

if st.session_state["logged_in"] and st.session_state["user"]:
    show_navbar()

    page = st.session_state.get("page", "Dashboard")

    page_map = {
        "Dashboard": show_dashboard,
        "Crop Diagnosis": show_crop_diagnosis,
        "Crop Monitoring": show_crop_monitoring,
        "Market": show_market,
        "Weather": show_weather,
        "IoT Dashboard": show_iot_dashboard,
        "Chatbot": show_chatbot,
        "Soil & Erosion": show_soil_erosion,
        "Community": show_community,
        "Profile": show_profile,
        "Blockchain": show_blockchain,
        "Climate Smart": show_climate_smart,
        "Biotech & AI": show_biotech_ai,
        "Robotics": show_robotics,
        "Smart Irrigation": show_smart_irrigation,
        "Labour": show_labour,
        "Sustainability": show_sustainability,
        "Supply Chain": show_supply_chain,
        "Crop Improvement": show_crop_improvement,
    }

    handler = page_map.get(page, show_dashboard)
    handler()
else:
    page = st.session_state.get("page", "Login")
    if page == "Signup":
        show_signup()
    else:
        show_login()
