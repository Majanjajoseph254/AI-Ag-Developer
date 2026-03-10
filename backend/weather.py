import os
import random
import requests


KENYAN_CITIES = [
    "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret",
    "Thika", "Malindi", "Kitale", "Garissa", "Nyeri",
    "Machakos", "Meru", "Lamu", "Naivasha", "Nanyuki",
    "Embu", "Kericho", "Bungoma", "Kakamega", "Isiolo"
]

MOCK_CONDITIONS = [
    {"description": "clear sky", "icon": "☀️", "main": "Clear"},
    {"description": "partly cloudy", "icon": "⛅", "main": "Clouds"},
    {"description": "overcast clouds", "icon": "☁️", "main": "Clouds"},
    {"description": "light rain", "icon": "🌦️", "main": "Rain"},
    {"description": "moderate rain", "icon": "🌧️", "main": "Rain"},
    {"description": "heavy rain", "icon": "🌧️", "main": "Rain"},
    {"description": "thunderstorm", "icon": "⛈️", "main": "Thunderstorm"},
    {"description": "scattered clouds", "icon": "🌤️", "main": "Clouds"},
]


def get_kenyan_cities():
    return KENYAN_CITIES


def _get_mock_weather(city):
    condition = random.choice(MOCK_CONDITIONS)
    temp = round(random.uniform(18, 34), 1)
    humidity = random.randint(40, 90)
    wind_speed = round(random.uniform(1, 15), 1)
    pressure = random.randint(1005, 1025)

    forecast = []
    for i in range(1, 6):
        fc = random.choice(MOCK_CONDITIONS)
        forecast.append({
            "day": f"Day {i}",
            "temp_min": round(random.uniform(15, 22), 1),
            "temp_max": round(random.uniform(24, 35), 1),
            "description": fc["description"],
            "icon": fc["icon"],
            "humidity": random.randint(40, 90),
            "wind_speed": round(random.uniform(1, 15), 1)
        })

    return {
        "success": True,
        "city": city,
        "source": "mock",
        "current": {
            "temperature": temp,
            "feels_like": round(temp + random.uniform(-2, 2), 1),
            "humidity": humidity,
            "pressure": pressure,
            "wind_speed": wind_speed,
            "description": condition["description"],
            "icon": condition["icon"],
            "main": condition["main"]
        },
        "forecast": forecast
    }


def get_weather(city):
    api_key = os.environ.get("OPENWEATHER_API_KEY")

    if not api_key:
        return _get_mock_weather(city)

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{city},KE",
            "appid": api_key,
            "units": "metric"
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = {
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
            "icon": _weather_icon(data["weather"][0]["main"]),
            "main": data["weather"][0]["main"]
        }

        forecast = []
        try:
            fc_url = "https://api.openweathermap.org/data/2.5/forecast"
            fc_resp = requests.get(fc_url, params=params, timeout=10)
            fc_resp.raise_for_status()
            fc_data = fc_resp.json()

            daily = {}
            for item in fc_data.get("list", []):
                date = item["dt_txt"].split(" ")[0]
                if date not in daily and len(daily) < 5:
                    daily[date] = {
                        "day": date,
                        "temp_min": item["main"]["temp_min"],
                        "temp_max": item["main"]["temp_max"],
                        "description": item["weather"][0]["description"],
                        "icon": _weather_icon(item["weather"][0]["main"]),
                        "humidity": item["main"]["humidity"],
                        "wind_speed": item["wind"]["speed"]
                    }
            forecast = list(daily.values())
        except Exception:
            pass

        return {
            "success": True,
            "city": city,
            "source": "openweathermap",
            "current": current,
            "forecast": forecast
        }

    except Exception as e:
        return _get_mock_weather(city)


def _weather_icon(main_condition):
    icons = {
        "Clear": "☀️",
        "Clouds": "☁️",
        "Rain": "🌧️",
        "Drizzle": "🌦️",
        "Thunderstorm": "⛈️",
        "Snow": "❄️",
        "Mist": "🌫️",
        "Fog": "🌫️",
        "Haze": "🌫️",
    }
    return icons.get(main_condition, "🌤️")


def get_weather_alerts(city, weather_data=None):
    weather = weather_data if weather_data else get_weather(city)
    alerts = []

    if not weather.get("success"):
        return alerts

    current = weather["current"]

    if current["main"] in ("Rain", "Thunderstorm"):
        if "heavy" in current["description"]:
            alerts.append({
                "type": "Heavy Rain Warning",
                "severity": "high",
                "message": f"Heavy rainfall detected in {city}. Risk of flooding in low-lying areas. Protect crops and avoid working in open fields.",
                "icon": "🚨"
            })
        elif "thunderstorm" in current["description"]:
            alerts.append({
                "type": "Thunderstorm Alert",
                "severity": "high",
                "message": f"Thunderstorm activity in {city}. Seek shelter immediately. Secure livestock and farm equipment.",
                "icon": "⛈️"
            })
        else:
            alerts.append({
                "type": "Rain Advisory",
                "severity": "low",
                "message": f"Rain expected in {city}. Good conditions for planting. Delay pesticide application.",
                "icon": "🌧️"
            })

    if current["humidity"] > 85:
        alerts.append({
            "type": "High Humidity Alert",
            "severity": "medium",
            "message": f"High humidity ({current['humidity']}%) in {city}. Increased risk of fungal diseases. Monitor crops closely.",
            "icon": "💧"
        })

    if current["temperature"] > 35:
        alerts.append({
            "type": "Heat Warning",
            "severity": "medium",
            "message": f"High temperatures ({current['temperature']}°C) in {city}. Increase irrigation. Provide shade for sensitive crops.",
            "icon": "🌡️"
        })

    if current["wind_speed"] > 12:
        alerts.append({
            "type": "Strong Wind Advisory",
            "severity": "medium",
            "message": f"Strong winds ({current['wind_speed']} m/s) in {city}. Stake tall crops. Delay spraying operations.",
            "icon": "💨"
        })

    for day in weather.get("forecast", []):
        if "heavy rain" in day.get("description", "").lower():
            alerts.append({
                "type": "Flood Risk Warning",
                "severity": "high",
                "message": f"Heavy rain forecasted for {city} on {day['day']}. Prepare drainage channels. Move harvested crops to dry storage.",
                "icon": "🌊"
            })
            break

    if not alerts:
        alerts.append({
            "type": "All Clear",
            "severity": "low",
            "message": f"No weather alerts for {city}. Conditions are favorable for farming activities.",
            "icon": "✅"
        })

    return alerts
