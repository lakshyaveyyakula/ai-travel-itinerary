import streamlit as st
from google import genai

st.set_page_config(page_title="AI Travel Itinerary Generator", layout="centered")

client = genai.Client(api_key=st.secrest["GEMINI_API_KEY"])

SYSTEM_PROMPT = """
You are a travel assitant chatbot for suggesting places.

You have to access to previous messages in the chat session.
Use this memory to provide consistent and helpful responses.
Do not claim that you have no memory of the conversation.

Guidelines:
- Provide general travel advice based on the destination entered.
- Do not claim any information as 100 percent accurate like time.
- Give general suggestions about places that are close to the mentioned destination.
- Be calm, energized and professional.
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
user_input = st.chat_input("Enter your destination", "")
#budget = st.number_input("Enter your budget ($)", min_value=0, value=1000, step=50)
#days = st.number_input("Number of days", min_value=1, max_value=14, value=3)

if destination:
    st.session_state.messages.append({"role": "user", "content": destination})
    st.chat_message("user").markdown(user_input)
    conversation = SYSTEM_PROMPT + "\n"    
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
    st.warning("not a professional chatbot")


