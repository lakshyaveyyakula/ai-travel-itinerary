import streamlit as st
import requests
import os
from openai import OpenAI

# -------------------- API KEYS --------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------- GOOGLE PLACES --------------------
def get_places(city):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"tourist attractions in {city}",
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params).json()
    results = response.get("results", [])

    places = []
    for place in results[:5]:
        name = place.get("name")
        rating = place.get("rating", "N/A")
        places.append(f"{name} (Rating: {rating})")

    return places

# -------------------- WEATHER --------------------
def get_weather(city):
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params).json()

    if "weather" in response:
        return response["weather"][0]["description"]
    return "No weather data"

# -------------------- AI ITINERARY --------------------
def generate_itinerary(city, interests, days):
    places = get_places(city)
    weather = get_weather(city)

    prompt = f"""
    Create a detailed {days}-day travel itinerary for {city}.

    Interests: {interests}
    Weather: {weather}
    Top attractions: {places}

    Give a day-by-day plan with activities, food suggestions, and timing.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# -------------------- STREAMLIT UI --------------------
st.set_page_config(page_title="AI Travel Planner")

st.title("AI Travel Itinerary Generator")

city = st.text_input("Enter destination (e.g., Paris)")
interests = st.text_input("Your interests (food, adventure, museums)")
days = st.slider("Number of days", 1, 5, 2)

if st.button("Generate Itinerary"):
    if not city:
        st.warning("Please enter a destination")
    else:
        with st.spinner("Planning your trip..."):
            itinerary = generate_itinerary(city, interests, days)

        st.subheader("🧳 Your Travel Plan")
        st.write(itinerary)
