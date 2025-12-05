# frontend/components/voice_input.py
import streamlit as st
import streamlit.components.v1 as components

def render_voice_input(key="voice_input", placeholder="Click microphone to speak..."):
    """
    Render a voice input button with speech-to-text functionality
    Returns the transcribed text when user stops speaking
    """
    
    voice_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: transparent;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 10px;
            }}
            
            .voice-container {{
                display: flex;
                gap: 10px;
                align-items: center;
                width: 100%;
            }}
            
            .voice-btn {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                position: relative;
                flex-shrink: 0;
            }}
            
            .voice-btn:hover {{
                transform: scale(1.05);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }}
            
            .voice-btn:active {{
                transform: scale(0.95);
            }}
            
            .voice-btn.listening {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                animation: pulse 1.5s infinite;
            }}
            
            .voice-btn.disabled {{
                background: #94a3b8;
                cursor: not-allowed;
                opacity: 0.6;
            }}
            
            @keyframes pulse {{
                0%, 100% {{
                    box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
                }}
                50% {{
                    box-shadow: 0 4px 25px rgba(245, 87, 108, 0.8);
                }}
            }}
            
            .mic-icon {{
                width: 24px;
                height: 24px;
                fill: white;
            }}
            
            .status-indicator {{
                position: absolute;
                top: -5px;
                right: -5px;
                width: 15px;
                height: 15px;
                border-radius: 50%;
                background: #10b981;
                border: 2px solid white;
                display: none;
            }}
            
            .voice-btn.listening .status-indicator {{
                display: block;
                animation: blink 1s infinite;
            }}
            
            @keyframes blink {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.3; }}
            }}
            
            .transcript-display {{
                flex: 1;
                padding: 12px 16px;
                background: #f1f5f9;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                min-height: 60px;
                display: flex;
                align-items: center;
                font-size: 14px;
                color: #334155;
                transition: all 0.3s ease;
            }}
            
            .transcript-display.active {{
                border-color: #667eea;
                background: #f8faff;
            }}
            
            .transcript-display.empty {{
                color: #94a3b8;
                font-style: italic;
            }}
            
            .error-message {{
                color: #ef4444;
                font-size: 12px;
                margin-top: 5px;
                display: none;
            }}
            
            .error-message.show {{
                display: block;
            }}
            
            .controls {{
                display: flex;
                gap: 8px;
                margin-top: 10px;
                justify-content: center;
            }}
            
            .control-btn {{
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 600;
                transition: all 0.2s ease;
            }}
            
            .clear-btn {{
                background: #fee2e2;
                color: #991b1b;
            }}
            
            .clear-btn:hover {{
                background: #fecaca;
            }}
            
            .copy-btn {{
                background: #dbeafe;
                color: #1e40af;
            }}
            
            .copy-btn:hover {{
                background: #bfdbfe;
            }}
        </style>
    </head>
    <body>
        <div class="voice-container">
            <button class="voice-btn" id="voiceBtn" title="Click to speak">
                <svg class="mic-icon" viewBox="0 0 24 24">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
                <div class="status-indicator"></div>
            </button>
            <div class="transcript-display empty" id="transcript">{placeholder}</div>
        </div>
        <div class="error-message" id="errorMsg"></div>
        <div class="controls">
            <button class="control-btn clear-btn" id="clearBtn" style="display:none;">Clear</button>
            <button class="control-btn copy-btn" id="copyBtn" style="display:none;">Copy</button>
        </div>
        
        <script>
            let recognition = null;
            let isListening = false;
            let finalTranscript = '';
            
            const voiceBtn = document.getElementById('voiceBtn');
            const transcriptDiv = document.getElementById('transcript');
            const errorMsg = document.getElementById('errorMsg');
            const clearBtn = document.getElementById('clearBtn');
            const copyBtn = document.getElementById('copyBtn');
            
            // Check for browser support
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = 'en-US';
                
                recognition.onstart = () => {{
                    isListening = true;
                    voiceBtn.classList.add('listening');
                    transcriptDiv.classList.add('active');
                    transcriptDiv.classList.remove('empty');
                    errorMsg.classList.remove('show');
                }};
                
                recognition.onresult = (event) => {{
                    let interimTranscript = '';
                    
                    for (let i = event.resultIndex; i < event.results.length; i++) {{
                        const transcript = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {{
                            finalTranscript += transcript + ' ';
                        }} else {{
                            interimTranscript += transcript;
                        }}
                    }}
                    
                    const displayText = finalTranscript + interimTranscript;
                    transcriptDiv.textContent = displayText || '{placeholder}';
                    
                    if (displayText) {{
                        transcriptDiv.classList.remove('empty');
                        clearBtn.style.display = 'block';
                        copyBtn.style.display = 'block';
                    }}
                    
                    // Send to Streamlit
                    if (finalTranscript.trim()) {{
                        window.parent.postMessage({{
                            type: 'streamlit:setComponentValue',
                            key: '{key}',
                            value: finalTranscript.trim()
                        }}, '*');
                    }}
                }};
                
                recognition.onerror = (event) => {{
                    console.error('Speech recognition error:', event.error);
                    
                    let errorText = 'Error: ';
                    switch(event.error) {{
                        case 'no-speech':
                            errorText += 'No speech detected. Please try again.';
                            break;
                        case 'audio-capture':
                            errorText += 'No microphone found. Please check your device.';
                            break;
                        case 'not-allowed':
                            errorText += 'Microphone permission denied. Please allow access.';
                            break;
                        case 'network':
                            errorText += 'Network error. Please check your connection.';
                            break;
                        default:
                            errorText += event.error;
                    }}
                    
                    errorMsg.textContent = errorText;
                    errorMsg.classList.add('show');
                    stopListening();
                }};
                
                recognition.onend = () => {{
                    stopListening();
                }};
                
            }} else {{
                voiceBtn.classList.add('disabled');
                voiceBtn.disabled = true;
                errorMsg.textContent = 'Speech recognition not supported in this browser. Try Chrome or Edge.';
                errorMsg.classList.add('show');
            }}
            
            voiceBtn.addEventListener('click', () => {{
                if (!recognition) return;
                
                if (isListening) {{
                    recognition.stop();
                }} else {{
                    finalTranscript = '';
                    recognition.start();
                }}
            }});
            
            clearBtn.addEventListener('click', () => {{
                finalTranscript = '';
                transcriptDiv.textContent = '{placeholder}';
                transcriptDiv.classList.add('empty');
                clearBtn.style.display = 'none';
                copyBtn.style.display = 'none';
                
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    key: '{key}',
                    value: ''
                }}, '*');
            }});
            
            copyBtn.addEventListener('click', () => {{
                const text = finalTranscript.trim();
                if (text) {{
                    navigator.clipboard.writeText(text).then(() => {{
                        copyBtn.textContent = '✓ Copied!';
                        setTimeout(() => {{
                            copyBtn.textContent = 'Copy';
                        }}, 2000);
                    }});
                }}
            }});
            
            function stopListening() {{
                isListening = false;
                voiceBtn.classList.remove('listening');
                transcriptDiv.classList.remove('active');
                
                if (!finalTranscript.trim()) {{
                    transcriptDiv.classList.add('empty');
                    transcriptDiv.textContent = '{placeholder}';
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    # Render the voice input component
    voice_text = components.html(voice_html, height=150)
    
    return voice_text