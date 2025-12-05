# frontend/components/sidebar.py
import streamlit as st
from config import DEFAULT_API_ENDPOINT

def render_sidebar():
    """Render sidebar with configuration and info"""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Theme switcher
        st.write("🌓 **Theme Settings**")
        theme = st.radio(
            "Choose Theme:", 
            ["Dark", "Light"], 
            index=0,
            key="theme_selector"
        )
        st.session_state.theme = theme
        
        st.divider()
        
        # API endpoint
        api_endpoint = st.text_input(
            "FastAPI Endpoint", 
            value=DEFAULT_API_ENDPOINT
        )
        
        st.divider()
        
        # NEW: GitHub Personal Access Token for Private Repos
        st.write("🔒 **Private Repository Access**")
        
        with st.expander("ℹ️ How to get GitHub Token"):
            st.markdown("""
            **Steps to create a Personal Access Token:**
            
            1. Go to GitHub → Settings
            2. Developer settings → Personal access tokens → Tokens (classic)
            3. Generate new token (classic)
            4. Select scopes: `repo` (Full control of private repositories)
            5. Copy the token
            6. Paste it below
            
            **Note:** Token is stored only in your browser session and never saved.
            """)
        
        github_token = st.text_input(
            "GitHub Personal Access Token",
            type="password",
            placeholder="ghp_xxxxxxxxxxxxxxxxxxxx",
            help="Required only for private repositories",
            key="github_token_input"
        )
        
        # Store token in session state
        if github_token:
            st.session_state.github_token = github_token
            st.success("✅ Token saved for this session")
        elif 'github_token' not in st.session_state:
            st.session_state.github_token = None
        
        st.divider()
        
        # Info section
        st.info("""
        **✨ Features:**
        - Generate standard diagrams
        - Chat for custom diagrams
        - Export diagrams as PNG/SVG
        - Access private repositories
        - Focus on specific components
        - Save diagram history
        
        **Tools:**
        - OpenAI GPT-4o
        - FastAPI
        - LangChain
        - MermaidJS
        """)
        
        st.divider()
        
        # Example prompts
        st.markdown("""
        ### 💡 Example Prompts:
        - "Show sequence diagram between frontend and backend"
        - "Create flowchart for authentication"
        - "Visualize the API routes"
        - "Show database relationships"
        - "Diagram the component hierarchy"
        """)
    
    return api_endpoint