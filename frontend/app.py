# frontend/app.py
import streamlit as st
from config import setup_page_config
from utils.state_manager import initialize_session_state
from components.sidebar import render_sidebar
from components.theme_manager import apply_theme
from pages import quick_diagrams, chat_interface, diagram_history

# Page configuration
setup_page_config()

# Initialize session state
initialize_session_state()

# Sidebar
api_endpoint = render_sidebar()

# Theme application
theme = st.session_state.get('theme', 'Dark')
apply_theme(theme)

# Main title
st.title("🚀 GitHub → Mermaid Diagram Generator")
st.write("Transform any GitHub repository into **beautiful Mermaid diagrams** using AI.")

# Tabs
tab1, tab2, tab3 = st.tabs([
    "📊 Quick Diagrams", 
    "💬 Chat & Custom Diagrams", 
    "📚 Diagram History"
])

# Render tab contents
with tab1:
    quick_diagrams.render(api_endpoint)

with tab2:
    chat_interface.render(api_endpoint)

with tab3:
    diagram_history.render()

# Footer
st.markdown(
    "<br><br><center>Made with ❤️ using OpenAI + FastAPI + Streamlit</center>", 
    unsafe_allow_html=True
)