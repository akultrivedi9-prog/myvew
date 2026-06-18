import streamlit as st
from google import genai

# Set up the webpage layout and title
st.set_page_config(page_title="My AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 My Custom AI Chatbot")
st.caption("A clean web interface with full markdown and bold text support.")

# 🟢 SECURE CONFIGURATION: Pull the API key safely from hidden environment settings
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("Missing Gemini API Key configuration. Please check your Secrets setup.")
    st.stop()

# Initialize chat history inside the website's memory session if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🧼 ADDED FEATURE: Add a reset button to the sidebar to clear conversation history
with st.sidebar:
    st.title("Settings")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

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

    # 🛠️ UPGRADED ERROR HANDLER: Catch 503 high demand traffic spikes cleanly
    except Exception as e:
        if "503" in str(e) or "UNAVAILABLE" in str(e).upper():
            st.warning(
                "⚠️ Google's AI servers are experiencing temporary high traffic. Please wait 10 seconds and try resubmitting your message!")
        else:
            st.error(f"An error occurred: {e}")
