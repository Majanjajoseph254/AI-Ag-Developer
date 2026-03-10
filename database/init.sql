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

CREATE TABLE IF NOT EXISTS blockchain_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    batch_id VARCHAR(50) NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    stage VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    verified BOOLEAN DEFAULT FALSE,
    tx_hash VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS irrigation_schedules (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    crop_name VARCHAR(100) NOT NULL,
    area_hectares DECIMAL(8,2),
    method VARCHAR(50) NOT NULL,
    frequency VARCHAR(50),
    water_per_session DECIMAL(8,2),
    next_scheduled DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS labour_tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    task_name VARCHAR(255) NOT NULL,
    worker_name VARCHAR(255),
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    due_date DATE,
    completed_at TIMESTAMP,
    hours_worked DECIMAL(6,2),
    hourly_rate DECIMAL(8,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS supply_chain_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    item_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    quantity DECIMAL(10,2),
    unit VARCHAR(50),
    stage VARCHAR(50) DEFAULT 'farm',
    origin VARCHAR(255),
    destination VARCHAR(255),
    cost DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'in_stock',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS crop_improvements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    variety_name VARCHAR(255) NOT NULL,
    crop_type VARCHAR(100) NOT NULL,
    planting_date DATE,
    harvest_date DATE,
    yield_kg DECIMAL(10,2),
    area_hectares DECIMAL(8,2),
    soil_type VARCHAR(100),
    fertilizer VARCHAR(255),
    irrigation_method VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sustainability_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    value DECIMAL(12,2),
    unit VARCHAR(50),
    notes TEXT,
    logged_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS automation_tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    task_name VARCHAR(255) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    scheduled_at TIMESTAMP,
    completed_at TIMESTAMP,
    area_covered DECIMAL(8,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
