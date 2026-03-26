import streamlit as st
from rag.realtime import fetch_google_places, fetch_eventbrite_events, fetch_weather
from rag.embed import build_index
from agent.agent import agent

st.set_page_config(page_title="AI Travel Itinerary Generator", layout="wide")
st.title("AI Travel Itinerary Generator")

# --- Load API keys from Streamlit secrets ---
GOOGLE_PLACES_KEY = st.secrets["GOOGLE_PLACES_KEY"]
EVENTBRITE_KEY = st.secrets.get("EVENTBRITE_KEY", "")
WEATHER_KEY = st.secrets.get("WEATHER_KEY", "")

# --- User Inputs ---
destination = st.text_input("Enter your destination", "")
budget = st.number_input("Enter your budget ($)", min_value=0, value=1000, step=50)
days = st.number_input("Number of days", min_value=1, max_value=14, value=3)

# Default interests
default_interests = ["food", "nature", "sightseeing"]

if st.button("Generate Itinerary"):

    if not destination:
        st.warning("Please enter a destination!")
    else:
        with st.spinner("Fetching real-time data..."):

            documents = []

            # --- Fetch attractions / hotels ---
            for interest in default_interests:
                documents += fetch_google_places(destination, interest, GOOGLE_PLACES_KEY)

            # --- Fetch events ---
            documents += fetch_eventbrite_events(destination, EVENTBRITE_KEY)

            # --- Fetch weather ---
            weather_info = fetch_weather(destination, WEATHER_KEY)
            if weather_info:
                documents.append(weather_info)

            # --- Check if data fetched ---
            if not documents:
                st.error("No data fetched. Check your API keys or destination.")
            else:
                # --- Build embeddings & generate itinerary ---
                index = build_index(documents)
                user_input = f"{days}-day trip to {destination} focusing on food, nature, sightseeing"

                itinerary = agent(
                    user_input=user_input,
                    index=index,
                    documents=documents,
                    budget=budget,
                    days=days,
                    interests=", ".join(default_interests)
                )

                # --- Display nicely with expandable day sections ---
                st.subheader("📝 Your Personalized Itinerary")
                days_sections = itinerary.split("Day")
                for d in days_sections:
                    if d.strip():
                        day_title = "Day " + d.strip().split(":", 1)[0]
                        day_content = d.strip().split(":", 1)[1] if ":" in d else d.strip()
                        st.expander(day_title).text(day_content)
