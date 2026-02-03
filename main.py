import streamlit as st
from openai import OpenAI

# --- 1. PAGE CONFIGURATION (The Canvas) ---
st.set_page_config(
    page_title="BidWinner AI",
    page_icon="⚡",
    layout="wide",  # WIDER layout for a dashboard feel
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS (The Skin) ---
# This injects custom HTML/CSS to remove the "Streamlit" look
st.markdown("""
<style>
    /* Main Header Styling */
    .main-header {
        font-size: 2.5rem;
        color: #FF4B4B; /* Streamlit Red/Orange */
        font-weight: 800;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    /* Input Field Styling */
    .stTextArea textarea {
        background-color: #f0f2f6;
        color: #31333F; /* Force text to be Dark Gray/Black */
        border-radius: 10px;
    }
    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE (The Memory) ---
# We use this to remember if the API key is valid so we don't check every time
if 'api_key_valid' not in st.session_state:
    st.session_state['api_key_valid'] = False

# --- 4. SIDEBAR (The Control Panel) ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # AUTOMATIC AUTHENTICATION
    # We check if the key is in Secrets. If yes, we use it.
    if 'OPENAI_API_KEY' in st.secrets:
        st.success("✅ AI Server Connected (SaaS Mode)")
        api_key = st.secrets['OPENAI_API_KEY']
        st.session_state['api_key'] = api_key
        st.session_state['api_key_valid'] = True
    else:
        # Fallback for localhost if you didn't set up secrets.toml locally
        api_key = st.text_input("Enter API Key", type="password")
        if api_key:
             st.session_state['api_key'] = api_key
             st.session_state['api_key_valid'] = True

    st.divider()
    
    # Strategy Settings
    st.write("### 🎛️ Strategy Console")
    tone = st.selectbox("Tone Strategy", ["Professional & Direct", "Persuasive & Salesy", "Casual & Confident"])
    length = st.select_slider("Response Length", options=["Tweet Sized", "Short Paragraph", "Detailed Letter"])

# --- 5. MAIN INTERFACE (The Dashboard) ---

# Custom Header using HTML
st.markdown('<p class="main-header">⚡ The Bid-Winner AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Dominate the Freelance Market. Stop Writing, Start Closing.</p>', unsafe_allow_html=True)

if not st.session_state['api_key_valid']:
    # Empty State (When not logged in)
    st.warning("⚠️ Waiting for API Connection in the Sidebar...")
    st.stop() # Stop the app from rendering further

# Layout Columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📄 1. The Client's Need (Job Post)")
    job_desc = st.text_area(
        "Job Description", 
        height=300, 
        placeholder="Paste the Upwork/Job post here...", 
        label_visibility="collapsed"
    )

with col2:
    st.markdown("#### 🛡️ 2. Your Weapon (Resume/Skills)")
    user_skills = st.text_area(
        "Your Skills", 
        height=300, 
        placeholder="Paste your resume summary or skills list here...", 
        label_visibility="collapsed"
    )

# --- 6. GENERATION LOGIC ---
st.markdown("---")
generate_col, _ = st.columns([1, 2]) # Make button smaller/aligned left

with generate_col:
    run_btn = st.button("🚀 EXECUTE STRATEGY", type="primary")

if run_btn:
    if not job_desc or not user_skills:
        st.error("⚠️ Tactical Error: Missing Data. Fill in both text areas.")
    else:
        client = OpenAI(api_key=st.session_state['api_key'])
        
        with st.spinner("🤖 Analyzing Job Metrics... Drafting Counter-Pick..."):
            try:
                # Optimized System Prompt
                system_prompt = f"""
                You are a world-class expert copywriter. Write a freelance proposal.
                TONE: {tone}.
                LENGTH: {length}.
                
                INSTRUCTIONS:
                - Hook the reader in the first sentence.
                - Address the client's specific pain points found in the job description.
                - Prove credibility using the user's skills.
                - NO AI JARGON. Sound human.
                - Call to action at the end.
                """
                
                user_prompt = f"JOB: {job_desc}\n\nMY SKILLS: {user_skills}"
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                
                result = response.choices[0].message.content
                
                # --- 7. RESULT DISPLAY ---
                st.success("✅ Mission Accomplished.")
                st.markdown("### 📋 Your Winning Proposal")

                # using text_area instead of code block for better readability and editing
                st.text_area(
                    label="Edit and Copy your proposal below:", 
                    value=result, 
                    height=400, # Taller box for vertical scrolling
                    key="final_output"
                )

                st.caption("Tip: You can edit the text above before copying it!")
                
            except Exception as e:
                st.error(f"System Failure: {e}")