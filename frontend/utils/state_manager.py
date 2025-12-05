# frontend/utils/state_manager.py
import streamlit as st

def initialize_session_state():
    """Initialize all session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_repo' not in st.session_state:
        st.session_state.current_repo = ""
    
    if 'diagram_history' not in st.session_state:
        st.session_state.diagram_history = []
    
    if 'theme' not in st.session_state:
        st.session_state.theme = 'Dark'
    
    # NEW: GitHub token for private repos
    if 'github_token' not in st.session_state:
        st.session_state.github_token = None
    
    # NEW: Auto-suggest history
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    # Clean up corrupted diagram history entries
    clean_diagram_history()

def clean_diagram_history():
    """Clean up any corrupted diagram history entries"""
    if st.session_state.diagram_history:
        cleaned_history = []
        for diagram in st.session_state.diagram_history:
            if isinstance(diagram, dict) and 'code' in diagram:
                cleaned_diagram = {
                    'type': diagram.get('type') or 'custom',
                    'code': diagram.get('code', ''),
                    'repo': diagram.get('repo') or 'Unknown',
                    'prompt': diagram.get('prompt') or 'No prompt'
                }
                cleaned_history.append(cleaned_diagram)
        st.session_state.diagram_history = cleaned_history

def add_to_diagram_history(diagram_type, code, repo_name, prompt):
    """Add a new diagram to history"""
    st.session_state.diagram_history.append({
        'type': diagram_type,
        'code': code,
        'repo': repo_name,
        'prompt': prompt
    })

def add_to_query_history(query: str):
    """Add query to history for auto-suggestions"""
    if query and query not in st.session_state.query_history:
        st.session_state.query_history.append(query)
        # Keep only last 20 queries
        if len(st.session_state.query_history) > 20:
            st.session_state.query_history = st.session_state.query_history[-20:]

def get_query_suggestions(partial_query: str) -> list:
    """Get auto-suggestions based on partial query"""
    
    # Default suggestions
    default_suggestions = [
        "Show me a sequence diagram",
        "Create an architecture diagram",
        "Visualize the authentication flow",
        "Show database schema diagram",
        "Create a flowchart for the main process",
        "Show component diagram",
        "Explain the API structure",
        "Show class diagram with relationships",
        "Create ER diagram for database",
        "Show the deployment architecture"
    ]
    
    if not partial_query:
        return default_suggestions[:5]
    
    partial_lower = partial_query.lower()
    
    # Filter from query history
    history_matches = [
        q for q in st.session_state.query_history 
        if partial_lower in q.lower()
    ]
    
    # Filter from default suggestions
    default_matches = [
        s for s in default_suggestions 
        if partial_lower in s.lower()
    ]
    
    # Combine and deduplicate
    all_suggestions = history_matches + default_matches
    seen = set()
    unique_suggestions = []
    for s in all_suggestions:
        if s.lower() not in seen:
            seen.add(s.lower())
            unique_suggestions.append(s)
    
    return unique_suggestions[:5]  # Return top 5

def clear_chat_history():
    """Clear chat history"""
    st.session_state.chat_history = []

def clear_diagram_history():
    """Clear diagram history"""
    st.session_state.diagram_history = []