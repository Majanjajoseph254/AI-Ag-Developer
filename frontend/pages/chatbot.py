import os
import streamlit as st
from datetime import datetime
from backend.db import execute_query, fetch_all

AGRONOMY_RESPONSES = {
    "maize": "🌽 **Maize Growing Tips:**\n- Plant at the onset of rains (March-April or October-November in Kenya)\n- Space seeds 75cm between rows, 25cm within rows\n- Apply DAP fertilizer at planting (50kg/acre)\n- Top dress with CAN at knee height\n- Common diseases: Maize Streak Virus, Grey Leaf Spot, Stalk Borer",
    "tomato": "🍅 **Tomato Growing Tips:**\n- Transplant seedlings at 4-6 weeks old\n- Space 60cm x 45cm\n- Stake plants for support\n- Water consistently but avoid waterlogging\n- Watch for blight, bacterial wilt, and whiteflies",
    "potato": "🥔 **Potato Growing Tips:**\n- Plant certified seed potatoes\n- Plant in well-drained, fertile soil\n- Hill up soil around stems as they grow\n- Harvest 3-4 months after planting\n- Watch for late blight and bacterial wilt",
    "wheat": "🌾 **Wheat Growing Tips:**\n- Best grown in highland areas (1500-3000m)\n- Plant in June-July for October harvest\n- Use 50kg seed per acre\n- Apply fertilizer at planting\n- Watch for rust diseases and aphids",
    "irrigation": "💧 **Irrigation Tips:**\n- Drip irrigation is most water-efficient\n- Water early morning or late evening\n- Mulch around plants to retain moisture\n- Check soil moisture before watering\n- Avoid overhead irrigation for disease-prone crops",
    "fertilizer": "🧪 **Fertilizer Guide:**\n- DAP (18-46-0): Use at planting for phosphorus\n- CAN (26-0-0): Top dressing for nitrogen\n- NPK (17-17-17): Balanced nutrition\n- Always do a soil test first\n- Apply organic manure for long-term soil health",
    "pest": "🐛 **Pest Management:**\n- Practice crop rotation to break pest cycles\n- Use certified seeds resistant to common pests\n- Scout fields regularly for early detection\n- Try integrated pest management (IPM)\n- Use pesticides as a last resort, follow label instructions",
    "soil": "🌍 **Soil Health Tips:**\n- Test soil pH (ideal: 6.0-7.0 for most crops)\n- Add organic matter (compost, manure)\n- Practice minimum tillage\n- Use cover crops to prevent erosion\n- Rotate crops to maintain soil nutrients",
    "weather": "🌦️ **Weather & Farming:**\n- Monitor weather forecasts before planting\n- Plant drought-resistant varieties in dry areas\n- Prepare drainage channels before heavy rains\n- Use mulching to protect soil from heavy rain\n- Consider greenhouse farming for weather protection",
    "market": "📊 **Market Tips for Farmers:**\n- Join farmer cooperatives for better prices\n- Store produce properly to reduce post-harvest losses\n- Use mobile platforms to check market prices\n- Consider value addition (drying, milling)\n- Build relationships with reliable buyers",
}

DEFAULT_RESPONSE = "🌱 I'm AgriShield's farming assistant! I can help with questions about:\n- **Crops**: maize, tomato, potato, wheat\n- **Farming**: irrigation, fertilizer, pest control\n- **Soil** health and management\n- **Weather** and farming\n- **Market** tips\n\nTry asking about any of these topics!"


def _get_rule_based_response(message):
    message_lower = message.lower()
    for keyword, response in AGRONOMY_RESPONSES.items():
        if keyword in message_lower:
            return response

    greetings = ["hello", "hi", "hey", "jambo", "habari"]
    if any(g in message_lower for g in greetings):
        return "👋 Habari! Welcome to AgriShield AI Assistant. How can I help you with your farming today?"

    thanks = ["thank", "asante", "thanks"]
    if any(t in message_lower for t in thanks):
        return "🙏 You're welcome! Feel free to ask anything about farming. Tutaendelea kusaidiana!"

    return DEFAULT_RESPONSE


def _get_ai_response(message, history):
    try:
        import openai
        client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        messages = [
            {"role": "system", "content": "You are AgriShield AI, an expert agricultural assistant for Kenyan farmers. Provide practical, actionable farming advice. Focus on crops common in Kenya (maize, tomatoes, potatoes, wheat, tea, coffee). Use simple language. Include local context when possible."}
        ]
        for h in history[-10:]:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception:
        return _get_rule_based_response(message)


def _save_message(user_id, role, content):
    execute_query(
        "INSERT INTO chatbot_history (user_id, role, content, created_at) VALUES (%s, %s, %s, %s)",
        (user_id, role, content, datetime.now())
    )


def _load_history(user_id):
    rows = fetch_all(
        "SELECT role, content, created_at FROM chatbot_history WHERE user_id = %s ORDER BY created_at ASC",
        (user_id,)
    )
    return [{"role": r["role"], "content": r["content"]} for r in rows]


def show_chatbot():
    st.title("🤖 AgriShield AI Assistant")
    st.markdown("Ask me anything about farming, crops, soil, weather, or markets!")

    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in to use the chatbot.")
        return

    user_id = user["id"]
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))

    if has_openai:
        st.caption("🧠 Powered by OpenAI")
    else:
        st.caption("📚 Using rule-based responses (no OpenAI API key configured)")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ Clear Chat"):
            execute_query("DELETE FROM chatbot_history WHERE user_id = %s", (user_id,))
            st.session_state.pop("chat_messages", None)
            st.rerun()

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = _load_history(user_id)

    if not st.session_state["chat_messages"]:
        st.session_state["chat_messages"].append({
            "role": "assistant",
            "content": "👋 Habari! I'm your AgriShield AI farming assistant. How can I help you today?\n\nYou can ask me about:\n- 🌽 Crop growing tips\n- 💧 Irrigation\n- 🧪 Fertilizers\n- 🐛 Pest management\n- 🌍 Soil health\n- 📊 Market tips"
        })

    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about farming, crops, soil..."):
        st.session_state["chat_messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        _save_message(user_id, "user", prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if has_openai:
                    response = _get_ai_response(prompt, st.session_state["chat_messages"])
                else:
                    response = _get_rule_based_response(prompt)
                st.markdown(response)

        st.session_state["chat_messages"].append({"role": "assistant", "content": response})
        _save_message(user_id, "assistant", response)
