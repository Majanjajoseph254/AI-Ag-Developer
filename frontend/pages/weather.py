import streamlit as st
from backend.weather import get_weather, get_weather_alerts, get_kenyan_cities


def show_weather():
    st.title("🌦️ Weather Dashboard")
    st.markdown("Monitor weather conditions across Kenya to plan your farming activities.")

    cities = get_kenyan_cities()
    selected_city = st.selectbox("Select a City", cities, index=0)

    if st.button("Get Weather", type="primary"):
        st.session_state["weather_city"] = selected_city

    city = st.session_state.get("weather_city", selected_city)

    with st.spinner("Fetching weather data..."):
        weather_data = get_weather(city)
        alerts = get_weather_alerts(city, weather_data=weather_data)

    if not weather_data.get("success"):
        st.error("Failed to fetch weather data. Please try again.")
        return

    current = weather_data["current"]

    st.subheader(f"Current Weather in {city}")
    if weather_data.get("source") == "mock":
        st.caption("📡 Using simulated weather data (no API key configured)")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌡️ Temperature", f"{current['temperature']}°C", f"Feels like {current['feels_like']}°C")
    with col2:
        st.metric("💧 Humidity", f"{current['humidity']}%")
    with col3:
        st.metric("💨 Wind Speed", f"{current['wind_speed']} m/s")
    with col4:
        st.metric("📊 Pressure", f"{current['pressure']} hPa")

    st.markdown(f"**Condition:** {current['icon']} {current['description'].title()}")

    st.divider()

    st.subheader("⚠️ Weather Alerts")
    for alert in alerts:
        severity_colors = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        severity_icon = severity_colors.get(alert["severity"], "🟢")
        with st.container():
            st.markdown(f"### {alert['icon']} {alert['type']} {severity_icon}")
            st.markdown(alert["message"])
            st.divider()

    forecast = weather_data.get("forecast", [])
    if forecast:
        st.subheader("📅 5-Day Forecast")
        cols = st.columns(len(forecast))
        for i, day in enumerate(forecast):
            with cols[i]:
                st.markdown(f"**{day['day']}**")
                st.markdown(f"{day['icon']}")
                st.markdown(f"🔺 {day['temp_max']}°C")
                st.markdown(f"🔻 {day['temp_min']}°C")
                st.markdown(f"💧 {day['humidity']}%")
                st.markdown(f"💨 {day['wind_speed']} m/s")
                st.caption(day["description"].title())
