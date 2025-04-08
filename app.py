import streamlit as st
import requests

# Set page config
st.set_page_config(
    page_title="FATIMA.ai | UTD Assistant",
    page_icon="🤖",
    layout="wide"
)

# Header
st.title("FATIMA.ai")
st.subheader("Flexible Academic Text Intelligence and Management Assistant")
st.write("Your intelligent guide to UTD's academic information")

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for chat in st.session_state.chat_history:
    st.markdown(f"**You:** {chat['question']}")
    st.markdown(f"**FATIMA:** {chat['answer']}")
    
    # Display contact information in a structured way
    if chat['contact_info']:
        st.markdown("**Contact Information:**")
        for contact in chat['contact_info']:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"📧 {contact['email']}")
            with col2:
                st.markdown(f"📞 {contact['phone']}")
            with col3:
                st.markdown(f" {contact['location']}")
    
    if chat['sources']:
        st.markdown("**Sources:** " + ", ".join(chat['sources']))

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
st.write("FATIMA.ai - Powered by advanced language models and UTD's knowledge base")
st.write("© 2024 UTD Information Systems")