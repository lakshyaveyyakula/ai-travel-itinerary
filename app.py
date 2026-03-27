import streamlit as st
from google import genai
import requests 
from datetime import date, timedelta
st.sidebar.header("Travel Dates")
check_in = st.sidebar.date_input("Check-in Date", date.today())
check_out = st.sidebar.date_input("Check-out Date", date.today() + timedelta(days=3))
st.set_page_config(page_title="AI Travel Planner", layout="centered")
st.title("AI Travel Itinerary Generator")
st.caption("Powered by AI")

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

def get_hotels(city, d1, d2):
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_hotels",
        "q": f"Hotels in {city}",
        "check_in_date": str(d1),  
        "check_out_date": str(d2),
        "api_key": st.secrets["SERP_API_KEY"]
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        hotels = data.get("properties", [])
        # Just get the names of the first 3 hotels
        names = [h['name'] for h in hotels[:3]]
        return ", ".join(names) if names else "No hotels found for these dates."
    return "Hotel data unavailable"
    

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
    hotel_info = get_hotels(user_input, check_in, check_out)

    SYSTEM_PROMPT = f"""
    You are a travel assitant chatbot for suggesting places.
    Current context for {user_input}:
    - Weather: {weather_info}
    - Hotels: ({check_in} to {check_out}: {hotel_info}
    You have to access to previous messages in the chat session.
    Use this memory to provide consistent and helpful responses.
    Do not claim that you have no memory of the conversation.

    Guidelines:
    - Provide general travel advice based on the destination entered.
    - Do not claim any information as 100 percent accurate like time.
    - Give general suggestions about places that are close to the mentioned destination.
    - Be calm, energized, professional.
    """

    conversation = SYSTEM_PROMPT + f"\n[REAL-TIME WEATHER]: {weather_info}\n[TOP HOTELS]: {hotel_info}\n"
    #conversation += f"[TOP HOTELS]: {hotel_info}\n"
    #conversation = SYSTEM_PROMPT + f"\n[CONTEXT] Weather: {weather_info} | Hotels: {hotel_info}\n"
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        conversation +=f"{role.capitalize()}: {content}\n"

    response = client.models.generate_content(
        model = "gemini-2.0-flash",
        contents=conversation
        )
    reply = response.text
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").markdown(reply)
    MAX_MESSAGES = 50
    st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]
    st.warning("It is not a professional chatbot, just for general information.")

