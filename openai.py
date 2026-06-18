import streamlit as st
from google import genai
from google.genai import types

# Set up the webpage layout and title
st.set_page_config(page_title="My AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 My Advanced AI Assistant")
st.caption("Now with persistent memory, real-time web search, and image parsing capabilities.")

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

# 🧼 Sidebar Settings to clear chat memory
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

    # Convert our stored chat history into the structure the Gemini API expects
    api_history = []
    for msg in st.session_state.messages[:-1]:  # Exclude the very last message we just added
        api_history.append(
            types.Content(
                role="user" if msg["role"] == "user" else "model",
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    # Generate response from the AI model
    try:
        # Start a chat session using the conversation history, adding tools and instructions
        chat = client.chats.create(
            model='gemini-2.5-flash',
            history=api_history,
            config=types.GenerateContentConfig(
                # 🧠 Give the AI its identity
                system_instruction="You are a highly capable AI assistant. Balance empathy with absolute objective candor. Provide comprehensive, direct answers first, using short sentences and punchy lists. You have full access to Google Search to look up live facts and images.",
                # 🌐 Enable real-time Google Search grounding
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )

        # Send the latest message inside the active session
        response = chat.send_message(user_query)

        # Display assistant response in chat message container with correct markdown rendering
        with st.chat_message("assistant"):
            st.markdown(response.text)

        # Add assistant response to chat history memory
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    # 🛠️ UPGRADED ERROR HANDLER
    except Exception as e:
        if "503" in str(e) or "UNAVAILABLE" in str(e).upper():
            st.warning(
                "⚠️ Google's AI servers are experiencing temporary high traffic. Please wait 10 seconds and try again!")
        else:
            st.error(f"An error occurred: {e}")
