# frontend/components/smart_autocomplete.py
import streamlit as st
import streamlit.components.v1 as components

def render_smart_input(key: str, placeholder: str, suggestions: list):
    """
    Render smart autocomplete input with inline suggestions
    Similar to GitHub Copilot - shows grayed suggestion, press Tab to accept
    """
    
    # Get theme
    theme = st.session_state.get('theme', 'Dark')
    bg_color = "#1a1a1a" if theme == "Dark" else "#f7f7f8"
    text_color = "#ffffff" if theme == "Dark" else "#2e2e2e"
    suggestion_color = "#666666" if theme == "Dark" else "#999999"
    border_color = "#333333" if theme == "Dark" else "#e5e5e5"
    focus_color = "#a78bfa" if theme == "Dark" else "#7c3aed"
    
    # Convert suggestions to JavaScript array
    suggestions_js = str(suggestions).replace("'", '"')
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: transparent;
                padding: 0;
            }}
            
            .autocomplete-container {{
                position: relative;
                width: 100%;
            }}
            
            .input-wrapper {{
                position: relative;
                width: 100%;
            }}
            
            #suggestion-overlay {{
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                pointer-events: none;
                color: {suggestion_color};
                padding: 12px 16px;
                font-size: 16px;
                white-space: pre;
                overflow: hidden;
                border: 2px solid transparent;
                border-radius: 10px;
                background: transparent;
                font-family: inherit;
            }}
            
            #user-input {{
                width: 100%;
                padding: 12px 16px;
                font-size: 16px;
                background: {bg_color};
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: 10px;
                outline: none;
                transition: all 0.2s ease;
                font-family: inherit;
                position: relative;
                z-index: 1;
            }}
            
            #user-input::placeholder {{
                color: {suggestion_color};
            }}
            
            #user-input:focus {{
                border-color: {focus_color};
                box-shadow: 0 0 0 1px {focus_color};
            }}
            
            .hint-text {{
                margin-top: 8px;
                font-size: 12px;
                color: {suggestion_color};
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .kbd {{
                padding: 2px 6px;
                background: {bg_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                font-family: monospace;
                font-size: 11px;
            }}
            
            .suggestion-list {{
                margin-top: 8px;
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }}
            
            .suggestion-chip {{
                padding: 6px 12px;
                background: {bg_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                font-size: 13px;
                color: {text_color};
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            
            .suggestion-chip:hover {{
                background: {focus_color};
                color: white;
                border-color: {focus_color};
                transform: translateY(-1px);
            }}
        </style>
    </head>
    <body>
        <div class="autocomplete-container">
            <div class="input-wrapper">
                <div id="suggestion-overlay"></div>
                <input 
                    type="text" 
                    id="user-input" 
                    placeholder="{placeholder}"
                    autocomplete="off"
                />
            </div>
            
            <div class="hint-text" id="hint" style="display: none;">
                Press <span class="kbd">Tab</span> to accept suggestion
            </div>
            
            <div class="suggestion-list" id="suggestion-chips"></div>
        </div>
        
        <script>
            const input = document.getElementById('user-input');
            const overlay = document.getElementById('suggestion-overlay');
            const hint = document.getElementById('hint');
            const chipsContainer = document.getElementById('suggestion-chips');
            
            // All available suggestions
            const allSuggestions = {suggestions_js};
            
            let currentSuggestion = '';
            let inputValue = '';
            
            // Find best matching suggestion
            function findBestMatch(text) {{
                if (!text || text.length < 3) return '';
                
                const textLower = text.toLowerCase();
                
                // Find suggestions that start with or contain the text
                const matches = allSuggestions.filter(s => 
                    s.toLowerCase().startsWith(textLower)
                );
                
                if (matches.length > 0) {{
                    return matches[0];
                }}
                
                // Fuzzy match - find suggestions containing the words
                const words = textLower.split(' ');
                const fuzzyMatches = allSuggestions.filter(s => {{
                    const sLower = s.toLowerCase();
                    return words.every(word => sLower.includes(word));
                }});
                
                return fuzzyMatches.length > 0 ? fuzzyMatches[0] : '';
            }}
            
            // Update suggestion overlay
            function updateSuggestion() {{
                inputValue = input.value;
                currentSuggestion = findBestMatch(inputValue);
                
                if (currentSuggestion && inputValue) {{
                    // Show the suggestion with the typed text + grayed remaining
                    const remaining = currentSuggestion.slice(inputValue.length);
                    overlay.textContent = inputValue + remaining;
                    hint.style.display = 'flex';
                }} else {{
                    overlay.textContent = '';
                    hint.style.display = 'none';
                }}
                
                updateSuggestionChips();
                
                // Send value to Streamlit
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: inputValue
                }}, '*');
            }}
            
            // Update suggestion chips
            function updateSuggestionChips() {{
                const filtered = inputValue ? 
                    allSuggestions.filter(s => 
                        s.toLowerCase().includes(inputValue.toLowerCase())
                    ).slice(0, 3) : 
                    allSuggestions.slice(0, 3);
                
                chipsContainer.innerHTML = '';
                filtered.forEach(suggestion => {{
                    const chip = document.createElement('div');
                    chip.className = 'suggestion-chip';
                    chip.textContent = suggestion;
                    chip.onclick = () => {{
                        input.value = suggestion;
                        inputValue = suggestion;
                        updateSuggestion();
                        input.focus();
                    }};
                    chipsContainer.appendChild(chip);
                }});
            }}
            
            // Handle Tab key to accept suggestion
            input.addEventListener('keydown', (e) => {{
                if (e.key === 'Tab' && currentSuggestion && inputValue) {{
                    e.preventDefault();
                    input.value = currentSuggestion;
                    updateSuggestion();
                }}
                
                // Handle Enter to submit
                if (e.key === 'Enter') {{
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: {{ submitted: true, value: input.value }}
                    }}, '*');
                }}
            }});
            
            // Update on input
            input.addEventListener('input', updateSuggestion);
            
            // Initial render
            updateSuggestionChips();
            
            // Focus input on load
            input.focus();
        </script>
    </body>
    </html>
    """
    
    # Render the component
    result = components.html(html_code, height=120, scrolling=False)
    
    return result