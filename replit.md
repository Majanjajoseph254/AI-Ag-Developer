# AgriShield AI

Agricultural application for Kenyan farmers built with Streamlit and PostgreSQL.

## Architecture

- **Frontend**: Streamlit (multi-page via session state routing)
- **Backend**: Python modules in `backend/` (database, auth, ML crop recognition, IoT, weather)
- **ML**: scikit-learn RandomForest classifiers for plant/non-plant and crop type identification
- **Database**: Replit PostgreSQL
- **Entry Point**: `app.py` (run via `streamlit run app.py --server.port 5000`)
- **UI Theme**: Modern design with Google Fonts (Inter + Poppins), green gradient theme, glassmorphism cards
- **Routing**: `app.py` uses a `page_map` dict for session-state routing. Navbar organized into sections (Main, Smart Farming, Operations, Community).

## Folder Structure

```
├── app.py                           # Main Streamlit entry point with page_map routing
├── assets/images/                   # AI-generated images for UI
├── backend/
│   ├── db.py                        # PostgreSQL helpers (execute_query, fetch_one, fetch_all, execute_returning)
│   ├── auth.py                      # User auth (bcrypt) + profile update + password change
│   ├── ai_disease.py                # Crop disease detection database
│   ├── crop_recognition.py          # ML crop recognition (trained classifiers)
│   ├── iot.py                       # IoT device management & sensor simulation
│   └── weather.py                   # Weather API (OpenWeatherMap or mock)
├── frontend/
│   ├── styles.py                    # Modern CSS theme (Google Fonts, cards, animations)
│   ├── components/navbar.py         # Sidebar navigation (sections: Main, Smart Farming, Operations, Community)
│   └── pages/
│       ├── login.py                 # Login with hero image + social login buttons
│       ├── signup.py                # Registration with hero image + social login
│       ├── profile.py               # Profile editing
│       ├── dashboard.py             # Dashboard with hero banner, stat cards, feature cards
│       ├── crop_diagnosis.py        # ML crop recognition + disease detection
│       ├── crop_monitoring.py       # Crop growth logging
│       ├── market.py                # Market listings
│       ├── weather.py               # Weather & flood alerts
│       ├── iot_dashboard.py         # IoT sensor monitoring
│       ├── chatbot.py               # AI farming assistant
│       ├── community.py             # Community forum
│       ├── soil_erosion.py          # Soil & erosion assessment
│       ├── blockchain.py            # Blockchain traceability (batch tracking, transaction ledger)
│       ├── climate_smart.py         # Climate smart practices (carbon calc, seasonal calendar)
│       ├── biotech_ai.py            # Biotechnology & AI (variety DB, recommendations, yield prediction)
│       ├── robotics.py              # Robotics & automation (task manager, drone dashboard)
│       ├── smart_irrigation.py      # Smart irrigation (schedules, water analytics, soil moisture)
│       ├── labour.py                # Labour management (task board, cost calculator, analytics)
│       ├── sustainability.py        # Sustainability (impact score, resource tracking, goals)
│       ├── supply_chain.py          # Supply chain (inventory, stages, cost analytics)
│       └── crop_improvement.py      # Crop improvement (variety trials, yield comparison, seed guide)
├── database/
│   ├── init.sql                     # Schema creation SQL (20 tables)
│   └── sample_data.sql              # Sample data
└── .streamlit/config.toml           # Streamlit server config
```

## Database Tables

### Core
- `users` - User accounts (name, email, password_hash, role, phone, location, bio, avatar_url)
- `crops` - Crop logs with growth stages, disease data, treatments
- `market` - Market listings with prices and contact info
- `chatbot_history` - Chat messages
- `community_posts` / `community_replies` - Forum
- `badges` - Gamification badges

### IoT & Sensors
- `iot_devices` - IoT sensor devices
- `iot_readings` - Sensor readings (soil moisture, temperature, humidity, pH, light, etc.)
- `iot_alerts` - Threshold-based alerts
- `crop_recognition_logs` - ML classification results

### New Feature Tables
- `blockchain_records` - Batch traceability (batch_id, crop_name, stage, location, verified, tx_hash)
- `irrigation_schedules` - Irrigation schedules (crop, area, method, frequency, water_per_session)
- `labour_tasks` - Worker task tracking (task_name, worker_name, priority, status, hours, rate)
- `supply_chain_items` - Inventory tracking (item, category, quantity, stage, origin, destination, cost)
- `crop_improvements` - Variety trials (variety, crop_type, yield, area, soil, fertilizer)
- `sustainability_logs` - Resource usage logs (category, metric, value, unit)
- `automation_tasks` - Automation/drone tasks (task_type, status, area_covered)

## Features (20 pages)

### Main
1. **Dashboard** - Hero banner, stat cards, charts, feature cards with images
2. **Crop Diagnosis** - ML pipeline: plant detection → crop ID → disease analysis
3. **Crop Monitoring** - Log planting dates, growth stages, fertilizer/pesticide
4. **Market** - Post/browse crop listings
5. **Weather** - Weather data for Kenyan cities
6. **IoT Dashboard** - Device management, live monitoring, analytics, alerts

### Smart Farming
7. **Smart Irrigation** - Schedule manager, water analytics, soil moisture, method comparison, water budget
8. **Robotics & Automation** - Task scheduling, drone dashboard, equipment inventory, efficiency analytics
9. **Biotech & AI** - Variety database, AI recommendations, biotech innovations, seed comparison, yield prediction
10. **Climate Smart** - Carbon footprint calculator, regional recommendations, seasonal calendar, agroforestry
11. **Crop Improvement** - Variety trials tracker, yield comparison, seed selection guide, best practices

### Operations
12. **Blockchain Traceability** - Farm-to-market batch tracking, transaction ledger, batch timeline, verification
13. **Supply Chain** - Inventory management, supply chain stages, cost analytics, directory
14. **Labour Management** - Task board (Kanban), cost calculator, workforce analytics
15. **Sustainability** - Impact score (0-100), resource tracking, goals, eco-recommendations, reports

### Community & Tools
16. **Chatbot** - Rule-based farming assistant (OpenAI optional)
17. **Soil & Erosion** - Risk assessment
18. **Community Forum** - Posts, replies, categories
19. **Profile** - Edit profile, change password, activity stats, badges
20. **Auth** - Login/signup with social login buttons (coming soon)

## ML Models

- **Plant Classifier**: RandomForest on 1800 synthetic samples, 16 image features
- **Crop Classifier**: RandomForest on 800 synthetic samples (maize, tomatoes, potatoes, wheat)

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (auto-set by Replit)
- `OPENWEATHER_API_KEY` - (optional) OpenWeatherMap API key
- `OPENAI_API_KEY` - (optional) OpenAI API key for chatbot

## Demo Accounts

All use password: `password123`
- john@example.com (farmer)
- mary@example.com (farmer)
- admin@example.com (admin)
