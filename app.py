import streamlit as st

st.set_page_config(
    page_title="AgriShield AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1b5e20 0%, #2e7d32 50%, #388e3c 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background-color: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white !important;
        border-radius: 8px;
        transition: background-color 0.3s;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    .stMetric {
        background-color: #f0f7f0;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #2e7d32;
    }
    h1, h2, h3 {
        color: #1b5e20;
    }
    .stForm {
        background-color: #fafafa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    @media (max-width: 768px) {
        .stColumns > div {
            min-width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

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
    elif page == "Chatbot":
        show_chatbot()
    elif page == "Soil & Erosion":
        show_soil_erosion()
    elif page == "Community":
        show_community()
    else:
        show_dashboard()
else:
    page = st.session_state.get("page", "Login")
    if page == "Signup":
        show_signup()
    else:
        show_login()
