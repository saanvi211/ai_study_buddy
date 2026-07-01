import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API Key not found. Please add GEMINI_API_KEY to your .env file.")
    st.stop()
else:
    client = genai.Client(api_key=api_key)

st.set_page_config(page_title="AI Learning Buddy saanvi", page_icon="🎓", layout="wide")

# Initialize session states
if "quiz_text" not in st.session_state:
    st.session_state.quiz_text = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def clear_state():
    st.session_state.quiz_text = None
    st.session_state.chat_history = []

# ================= SIDEBAR =================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4762/4762311.png", width=100) # Cute robot/learning icon
    st.title("Settings")
    st.markdown("Customize your learning experience here.")
    st.divider()
    
    topic = st.text_input("📚 What are you learning today?", placeholder="e.g. Photosynthesis, Machine Learning", on_change=clear_state)
    
    option = st.radio(
        "🎯 Choose Activity",
        [
            "Explain Concept",
            "Real-Life Example",
            "Generate Quiz",
            "Ask Anything"
        ],
        on_change=clear_state
    )
    
    st.divider()
    

# ================= MAIN AREA =================
st.title("🎓 AI Learning Buddy saanvi")
st.markdown("Hello! I am Saanvi, your patient and knowledgeable AI learning companion. Tell me what you're studying in the sidebar, and let's get started!")
st.divider()

if not topic:
    st.info("👈 Please enter a topic in the sidebar to begin.")
    st.stop()

st.subheader(f"Current Topic: **{topic}**")

# ----------------- EXPLAIN CONCEPT & REAL-LIFE EXAMPLE -----------------
if option in ["Explain Concept", "Real-Life Example"]:
    if st.button("Generate Explanation", type="primary"):
        if option == "Explain Concept":
            prompt = f"Explain {topic} in simple language for a beginner. Use bullet points and bold text for key terms to make it easy to read."
        elif option == "Real-Life Example":
            prompt = f"Give one simple real-life example of {topic}. Explain how the real-life example connects to the concept."
        
        with st.spinner("Saanvi is thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                with st.chat_message("assistant", avatar="🎓"):
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"Error generating response: {e}")

# ----------------- GENERATE QUIZ -----------------
elif option == "Generate Quiz":
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Generate Quiz", type="primary"):
            prompt = f"Create 5 multiple choice questions on {topic}. Do NOT provide the answers, only the questions and the options (A, B, C, D). Ensure there are blank lines between questions and options."
            with st.spinner("Generating quiz..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    st.session_state.quiz_text = response.text
                except Exception as e:
                    st.error(f"Error generating quiz: {e}")
    
    # If a quiz has been generated, show it and allow answering
    if st.session_state.quiz_text:
        with st.container(border=True):
            st.markdown("### 📝 Your Quiz")
            # Replace single newlines with double newlines so Streamlit doesn't collapse them
            st.markdown(st.session_state.quiz_text.replace('\n', '\n\n'))
        
        st.markdown("### ✍️ Submit Your Answers")
        user_answers = st.text_area("Type your answers here (e.g. 1-A, 2-B...)", height=150)
        
        if st.button("Submit Answers & Get Feedback", type="primary"):
            if user_answers.strip() == "":
                st.warning("Please enter your answers before submitting.")
            else:
                evaluate_prompt = f"Here is a quiz about {topic}:\n{st.session_state.quiz_text}\n\nHere are the student's answers:\n{user_answers}\n\nPlease act as a patient learning buddy. Evaluate the answers, tell them what they got right and wrong, provide the correct answers, and give encouraging feedback."
                with st.spinner("Saanvi is grading your quiz..."):
                    try:
                        eval_response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=evaluate_prompt
                        )
                        st.markdown("### 🏆 Feedback from Saanvi")
                        with st.chat_message("assistant", avatar="🎓"):
                            st.markdown(eval_response.text)
                    except Exception as e:
                        st.error(f"Error generating feedback: {e}")

# ----------------- ASK ANYTHING (CHAT UI) -----------------
elif option == "Ask Anything":
    st.markdown("Have specific doubts? Chat with Saanvi below!")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"], avatar="🎓" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])
            
    # Chat input
    if user_doubt := st.chat_input("Type your specific doubt here..."):
        # Add user message to state and display
        st.session_state.chat_history.append({"role": "user", "content": user_doubt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_doubt)
            
        prompt = f"The student is learning about '{topic}'. They have the following specific doubt: '{user_doubt}'. Act as a patient, encouraging AI learning buddy. Address their doubt directly and provide a clear, tailored explanation."
        
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("Saanvi is typing..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    st.markdown(response.text)
                    # Add assistant response to state
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error generating explanation: {e}")
