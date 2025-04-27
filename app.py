import streamlit as st
import requests
import base64
import subprocess
import time

# Function to ensure server is running
def ensure_server_running():
    """Ensure that the chatbot server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200 and response.json().get("status") == "healthy":
            print("Chatbot server already running.")
            return
    except requests.exceptions.RequestException:
        print("Chatbot server not running. Starting server...")

    # Start chatbot_server.py if not running
    subprocess.Popen(["python", "chatbot_server.py"])
    time.sleep(5)  # Give time for server to start

# Set page config
st.set_page_config(
    page_title="FATIMA.ai | UTD Assistant",
    page_icon="🤖",
    layout="wide"
)

# Ensure the backend server is running
ensure_server_running()

##########################################################################
# UTD color scheme
UTD_ORANGE = "#CC5500"  # Soft Light Peach Orange
UTD_GREEN = "#06402B"   # Classic UTD Dark Green
UTD_WHITE = "#FFFFFF"   # White

# Custom CSS to apply the UTD color scheme and create the title container
css = f"""
<style>
    .main .block-container {{
        padding-top: 1rem;
        background-color: {UTD_WHITE};
        padding-bottom: 100vh; /* Make background color fill the entire page */
    }}
    .stApp {{
        background-color: {UTD_WHITE};
    }}
    .title-container {{
        background-color: {UTD_GREEN};
        padding: 1.5rem;
        border-radius: 5px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .title-container h1 {{
        color: {UTD_WHITE};
        margin: 0;
        font-size: 2.5rem;
    }}
    .logo-in-container {{
        height: 120px;
        margin-right: 1rem;
    }}
    .footer-text {{
        color: black;
        font-weight: normal;
    }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Function to load and encode an image
def get_encoded_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Try to get the encoded logo
try:
    encoded_logo = get_encoded_image("utd_logo.png")
    logo_available = True
except FileNotFoundError:
    logo_available = False

# Try to get the encoded fatima icon
try:
    encoded_fatima_icon = get_encoded_image("fatima.png")
    fatima_icon_available = True
except FileNotFoundError:
    fatima_icon_available = False

# App title and logo in UTD green container
if logo_available:
    title_html = f"""
    <div class="title-container">
        <h1>FATIMA.ai - Flexible Academic Text Intelligence and Management Assistant</h1>
        <img class="logo-in-container" src="data:image/png;base64,{encoded_logo}" alt="UTD Logo">
    </div>
    """
else:
    title_html = f"""
    <div class="title-container">
        <h1>FATIMA.ai - Flexible Academic Text Intelligence and Management Assistant</h1>
        <div>Logo not found</div>
    </div>
    """

#########################################################################

# Header
st.markdown(title_html, unsafe_allow_html=True)

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for chat in st.session_state.chat_history:

    # User Message (right aligned)
    user_message_html = f"""
    <div style="
        display: inline-block;
        background-color: {UTD_ORANGE};
        border: 2px solid {UTD_WHITE};
        padding: 1rem 1.5rem;
        border-radius: 20px;
        max-width: 70%;
        float: right;
        text-align: left;
        color: {UTD_WHITE};
        font-weight: bold;
        margin-bottom: 2rem;
    ">
        <strong>You:</strong> {chat['question']}
    </div>
    """

    # FATIMA Response (left aligned)
    if fatima_icon_available:
        fatima_message_html = f"""
        <div style="
            display: inline-block;
            background-color: {UTD_GREEN};
            border: 2px solid {UTD_WHITE};
            padding: 1rem 1.5rem;
            border-radius: 20px;
            max-width: 70%;
            text-align: left;
            color: {UTD_WHITE};
            font-weight: bold;
            margin-bottom: 0.5rem;
        ">
            <img src="data:image/png;base64,{encoded_fatima_icon}" style="width: 40px; height: 40px; border-radius: 50%; vertical-align: middle; margin-right: 10px;"> 
            <strong>FATIMA:</strong> {chat['answer']}
        """
    else:
        fatima_message_html = f"""
        <div style="
            display: inline-block;
            background-color: {UTD_GREEN};
            border: 2px solid {UTD_WHITE};
            padding: 1rem 1.5rem;
            border-radius: 20px;
            max-width: 70%;
            text-align: left;
            color: {UTD_WHITE};
            font-weight: bold;
            margin-bottom: 0.5rem;
        ">
            <strong>FATIMA:</strong> {chat['answer']}
        """

    if chat['contact_info']:
        fatima_message_html += "<br><br><strong>Contact Information:</strong><ul>"
        for contact in chat['contact_info']:
            fatima_message_html += f"""
            <li>📧 {contact['email']} | 📞 {contact['phone']} | 📍 {contact['location']}</li>
            """
        fatima_message_html += "</ul>"

    if chat['sources']:
        fatima_message_html += f"<br><br><strong>Sources:</strong> {', '.join(chat['sources'])}"

    fatima_message_html += "</div>"

    # Combine both, with USER first and then FATIMA
    st.markdown(user_message_html, unsafe_allow_html=True)
    st.markdown(fatima_message_html, unsafe_allow_html=True)
    st.markdown("<div style='clear: both;'></div>", unsafe_allow_html=True)

# Input area
user_input = st.text_input("Ask FATIMA about UTD...", key="user_input")
send_button = st.button("Ask FATIMA")

# Handle input
if send_button and user_input:
    with st.spinner('FATIMA is thinking...'):
        try:
            response = requests.post(
                "http://localhost:8000/chatbot",
                json={"query": user_input},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()

                # Add to chat history
                st.session_state.chat_history.append({
                    "question": user_input,
                    "answer": result.get("answer", ""),
                    "sources": result.get("sources", []),
                    "contact_info": result.get("contact_info", [])
                })

                # Clear input
                st.rerun()
            else:
                st.error(f"Error: Server returned status code {response.status_code}")

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the server: {str(e)}")
            st.info("Make sure the chatbot server is running (python chatbot_server.py)")

# Footer
st.markdown("---")
st.markdown("<div class='footer-text'>FATIMA.ai - Powered by advanced language models and UTD's knowledge base</div>", unsafe_allow_html=True)
st.markdown("<div class='footer-text'>&copy; 2024 UTD Information Systems</div>", unsafe_allow_html=True)
