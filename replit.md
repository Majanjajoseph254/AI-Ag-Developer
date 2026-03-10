# AgriShield AI

Agricultural application for Kenyan farmers built with Streamlit and PostgreSQL.

## Architecture

- **Frontend**: Streamlit (multi-page via session state routing)
- **Backend**: Python modules in `backend/` (database, auth, ML crop recognition, IoT, weather)
- **ML**: scikit-learn RandomForest classifiers for plant/non-plant and crop type identification
- **Database**: Replit PostgreSQL
- **Entry Point**: `app.py` (run via `streamlit run app.py --server.port 5000`)
- **UI Theme**: Modern design with Google Fonts (Inter + Poppins), green gradient theme, glassmorphism cards

## Folder Structure

```
├── app.py                           # Main Streamlit entry point
├── assets/
│   └── images/                      # AI-generated images for UI
│       ├── hero_banner.png          # Hero banner (Kenyan farm landscape)
│       ├── crop_maize.png           # Maize crop image
│       ├── crop_tomato.png          # Tomato crop image
│       ├── iot_sensor.png           # IoT sensor in field
│       ├── farm_aerial.png          # Aerial farm view
│       ├── farmer_inspecting.png    # Farmer inspecting crops
│       ├── market_produce.png       # Market produce display
│       └── weather_station.png      # Weather station equipment
├── backend/
│   ├── __init__.py
│   ├── db.py                        # PostgreSQL connection helpers
│   ├── auth.py                      # User auth (bcrypt) + profile update + password change
│   ├── ai_disease.py                # Crop disease detection database
│   ├── crop_recognition.py          # ML crop recognition (trained classifiers)
│   ├── iot.py                       # IoT device management & sensor simulation
│   └── weather.py                   # Weather API (OpenWeatherMap or mock)
├── frontend/
│   ├── __init__.py
│   ├── styles.py                    # Modern CSS theme (Google Fonts, cards, animations)
│   ├── components/
│   │   ├── __init__.py
│   │   └── navbar.py                # Sidebar navigation with profile avatar
│   └── pages/
│       ├── __init__.py
│       ├── login.py                 # Login with hero image + social login buttons
│       ├── signup.py                # Registration with hero image + social login
│       ├── profile.py               # Profile editing (name, email, phone, location, bio, password)
│       ├── dashboard.py             # Dashboard with hero banner, stat cards, feature cards
│       ├── crop_diagnosis.py        # ML crop recognition + disease detection
│       ├── crop_monitoring.py       # Crop growth logging
│       ├── market.py                # Market listings (buy/sell)
│       ├── weather.py               # Weather & flood alerts
│       ├── iot_dashboard.py         # IoT sensor monitoring & analytics
│       ├── chatbot.py               # AI farming assistant
│       ├── community.py             # Community forum
│       └── soil_erosion.py          # Soil & erosion assessment
├── ai_models/
│   ├── __init__.py
│   └── preprocessing.py             # Image preprocessing utilities
├── database/
│   ├── init.sql                     # Schema creation SQL
│   └── sample_data.sql              # Sample data SQL
└── .streamlit/
    └── config.toml                  # Streamlit server config
```

## Database Tables

- `users` - User accounts with bcrypt hashed passwords, roles, phone, location, bio, avatar_url
- `crops` - Crop logs with growth stages, disease data, and treatments
- `market` - Market listings with prices and contact info
- `chatbot_history` - Chat messages (role + content format)
- `community_posts` - Forum posts with categories
- `community_replies` - Replies to forum posts
- `badges` - Gamification badges for users
- `iot_devices` - IoT sensor devices with type and location
- `iot_readings` - Sensor readings (soil moisture, temperature, humidity, pH, light, etc.)
- `iot_alerts` - IoT threshold-based alerts
- `crop_recognition_logs` - ML classification results with features

## Features

1. **Authentication** - Sign up / login with bcrypt password hashing, social login buttons (coming soon)
2. **Profile** - Edit name, email, phone, location, bio, role; change password; view activity stats & badges
3. **Dashboard** - Hero banner, stat cards, crop distribution charts, disease trends, feature cards with images
4. **Crop Diagnosis** - ML pipeline: plant/non-plant classification -> crop type identification -> disease detection
5. **Crop Monitoring** - Log planting dates, growth stages, fertilizer/pesticide usage
6. **Market** - Post crop listings, browse/search by crop or location, contact sellers
7. **Weather** - Weather data for Kenyan cities (mock or OpenWeatherMap API)
8. **IoT Dashboard** - Device management, live sensor monitoring, analytics charts, threshold alerts
9. **AI Chatbot** - Rule-based farming assistant (or OpenAI if API key provided)
10. **Community Forum** - Post questions, reply, filter by category
11. **Soil & Erosion** - Risk assessment based on soil type, slope, rainfall, vegetation

## ML Models

- **Plant Classifier**: RandomForestClassifier trained on 1800 synthetic samples. Extracts 16 image features (color, HSV, texture, shape). Distinguishes plants from non-plants (urban, documents, people).
- **Crop Classifier**: RandomForestClassifier trained on 800 synthetic samples. Identifies maize, tomatoes, potatoes, wheat based on color and texture profiles.
- Both models trained at module load time using synthetic feature distributions.

## UI Design

- **Fonts**: Inter (body text) + Poppins (headings) via Google Fonts
- **Colors**: Green gradient theme (#064e3b → #059669), white cards, subtle shadows
- **Components**: Stat cards, feature cards with images, hero sections, profile avatars
- **Security**: All user-derived HTML content escaped via html.escape

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (auto-set by Replit)
- `OPENWEATHER_API_KEY` - (optional) OpenWeatherMap API key for real weather data
- `OPENAI_API_KEY` - (optional) OpenAI API key for AI chatbot responses

## Dependencies

- streamlit, psycopg2-binary, bcrypt, plotly, pillow, requests, pandas, numpy, pyjwt, scikit-learn, scipy

## Demo Accounts

All sample accounts use password: `password123`
- john@example.com (farmer)
- mary@example.com (farmer)
- admin@example.com (admin)
