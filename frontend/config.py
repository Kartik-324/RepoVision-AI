# frontend/config.py
import streamlit as st

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="GitHub Mermaid Generator",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# API Configuration
DEFAULT_API_ENDPOINT = "http://localhost:8000"

# Diagram Types
DIAGRAM_TYPES = [
    "sequence",
    "component", 
    "database",
    "flowchart",
    "class",
    "state",
    "journey",
    "gantt",
    "mindmap"
]

# Diagram keywords for chat detection
DIAGRAM_KEYWORDS = [
    "diagram", "show", "visualize", "create",
    "generate", "draw", "chart", "flow", "architecture"
]