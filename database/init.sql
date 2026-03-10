CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'farmer',
    phone VARCHAR(50),
    location VARCHAR(255),
    bio TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS crops (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    crop_name VARCHAR(100) NOT NULL,
    growth_stage VARCHAR(100),
    disease_detected VARCHAR(255),
    treatment TEXT,
    photo_url TEXT,
    date_logged TIMESTAMP DEFAULT NOW(),
    planting_date DATE,
    fertilizer_used VARCHAR(255),
    pesticide_used VARCHAR(255),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS market (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    crop_name VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    price_per_kg DECIMAL(10, 2),
    contact_info VARCHAR(255),
    description TEXT,
    posted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chatbot_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS community_posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100) DEFAULT 'general',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS community_replies (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES community_posts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    badge_name VARCHAR(100) NOT NULL,
    description TEXT,
    earned_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS iot_devices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    device_name VARCHAR(255) NOT NULL,
    device_type VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS iot_readings (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES iot_devices(id) ON DELETE CASCADE,
    soil_moisture DECIMAL(5,2),
    soil_temperature DECIMAL(5,2),
    air_temperature DECIMAL(5,2),
    air_humidity DECIMAL(5,2),
    light_intensity DECIMAL(8,2),
    soil_ph DECIMAL(4,2),
    rainfall DECIMAL(6,2),
    wind_speed DECIMAL(5,2),
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS iot_alerts (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES iot_devices(id) ON DELETE CASCADE,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS crop_recognition_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    is_plant BOOLEAN NOT NULL,
    plant_confidence DECIMAL(5,4),
    predicted_crop VARCHAR(100),
    crop_confidence DECIMAL(5,4),
    image_features JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
