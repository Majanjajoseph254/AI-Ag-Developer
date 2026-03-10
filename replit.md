# AgriShield AI

Agricultural application for Kenyan farmers built with Streamlit and PostgreSQL.

## Architecture

- **Frontend**: Streamlit (multi-page via session state routing)
- **Backend**: Python modules in `backend/` (database, auth, AI disease detection, weather)
- **Database**: Replit PostgreSQL
- **Entry Point**: `app.py` (run via `streamlit run app.py --server.port 5000`)

## Folder Structure

```
├── app.py                           # Main Streamlit entry point
├── backend/
│   ├── __init__.py
│   ├── db.py                        # PostgreSQL connection helpers
│   ├── auth.py                      # User authentication (bcrypt)
│   ├── ai_disease.py                # Crop disease detection (simulated AI)
│   └── weather.py                   # Weather API (OpenWeatherMap or mock)
├── frontend/
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   └── navbar.py                # Sidebar navigation
│   └── pages/
│       ├── __init__.py
│       ├── login.py                 # Login page
│       ├── signup.py                # Registration page
│       ├── dashboard.py             # User dashboard with charts
│       ├── crop_diagnosis.py        # AI crop disease detection
│       ├── crop_monitoring.py       # Crop growth logging
│       ├── market.py                # Market listings (buy/sell)
│       ├── weather.py               # Weather & flood alerts
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

- `users` - User accounts with bcrypt hashed passwords and roles
- `crops` - Crop logs with growth stages, disease data, and treatments
- `market` - Market listings with prices and contact info
- `chatbot_history` - Chat messages (role + content format)
- `community_posts` - Forum posts with categories
- `community_replies` - Replies to forum posts
- `badges` - Gamification badges for users

## Features

1. **Authentication** - Sign up / login with bcrypt password hashing
2. **Dashboard** - Overview metrics, crop distribution charts, disease trends
3. **Crop Diagnosis** - Upload/camera image, simulated AI disease detection (top 3 predictions)
4. **Crop Monitoring** - Log planting dates, growth stages, fertilizer/pesticide usage
5. **Market** - Post crop listings, browse/search by crop or location, contact sellers
6. **Weather** - Weather data for Kenyan cities (mock or OpenWeatherMap API)
7. **AI Chatbot** - Rule-based farming assistant (or OpenAI if API key provided)
8. **Community Forum** - Post questions, reply, filter by category
9. **Soil & Erosion** - Risk assessment based on soil type, slope, rainfall, vegetation

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (auto-set by Replit)
- `OPENWEATHER_API_KEY` - (optional) OpenWeatherMap API key for real weather data
- `OPENAI_API_KEY` - (optional) OpenAI API key for AI chatbot responses

## Dependencies

- streamlit, psycopg2-binary, bcrypt, plotly, pillow, requests, pandas, numpy, pyjwt

## Demo Accounts

All sample accounts use password: `password123` (but the bcrypt hash in sample_data is a placeholder)
- john@example.com (farmer)
- mary@example.com (farmer)
- admin@example.com (admin)
