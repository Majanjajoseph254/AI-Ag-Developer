import random
import math
from datetime import datetime, timedelta
from backend.db import execute_query, execute_returning, fetch_one, fetch_all


def register_device(user_id, device_name, device_type, location):
    query = """
        INSERT INTO iot_devices (user_id, device_name, device_type, location)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """
    result = execute_returning(query, (user_id, device_name, device_type, location))
    return result["id"]


def get_user_devices(user_id):
    query = """
        SELECT * FROM iot_devices
        WHERE user_id = %s
        ORDER BY created_at DESC
    """
    return fetch_all(query, (user_id,))


def update_device(device_id, user_id, is_active):
    query = """
        UPDATE iot_devices
        SET is_active = %s
        WHERE id = %s AND user_id = %s
    """
    execute_query(query, (is_active, device_id, user_id))


def delete_device(device_id, user_id):
    query = """
        DELETE FROM iot_devices
        WHERE id = %s AND user_id = %s
    """
    execute_query(query, (device_id, user_id))


def _generate_reading(device_type):
    reading = {}

    if device_type in ("Soil Sensor", "Full Station"):
        reading["soil_moisture"] = round(random.uniform(20, 80), 1)
        reading["soil_temperature"] = round(random.uniform(15, 35), 1)
        reading["soil_ph"] = round(random.uniform(4.5, 8.5), 2)

    if device_type in ("Weather Station", "Full Station"):
        reading["air_temperature"] = round(random.uniform(15, 38), 1)
        reading["air_humidity"] = round(random.uniform(30, 90), 1)
        reading["rainfall"] = round(random.uniform(0, 50), 1)
        reading["wind_speed"] = round(random.uniform(0, 20), 1)

    if device_type in ("Light Sensor", "Full Station"):
        reading["light_intensity"] = round(random.uniform(0, 100000), 0)

    return reading


def _insert_reading(device_id, reading, timestamp=None):
    columns = ["device_id"]
    values = [device_id]
    placeholders = ["%s"]

    for col in ["soil_moisture", "soil_temperature", "air_temperature",
                "air_humidity", "light_intensity", "soil_ph", "rainfall", "wind_speed"]:
        if col in reading:
            columns.append(col)
            values.append(reading[col])
            placeholders.append("%s")

    if timestamp:
        columns.append("recorded_at")
        values.append(timestamp)
        placeholders.append("%s")
    else:
        columns.append("recorded_at")
        values.append(datetime.now())
        placeholders.append("%s")

    query = f"""
        INSERT INTO iot_readings ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        RETURNING id
    """
    return execute_returning(query, tuple(values))


def simulate_sensor_reading(device_id):
    device = fetch_one("SELECT * FROM iot_devices WHERE id = %s", (device_id,))
    if not device:
        return None

    reading = _generate_reading(device["device_type"])
    result = _insert_reading(device_id, reading)
    reading_id = result["id"]

    return {"id": reading_id, "device_id": device_id, "data": reading}


def get_readings(device_id, limit=50):
    query = """
        SELECT * FROM iot_readings
        WHERE device_id = %s
        ORDER BY recorded_at DESC
        LIMIT %s
    """
    return fetch_all(query, (device_id, limit))


def get_readings_range(device_id, start_date, end_date):
    query = """
        SELECT * FROM iot_readings
        WHERE device_id = %s AND recorded_at >= %s AND recorded_at <= %s
        ORDER BY recorded_at ASC
    """
    return fetch_all(query, (device_id, start_date, end_date))


