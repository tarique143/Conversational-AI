import google.generativeai as genai
import streamlit as st
from datetime import datetime, timedelta
import time
import pyttsx3  # For text-to-speech
import speech_recognition as sr  # For speech-to-text

# Configure the API
genai.configure(api_key="AIzaSyBs0tJumqCnwjowFa2oWN7b3Y6SVOzSGGY")

class ChatBot:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro-latest")
        self.chat = None
        self.last_request_time = datetime.now()
        self.request_delay = timedelta(seconds=3)
        self.setup_bot()
        self.recognizer = sr.Recognizer()  # Speech recognizer
        self.engine = pyttsx3.init()  # Text-to-speech engine
        
        # Set Hindi voice if available
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'hindi' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

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
    
    def speak(self, text):
        """Convert text to speech"""
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        """Convert speech to text"""
        with sr.Microphone() as source:
            st.info("Listening... Speak now")
            audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio, )  # Hindi by default
                return text
            except Exception as e:
                st.error(f"Could not understand audio: {e}")
                return None

def main():
    st.title("🎙️ Multilingual Voice ChatBot")
    st.caption("Chat in English or Hindi using voice or text. Say 'quit' to end conversation")
    
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
    
    # Voice input button
    if st.button("🎤 Speak"):
        user_input = bot.listen()
        if user_input:
            process_input(user_input, bot)
    
    # Text input
    if prompt := st.chat_input("Type your message here..."):
        process_input(prompt, bot)

def process_input(prompt, bot):
    """Process user input and generate response"""
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Exit condition
    if prompt.lower() in ['quit', 'exit', 'bye', 'बंद करो', 'अलविदा']:
        response = "Goodbye! Have a great day! / अलविदा! आपका दिन शुभ हो!"
        st.session_state.messages.append({"role": "assistant", "content": response})
        bot.speak(response)
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
        
        # Speak the response
        bot.speak(response)
        
        # Rerun to update the display
        st.rerun()

if __name__ == "__main__":
    main()