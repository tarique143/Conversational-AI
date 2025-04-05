import google.generativeai as genai
import time
from datetime import datetime, timedelta
import streamlit as st

# Configure the API
genai.configure(api_key="AIzaSyBs0tJumqCnwjowFa2oWN7b3Y6SVOzSGGY")

class ChatBot:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro-latest")
        self.chat = None
        self.last_request_time = datetime.now()
        self.request_delay = timedelta(seconds=3)  # 3 seconds between requests
        self.setup_bot()

    def setup_bot(self):
        """Initialize the chat session"""
        if "chat" not in st.session_state:
            st.session_state.chat = self.model.start_chat(history=[])
        self.chat = st.session_state.chat

    def enforce_rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        elapsed = datetime.now() - self.last_request_time
        if elapsed < self.request_delay:
            wait_time = (self.request_delay - elapsed).total_seconds()
            time.sleep(wait_time)
        self.last_request_time = datetime.now()

    def get_response(self, user_input):
        """Get AI response with error handling"""
        try:
            self.enforce_rate_limit()
            response = self.chat.send_message(
                user_input,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500
                )
            )
            return response.text
            
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                return "I've reached my usage limit. Please try again later."
            return f"I'm having trouble responding. Error: {str(e)[:100]}..."

def main():
    st.title("Multilingual AI ChatBot")
    st.caption("Type in English or Hindi. Enter 'quit' to end conversation")
    
    # Initialize chatbot
    bot = ChatBot()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Hello! How can I help you today?"})
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Exit condition
        if prompt.lower() in ['quit', 'exit', 'bye']:
            st.session_state.messages.append({"role": "assistant", "content": "Goodbye! Have a great day!"})
            st.rerun()
        
        else:
            # Get bot response
            with st.spinner("Thinking..."):
                response = bot.get_response(prompt)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(response)
            
            # Rerun to update the display
            st.rerun()

if __name__ == "__main__":
    main()