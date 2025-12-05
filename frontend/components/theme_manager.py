# frontend/components/theme_manager.py
import streamlit as st

def get_theme_config(theme):
    """Get theme configuration matching Claude's aesthetic"""
    if theme == "Dark":
        return {
            'bg_color': "#0e0e0e",
            'surface_color': "#1a1a1a",
            'text_primary': "#ffffff",
            'text_secondary': "#b0b0b0",
            'accent_color': "#a78bfa",
            'user_msg_bg': "#2d2d2d",
            'assistant_msg_bg': "#1a1a1a",
            'border_color': "#333333",
            'hover_color': "#2d2d2d",
            'mermaid_theme': "dark"
        }
    else:
        return {
            'bg_color': "#ffffff",
            'surface_color': "#f7f7f8",
            'text_primary': "#2e2e2e",
            'text_secondary': "#6b6b6b",
            'accent_color': "#7c3aed",
            'user_msg_bg': "#f0f0f0",
            'assistant_msg_bg': "#ffffff",
            'border_color': "#e5e5e5",
            'hover_color': "#f5f5f5",
            'mermaid_theme': "default"
        }

def apply_theme(theme):
    """Apply Claude-inspired theme CSS"""
    config = get_theme_config(theme)
    
    st.markdown(f"""
    <style>
    /* Import Google Fonts for better typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {{
        background-color: {config['bg_color']} !important;
        color: {config['text_primary']} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }}
    
    /* Fix Streamlit default styles */
    .stApp {{
        background-color: {config['bg_color']} !important;
    }}
    
    /* All text should be visible */
    p, span, div, label, h1, h2, h3, h4, h5, h6 {{
        color: {config['text_primary']} !important;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {{
        visibility: hidden;
    }}
    
    /* Title Styling */
    h1 {{
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: {config['text_primary']} !important;
        margin-bottom: 0.5rem !important;
        padding: 1rem 0 !important;
    }}
    
    h2, h3 {{
        color: {config['text_primary']} !important;
        font-weight: 600 !important;
    }}
    
    /* Repository Input */
    .repo-input-container {{
        background: {config['surface_color']};
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid {config['border_color']};
        margin-bottom: 1.5rem;
    }}
    
    /* Welcome Screen */
    .welcome-container {{
        text-align: center;
        padding: 3rem 1rem;
        max-width: 900px;
        margin: 0 auto;
    }}
    
    .welcome-container h2 {{
        font-size: 2rem;
        margin-bottom: 0.5rem;
        color: {config['text_primary']};
    }}
    
    .welcome-subtitle {{
        font-size: 1.1rem;
        color: {config['text_secondary']};
        margin-bottom: 2rem;
    }}
    
    .example-prompts {{
        margin-top: 2rem;
    }}
    
    .example-prompts h3 {{
        font-size: 1.2rem;
        margin-bottom: 1rem;
        color: {config['text_primary']};
    }}
    
    .prompt-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }}
    
    .prompt-card {{
        background: {config['surface_color']};
        border: 1px solid {config['border_color']};
        border-radius: 10px;
        padding: 1rem;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
        display: flex;
        align-items: start;
        gap: 0.75rem;
    }}
    
    .prompt-card:hover {{
        background: {config['hover_color']};
        border-color: {config['accent_color']};
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.15);
    }}
    
    .prompt-icon {{
        font-size: 1.5rem;
        flex-shrink: 0;
    }}
    
    .prompt-text {{
        font-size: 0.95rem;
        color: {config['text_primary']};
        line-height: 1.4;
    }}
    
    /* Message Containers */
    .message-container {{
        margin-bottom: 1.5rem;
        animation: fadeIn 0.3s ease-in;
    }}
    
    @keyframes fadeIn {{
        from {{
            opacity: 0;
            transform: translateY(10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    .message-header {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }}
    
    .message-avatar {{
        font-size: 1.2rem;
    }}
    
    .message-role {{
        font-weight: 600;
        font-size: 0.9rem;
        color: {config['text_secondary']};
    }}
    
    .message-content {{
        padding: 1rem 1.25rem;
        border-radius: 10px;
        line-height: 1.6;
        font-size: 1rem;
    }}
    
    .user-message {{
        background: {config['user_msg_bg']};
        color: {config['text_primary']};
        border-left: 3px solid {config['accent_color']};
    }}
    
    .assistant-message {{
        background: {config['assistant_msg_bg']};
        color: {config['text_primary']};
        border: 1px solid {config['border_color']};
    }}
    
    /* Diagram Container */
    .diagram-container {{
        background: {config['surface_color']};
        border: 1px solid {config['border_color']};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}
    
    .diagram-container h3 {{
        margin-top: 0;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }}
    
    /* Suggestions */
    .suggestions-container {{
        margin-top: 1rem;
        padding: 1rem;
        background: {config['surface_color']};
        border-radius: 8px;
        border: 1px solid {config['border_color']};
    }}
    
    .suggestions-header {{
        font-size: 0.9rem;
        font-weight: 600;
        color: {config['text_secondary']};
        margin-bottom: 0.75rem;
    }}
    
    /* Input Container */
    .input-container {{
        position: sticky;
        bottom: 0;
        background: {config['bg_color']};
        padding: 1rem 0;
        border-top: 1px solid {config['border_color']};
        z-index: 100;
    }}
    
    /* Streamlit Input Styling */
    .stTextInput > div > div > input {{
        background: {config['surface_color']} !important;
        border: 2px solid {config['border_color']} !important;
        border-radius: 10px !important;
        color: {config['text_primary']} !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }}
    
    .stTextInput > div > div > input::placeholder {{
        color: {config['text_secondary']} !important;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {config['accent_color']} !important;
        box-shadow: 0 0 0 1px {config['accent_color']} !important;
    }}
    
    /* Text input labels */
    .stTextInput > label {{
        color: {config['text_primary']} !important;
        font-weight: 600 !important;
    }}
    
    /* Button Styling */
    .stButton > button {{
        background: {config['accent_color']} !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }}
    
    .stButton > button:hover {{
        background: #9d7dff !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(167, 139, 250, 0.4) !important;
    }}
    
    .stButton > button:active {{
        transform: translateY(0);
    }}
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {{
        background: {config['surface_color']} !important;
        color: {config['text_primary']} !important;
        border: 2px solid {config['border_color']} !important;
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        background: {config['hover_color']} !important;
        border-color: {config['accent_color']} !important;
    }}
    
    /* Download and Secondary Buttons */
    .stDownloadButton > button {{
        background: {config['surface_color']} !important;
        color: {config['text_primary']} !important;
        border: 1px solid {config['border_color']} !important;
    }}
    
    .stDownloadButton > button:hover {{
        background: {config['hover_color']} !important;
        border-color: {config['accent_color']} !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background: transparent !important;
        padding: 0.5rem;
        border-radius: 10px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: {config['surface_color']} !important;
        border: 2px solid {config['border_color']} !important;
        color: {config['text_primary']} !important;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {config['accent_color']} !important;
        color: white !important;
        border-color: {config['accent_color']} !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background: {config['surface_color']} !important;
        border: 1px solid {config['border_color']} !important;
        border-radius: 8px !important;
        color: {config['text_primary']} !important;
    }}
    
    /* Selectbox */
    .stSelectbox > div > div {{
        background: {config['surface_color']} !important;
        border: 1px solid {config['border_color']} !important;
        border-radius: 10px !important;
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {config['surface_color']} !important;
        border-right: 2px solid {config['border_color']} !important;
    }}
    
    section[data-testid="stSidebar"] .stMarkdown {{
        color: {config['text_primary']} !important;
    }}
    
    section[data-testid="stSidebar"] p {{
        color: {config['text_primary']} !important;
    }}
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {config['text_primary']} !important;
    }}
    
    /* Info boxes */
    .stAlert {{
        background: {config['surface_color']} !important;
        border: 2px solid {config['border_color']} !important;
        border-radius: 10px !important;
        color: {config['text_primary']} !important;
        padding: 1rem !important;
    }}
    
    /* Info box text */
    .stAlert p, .stAlert span, .stAlert div {{
        color: {config['text_primary']} !important;
    }}
    
    /* Markdown in info boxes */
    .stAlert .stMarkdown {{
        color: {config['text_primary']} !important;
    }}
    
    /* Spinner */
    .stSpinner > div {{
        border-top-color: {config['accent_color']} !important;
    }}
    
    /* Divider */
    hr {{
        border-color: {config['border_color']} !important;
    }}
    
    /* Code blocks */
    .stCodeBlock {{
        background: {config['surface_color']} !important;
        border: 1px solid {config['border_color']} !important;
        border-radius: 8px !important;
    }}
    
    /* Success/Error messages */
    .stSuccess {{
        background: rgba(16, 185, 129, 0.1) !important;
        border-left: 3px solid #10b981 !important;
        color: {config['text_primary']} !important;
    }}
    
    .stError {{
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 3px solid #ef4444 !important;
        color: {config['text_primary']} !important;
    }}
    
    /* Markdown content */
    .stMarkdown {{
        color: {config['text_primary']} !important;
    }}
    
    .stMarkdown p {{
        color: {config['text_primary']} !important;
    }}
    
    .stMarkdown strong {{
        color: {config['text_primary']} !important;
    }}
    
    /* Blockquotes */
    blockquote {{
        border-left: 4px solid {config['accent_color']} !important;
        padding-left: 1rem !important;
        color: {config['text_secondary']} !important;
        background: {config['surface_color']} !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        margin: 1rem 0 !important;
    }}
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {config['bg_color']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {config['border_color']};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {config['accent_color']};
    }}
    </style>
    """, unsafe_allow_html=True)