def check_alerts(device_id):
    readings = get_readings(device_id, limit=1)
    if not readings:
        return []

    latest = readings[0]

    device = fetch_one("SELECT * FROM iot_devices WHERE id = %s", (device_id,))
    if not device:
        return []

    alerts = []

    soil_moisture = latest.get("soil_moisture")
    if soil_moisture is not None:
        soil_moisture = float(soil_moisture)
        if soil_moisture < 25:
            alerts.append(("Low Soil Moisture", "high",
                           f"Soil moisture at {soil_moisture}% (below 25%)"))
        elif soil_moisture > 75:
            alerts.append(("Waterlogged Soil", "medium",
                           f"Soil moisture at {soil_moisture}% (above 75%)"))

    air_temp = latest.get("air_temperature")
    if air_temp is not None:
        air_temp = float(air_temp)
        if air_temp > 35:
            alerts.append(("High Temperature", "medium",
                           f"Air temperature at {air_temp}°C (above 35°C)"))

    soil_ph = latest.get("soil_ph")
    if soil_ph is not None:
        soil_ph = float(soil_ph)
        if soil_ph < 5.5:
            alerts.append(("Soil pH Out of Range", "medium",
                           f"Soil pH at {soil_ph} (below 5.5)"))
        elif soil_ph > 7.5:
            alerts.append(("Soil pH Out of Range", "medium",
                           f"Soil pH at {soil_ph} (above 7.5)"))

    air_humidity = latest.get("air_humidity")
    if air_humidity is not None:
        air_humidity = float(air_humidity)
        if air_humidity > 85:
            alerts.append(("High Humidity - Disease Risk", "medium",
                           f"Humidity at {air_humidity}% (above 85%)"))

    wind_speed = latest.get("wind_speed")
    if wind_speed is not None:
        wind_speed = float(wind_speed)
        if wind_speed > 15:
            alerts.append(("Strong Wind Alert", "high",
                           f"Wind speed at {wind_speed} m/s (above 15 m/s)"))

    created_alerts = []
    for alert_type, severity, message in alerts:
        query = """
            INSERT INTO iot_alerts (device_id, alert_type, severity, message)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        result = execute_returning(query, (device_id, alert_type, severity, message))
        created_alerts.append({
            "id": result["id"],
            "device_id": device_id,
            "alert_type": alert_type,
            "severity": severity,
            "message": message
        })

    return created_alerts


def get_alerts(user_id, unread_only=False):
    if unread_only:
        query = """
            SELECT a.*, d.device_name, d.device_type
            FROM iot_alerts a
            JOIN iot_devices d ON a.device_id = d.id
            WHERE d.user_id = %s AND a.is_read = FALSE
            ORDER BY a.created_at DESC
        """
    else:
        query = """
            SELECT a.*, d.device_name, d.device_type
            FROM iot_alerts a
            JOIN iot_devices d ON a.device_id = d.id
            WHERE d.user_id = %s
            ORDER BY a.created_at DESC
        """
    return fetch_all(query, (user_id,))


def mark_alert_read(alert_id, user_id):
    query = """
        UPDATE iot_alerts
        SET is_read = TRUE
        WHERE id = %s AND device_id IN (
            SELECT id FROM iot_devices WHERE user_id = %s
        )
    """
    execute_query(query, (alert_id, user_id))


def generate_historical_data(device_id, days=30):
    device = fetch_one("SELECT * FROM iot_devices WHERE id = %s", (device_id,))
    if not device:
        return 0

    device_type = device["device_type"]
    now = datetime.now()
    count = 0

    for day in range(days, 0, -1):
        for hour_offset in [6, 10, 14, 18]:
            timestamp = now - timedelta(days=day) + timedelta(hours=hour_offset - now.hour)
            reading = {}

            hour_factor = math.sin((hour_offset - 6) * math.pi / 12)

            if device_type in ("Soil Sensor", "Full Station"):
                base_moisture = 50 + random.gauss(0, 10)
                reading["soil_moisture"] = round(max(20, min(80, base_moisture + random.gauss(0, 3))), 1)
                reading["soil_temperature"] = round(20 + 8 * hour_factor + random.gauss(0, 2), 1)
                reading["soil_ph"] = round(6.5 + random.gauss(0, 0.5), 2)

            if device_type in ("Weather Station", "Full Station"):
                reading["air_temperature"] = round(22 + 10 * hour_factor + random.gauss(0, 3), 1)
                reading["air_humidity"] = round(60 - 15 * hour_factor + random.gauss(0, 5), 1)
                reading["rainfall"] = round(max(0, random.gauss(0, 5) if random.random() < 0.2 else 0), 1)
                reading["wind_speed"] = round(max(0, 5 + random.gauss(0, 3)), 1)

            if device_type in ("Light Sensor", "Full Station"):
                reading["light_intensity"] = round(max(0, 50000 * hour_factor + random.gauss(0, 5000)), 0)

            _insert_reading(device_id, reading, timestamp)
            count += 1

    return count
