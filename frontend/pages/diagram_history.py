# frontend/pages/diagram_history.py
import streamlit as st
from components.mermaid_renderer import render_mermaid
from utils.state_manager import clear_diagram_history
from utils.helpers import truncate_text

def render():
    """Render diagram history tab"""
    st.subheader("📚 Your Diagram History")
    
    if not st.session_state.diagram_history:
        st.info("No diagrams generated yet. Start by creating some diagrams in other tabs!")
    else:
        st.write(f"**Total Diagrams:** {len(st.session_state.diagram_history)}")
        
        # Display diagrams in reverse order (newest first)
        for idx, diagram in enumerate(reversed(st.session_state.diagram_history)):
            display_diagram_item(idx, diagram)
        
        # Clear history button
        st.divider()
        if st.button("🗑️ Clear All History"):
            clear_diagram_history()
            st.rerun()

def display_diagram_item(idx, diagram):
    """Display a single diagram history item"""
    # Safe handling of diagram fields
    diagram_type = diagram.get('type', 'custom') or 'custom'
    repo_name = diagram.get('repo', 'Unknown')
    prompt_text = diagram.get('prompt', 'No prompt')
    diagram_code = diagram.get('code', '')
    
    # Create expander title
    title = f"🎨 {diagram_type.title()} - {repo_name} | {truncate_text(prompt_text, 50)}"
    
    with st.expander(title):
        st.markdown(f"**Repository:** {repo_name}")
        st.markdown(f"**Type:** {diagram_type}")
        st.markdown(f"**Request:** {prompt_text}")
        
        # Render diagram
        theme = st.session_state.get('theme', 'Dark')
        mermaid_theme = 'dark' if theme == 'Dark' else 'default'
        render_mermaid(
            diagram_code,
            height=400,
            unique_id=f"history_{idx}",
            theme=mermaid_theme
        )
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="💾 Download Code",
                data=diagram_code,
                file_name=f"{diagram_type}_diagram.mmd",
                mime="text/plain",
                key=f"hist_download_{idx}"
            )
        with col2:
            if st.button("📋 View Code", key=f"copy_{idx}"):
                st.code(diagram_code, language="mermaid")