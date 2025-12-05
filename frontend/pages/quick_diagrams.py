# frontend/pages/quick_diagrams.py
import streamlit as st
import requests
from config import DIAGRAM_TYPES
from components.mermaid_renderer import render_mermaid
from utils.state_manager import add_to_diagram_history

def render(api_endpoint):
    """Render quick diagrams tab"""
    st.subheader("Generate Standard Diagrams")
    st.write("Generate predefined diagram types for the entire repository")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/user/repo",
            key="quick_repo"
        )
    
    with col2:
        diagram_type = st.selectbox(
            "Choose Diagram Type",
            DIAGRAM_TYPES
        )
    
    if st.button("🎨 Generate Diagram"):
        if not repo_url:
            st.error("Please enter a GitHub repository URL.")
        else:
            generate_standard_diagram(api_endpoint, repo_url, diagram_type)

def generate_standard_diagram(api_endpoint, repo_url, diagram_type):
    """Generate a standard diagram"""
    with st.spinner("Generating diagram..."):
        try:
            response = requests.post(
                f"{api_endpoint}/generate-diagram",
                json={"repo_url": repo_url, "diagram_type": diagram_type},
                timeout=60,
            )
            
            if response.status_code == 200:
                data = response.json()
                st.success("✅ Diagram Generated Successfully!")
                
                mermaid_code = data["mermaid_code"]
                repo_name = data.get("repo_name", "Unknown")
                
                # Save to history
                add_to_diagram_history(
                    diagram_type=diagram_type,
                    code=mermaid_code,
                    repo_name=repo_name,
                    prompt=f"Standard {diagram_type} diagram"
                )
                
                # Render diagram
                st.markdown("### 📊 Generated Diagram")
                theme = st.session_state.get('theme', 'Dark')
                mermaid_theme = 'dark' if theme == 'Dark' else 'default'
                render_mermaid(
                    mermaid_code,
                    height=600,
                    unique_id=f"quick_{diagram_type}",
                    theme=mermaid_theme
                )
                
                # Code view and download
                with st.expander("📝 View Mermaid Code"):
                    st.code(mermaid_code, language="mermaid")
                    
                    st.download_button(
                        label="💾 Download Mermaid Code",
                        data=mermaid_code,
                        file_name=f"{diagram_type}_diagram.mmd",
                        mime="text/plain"
                    )
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        
        except requests.exceptions.Timeout:
            st.error("Request timed out. The repository might be too large or the server is busy.")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the API. Make sure the FastAPI server is running.")
        except Exception as e:
            st.error(f"Error: {str(e)}")