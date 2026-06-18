import streamlit as st
from google import genai

# Set up the webpage layout and title
st.set_page_config(page_title="My AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 My Custom AI Chatbot")
st.caption("A clean web interface with full markdown and bold text support.")

# 🟢 SECURE UPDATE: Pull the API key safely from hidden environment settings
# Do NOT paste your raw key text here anymore.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("Missing Gemini API Key configuration. Please check your Secrets setup.")
    st.stop()

# Initialize chat history inside the website's memory session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous conversation messages cleanly on the web page
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept chat input from the user via the web interface
if user_query := st.chat_input("Ask your AI anything..."):

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_query)

    # Add user message to chat history memory
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Generate response from the AI model
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_query,
        )

        # Display assistant response in chat message container with correct markdown rendering
        with st.chat_message("assistant"):
            st.markdown(response.text)

        # Add assistant response to chat history memory
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"An error occurred: {e}")
