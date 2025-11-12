import streamlit as st
import requests
import uuid

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Credit Card Advisor",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        max-width: 900px;
        margin: 0 auto;
        overflow-y: auto;
    }
            
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    
    .user-message {
        background: #667eea;
        color: black;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 1rem 0;
        margin-left: auto;
        max-width: 70%;
        float: right;
        clear: both;
        font-size: large;
    }
    
    .bot-message {
        background: #f1f3f4;
        color: #333;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 1rem 0;
        max-width: 70%;
        float: left;
        clear: both;
        font-size: large;
    }

    .card-rec {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: black;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .card-rec h3 {
        margin-top: 0;
        color: balck;
    }
    
    .stTextInput input {
        border-radius: 25px;
        padding: 1rem;
        border: 2px solid #667eea;
    }    
    
    .stButton button {
        background: #667eea;
        color: black;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        border: none;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background: #764ba2;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .main-header {
        text-align: center;
        color: black;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
    }

    .stat-box {
        background: rgba(255,255,255,0.2);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: black;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_stage" not in st.session_state:
    st.session_state.conversation_stage = "collecting" 

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "income": None,
        "spending": {},
        "preferences": [],
        "credit_score": None
    }

# API Functions
def send_message(message: str) -> str:
    """Send message to backend and get response"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": message,
                "session_id": st.session_state.session_id
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get("reply", "Sorry, I couldn't process that.")
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return "I'm having trouble connecting. Please try again."

def reset_conversation():
    """Reset the conversation"""
    try:
        requests.post(
            f"{API_BASE_URL}/reset",
            params={"session_id": st.session_state.session_id}
        )
    except:
        pass
    
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.conversation_stage = "collecting"
    st.session_state.user_profile = {
        "income": None,
        "spending": {},
        "preferences": [],
        "credit_score": None
    }


# UI Components
def render_header():
    """Render main header"""
    st.markdown("""
    <div class="main-header">
        <h1>💳 Credit Card Advisor</h1>
        <p>Your AI-powered guide to finding the perfect credit card</p>
    </div>
    """, unsafe_allow_html=True)

def render_stats():
    """Render stats boxes"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stat-box">
            <h2>20+</h2>
            <p>Credit Cards</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-box">
            <h2>AI-Powered</h2>
            <p>Recommendations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-box">
            <h2>100%</h2>
            <p>Personalized</p>
        </div>
        """, unsafe_allow_html=True)

def render_message(role: str, content: str):
    """Render a chat message"""
    if role == "user":
        st.markdown(f'<div class="user-message">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{content}</div>', unsafe_allow_html=True)
    st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True)

def render_chat_history():
    """Render all chat messages"""
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            render_message(msg["role"], msg["content"])

def render_quick_actions():
    """Render quick action buttons"""
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Start Over", use_container_width=True):
            reset_conversation()
            st.rerun()
    
    # with col2:
    #     if st.button("View Profile", use_container_width=True):
    #         st.session_state.show_profile = True
    
    with col2:
        if st.button("How It Works", use_container_width=True):
            st.session_state.show_help = True

def render_profile_sidebar():
    """Render user profile in sidebar"""
    with st.sidebar:
        st.markdown("### Your Profile")
        
        profile = st.session_state.user_profile
        
        if profile["income"]:
            st.markdown(f"**Income:** ₹{profile['income']:,}/month")
        
        if profile["spending"]:
            st.markdown("**Spending:**")
            for category, amount in profile["spending"].items():
                st.markdown(f"- {category}: ₹{amount:,}")
        
        if profile["preferences"]:
            st.markdown("**Preferences:**")
            for pref in profile["preferences"]:
                st.markdown(f"- {pref}")
        
        if profile["credit_score"]:
            st.markdown(f"**Credit Score:** {profile['credit_score']}")
        
        st.markdown("---")
        st.markdown(f"**Session ID:** `{st.session_state.session_id[:8]}...`")

def render_help_modal():
    """Render help information"""
    if st.session_state.get("show_help"):
        st.markdown("""
        ### How It Works
        
        1. **Chat with our AI:** Answer questions about your income, spending, and preferences
        2. **Get Personalized Recommendations:** Our AI analyzes 20+ credit cards to find your best matches
        3. **Compare & Choose:** Review detailed benefits and reward simulations
        4. **Apply:** Click through to apply for your chosen card
        
        **What We'll Ask:**
        - Monthly income
        - Spending on fuel, travel, groceries, dining
        - Preferred benefits (cashback, rewards, lounge access)
        - Credit score (optional)
        
        **Privacy:** Your data is used only for recommendations and not stored permanently.
        """)
        
        if st.button("Got it!"):
            st.session_state.show_help = False
            st.rerun()

# Main App
def main():
    render_header()
    render_stats()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        welcome_msg = """Hi! I'm your Credit Card Advisor. I'll help you find the perfect credit card based on your needs.

To get started, could you tell me your **approximate monthly income** in rupees?"""
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
    
    # Render chat history
    render_chat_history()
    
    # Chat input
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Type your message...",
                key="user_input",
                placeholder="Type your answer here...",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_button = st.form_submit_button("Send", use_container_width=True)
    
    if submit_button and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        thinking_index = len(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": "Thinking..."})
        st.rerun()
        
    elif st.session_state.messages and st.session_state.messages[-1]["content"] == "Thinking...":
        with st.spinner("Processing..."):
            user_message = st.session_state.messages[-2]["content"]
            bot_response = send_message(user_message)

        st.session_state.messages[-1]["content"] = bot_response
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    render_quick_actions()
    render_profile_sidebar()
    render_help_modal()

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: black; opacity: 0.8;">
        <p>Credit Card Advisor | Powered by AI | Made with ❤️ by Kritika</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()