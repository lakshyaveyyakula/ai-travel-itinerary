import streamlit as st
from google import genai
import requests 

st.set_page_config(page_title="AI Travel Planner", layout="centered")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather?"
    params = {
        "q": city, 
        "appid": st.secrets["OPENWEATHER_API_KEY"], 
        "units": "metric"
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        return f"{data['main']['temp']}°C and {data['weather'][0]['description']}"
    return "Weather data unavailable"


def get_events(city):
    url = "https://www.eventbriteapi.com/v3/events/search/"
    headers = {
        "Authorization": f"Bearer {st.secrets['EVENTBRITE_API_KEY']}"
    }
    params = {
        "location.address": city,
        "page_size": 3
    }
    r = requests.get(url, headers=headers, params=params)
    
    if r.status_code == 200:
        data = r.json()
        events = data.get("events", [])
        # Extract names into a list
        names = [e.get("name", {}).get("text", "Event") for e in events]
        return ", ".join(names) if names else "No events found"
    return "Event data unavailable"
    
SYSTEM_PROMPT = """
You are a travel assitant chatbot for suggesting places.

You have to access to previous messages in the chat session.
Use this memory to provide consistent and helpful responses.
Do not claim that you have no memory of the conversation.

Guidelines:
- Provide general travel advice based on the destination entered.
- Do not claim any information as 100 percent accurate like time.
- Give general suggestions about places that are close to the mentioned destination.
- Be sad, sassy, rude, swear and snappy.
"""
st.title("AI Travel Itinerary Generator")
st.caption("Powered by AI")

#Messages 
if "messages" not in st.session_state:
    st.session_state.messages = []

#previous messages 
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

#inputs
user_input = st.chat_input("Enter your destination")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    weather_info = get_weather(user_input)
    event_info = get_events(user_input)
# Now Gemini knows if it's muggy, cold, or perfect for a hike!
    conversation = SYSTEM_PROMPT + f"\n[REAL-TIME WEATHER]: {weather_info}\n"
    conversation += f"[REAL-TIME EVENTS]: {event_info}\n"
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        conversation +=f"{role.capitalize()}: {content}\n"

    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        contents=conversation
    )
    reply = response.text
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").markdown(reply)
    MAX_MESSAGES = 50
    st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]
    st.warning("It is not a professional chatbot, just for general information.")

