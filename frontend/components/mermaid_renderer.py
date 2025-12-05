# frontend/components/mermaid_renderer.py
import streamlit as st
import streamlit.components.v1 as components
from utils.helpers import generate_key
import re

def validate_and_fix_mermaid_syntax(mermaid_code: str) -> tuple:
    """Validate and fix common Mermaid syntax errors"""
    errors = []
    fixed_code = mermaid_code.strip()
    
    # Remove markdown code blocks
    if fixed_code.startswith("```mermaid"):
        fixed_code = fixed_code.replace("```mermaid", "").replace("```", "").strip()
    elif fixed_code.startswith("```"):
        fixed_code = fixed_code.replace("```", "").strip()
    
    # Fix 1: Remove invalid characters in node IDs
    lines = fixed_code.split('\n')
    fixed_lines = []
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        if not line or line.startswith('%%'):
            fixed_lines.append(line)
            continue
        
        # Fix 2: Correct arrow syntax
        line = re.sub(r'-{3,}>', '-->', line)  # Fix multiple dashes
        line = re.sub(r'\.{3,}>', '-..->', line)  # Fix dotted arrows
        
        # Fix 3: Escape special characters in labels
        def escape_label(match):
            label = match.group(1)
            label = label.replace('"', '\\"')
            return f'["{label}"]' if match.group(0).startswith('[') else f'"{label}"'
        
        line = re.sub(r'\["([^"]*?)"\]', escape_label, line)
        line = re.sub(r'"([^"]*?)"', escape_label, line)
        
        # Fix 4: Fix subgraph syntax
        if line.startswith('subgraph'):
            if not re.match(r'subgraph\s+\S+', line):
                line = line.replace('subgraph', 'subgraph default')
                errors.append(f"Fixed: Added default title to subgraph")
        
        # Fix 5: Fix class definitions
        if 'class ' in line and ':::' not in line:
            line = re.sub(r'class\s+(\w+)\s+(\w+)', r'\1:::\2', line)
        
        # Fix 6: Remove duplicate semicolons
        line = re.sub(r';+', ';', line)
        
        # Fix 7: Fix node shape syntax
        line = re.sub(r'\[\s+', '[', line)
        line = re.sub(r'\s+\]', ']', line)
        
        if line != original_line.strip():
            errors.append(f"Fixed line: {original_line.strip()[:50]}...")
        
        fixed_lines.append(line)
    
    fixed_code = '\n'.join(fixed_lines)
    
    # Fix 8: Validate diagram type
    valid_types = [
        'sequenceDiagram', 'graph', 'flowchart', 'classDiagram',
        'erDiagram', 'stateDiagram', 'journey', 'gantt', 'mindmap',
        'pie', 'gitGraph', 'C4Context'
    ]
    
    first_line = fixed_lines[0] if fixed_lines else ''
    diagram_type = first_line.split()[0] if first_line else ''
    
    if diagram_type not in valid_types:
        if 'sequence' in diagram_type.lower():
            fixed_code = 'sequenceDiagram\n' + '\n'.join(fixed_lines[1:])
            errors.append("Fixed: Corrected diagram type to 'sequenceDiagram'")
        elif 'flow' in diagram_type.lower() or 'graph' in diagram_type.lower():
            fixed_code = 'flowchart TD\n' + '\n'.join(fixed_lines[1:])
            errors.append("Fixed: Corrected diagram type to 'flowchart TD'")
        elif 'class' in diagram_type.lower():
            fixed_code = 'classDiagram\n' + '\n'.join(fixed_lines[1:])
            errors.append("Fixed: Corrected diagram type to 'classDiagram'")
    
    # Fix 9: Add proper spacing
    fixed_code = re.sub(r'\n{3,}', '\n\n', fixed_code)
    
    return fixed_code, errors

def render_mermaid(mermaid_code, height=600, unique_id=None, theme='dark'):
    """Render mermaid diagram with BULLETPROOF error handling and syntax fixes"""
    if not unique_id:
        unique_id = generate_key(mermaid_code)
    
    # Validate and fix syntax BEFORE rendering
    fixed_code, syntax_fixes = validate_and_fix_mermaid_syntax(mermaid_code)
    
    # Show syntax fixes if any
    if syntax_fixes:
        with st.expander("🔧 Auto-fixed Syntax Issues", expanded=False):
            for fix in syntax_fixes:
                st.info(fix)
    
    # Escape code for safe embedding
    safe_mermaid_code = fixed_code.replace('`', '\\`').replace('${', '\\${').replace('</script>', '<\\/script>')
    
    # Enhanced theme configuration
    if theme == 'dark':
        theme_vars = {
            'primaryColor': '#8b5cf6',
            'primaryTextColor': '#fff',
            'primaryBorderColor': '#6d28d9',
            'lineColor': '#a78bfa',
            'secondaryColor': '#4c1d95',
            'tertiaryColor': '#2e1065',
            'background': '#1a1a1a',
            'mainBkg': '#2d2d2d',
            'secondBkg': '#3d3d3d',
            'textColor': '#e8e8e8',
            'border1': '#404040',
            'border2': '#525252',
            'fontSize': '16px',
            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }
    else:
        theme_vars = {
            'primaryColor': '#7c3aed',
            'primaryTextColor': '#fff',
            'primaryBorderColor': '#6d28d9',
            'lineColor': '#8b5cf6',
            'secondaryColor': '#ede9fe',
            'tertiaryColor': '#f5f3ff',
            'background': '#ffffff',
            'mainBkg': '#f7f7f8',
            'secondBkg': '#ffffff',
            'textColor': '#2e2e2e',
            'border1': '#e5e5e5',
            'border2': '#d4d4d4',
            'fontSize': '16px',
            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }
    
    mermaid_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            
            let hasError = false;
            
            mermaid.initialize({{ 
                startOnLoad: false,
                theme: 'base',
                themeVariables: {{
                    primaryColor: '{theme_vars['primaryColor']}',
                    primaryTextColor: '{theme_vars['primaryTextColor']}',
                    primaryBorderColor: '{theme_vars['primaryBorderColor']}',
                    lineColor: '{theme_vars['lineColor']}',
                    secondaryColor: '{theme_vars['secondaryColor']}',
                    tertiaryColor: '{theme_vars['tertiaryColor']}',
                    background: '{theme_vars['background']}',
                    mainBkg: '{theme_vars['mainBkg']}',
                    secondBkg: '{theme_vars['secondBkg']}',
                    textColor: '{theme_vars['textColor']}',
                    border1: '{theme_vars['border1']}',
                    border2: '{theme_vars['border2']}',
                    fontSize: '{theme_vars['fontSize']}',
                    fontFamily: '{theme_vars['fontFamily']}'
                }},
                securityLevel: 'loose',
                logLevel: 'debug',
                suppressErrorRendering: false,
                flowchart: {{
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis',
                    padding: 20,
                    nodeSpacing: 50,
                    rankSpacing: 50
                }},
                sequence: {{
                    useMaxWidth: true,
                    diagramMarginX: 20,
                    diagramMarginY: 20,
                    actorMargin: 50,
                    width: 150,
                    height: 65,
                    boxMargin: 10,
                    messageMargin: 35,
                    mirrorActors: true,
                    wrap: true,
                    wrapPadding: 10
                }},
                class: {{
                    useMaxWidth: true,
                    padding: 20
                }},
                er: {{
                    useMaxWidth: true,
                    padding: 20,
                    layoutDirection: 'TB',
                    minEntityWidth: 100,
                    minEntityHeight: 75,
                    entityPadding: 15
                }}
            }});
            
            function showErrorMessage(errorDetails) {{
                const container = document.getElementById('diagram-container');
                if (container) {{
                    container.innerHTML = `
                        <div class="error-container">
                            <div class="error-icon">⚠️</div>
                            <div class="error-title">Diagram Rendering Error</div>
                            <div class="error-message">
                                <p><strong>Syntax Issue Detected</strong></p>
                                <div class="error-details">
                                    <p><strong>Error:</strong> ${{errorDetails || 'Unknown error'}}</p>
                                </div>
                                <div class="suggestions">
                                    <p>💡 <strong>Quick Fixes:</strong></p>
                                    <ul>
                                        <li>Ask: <em>"Regenerate this diagram with correct syntax"</em></li>
                                        <li>Try: <em>"Create a simpler version of this diagram"</em></li>
                                        <li>Alternative: <em>"Show me a flowchart instead"</em></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    `;
                }}
            }}
            
            async function renderDiagram() {{
                try {{
                    const code = `{safe_mermaid_code}`;
                    const element = document.getElementById('diagram-container');
                    
                    if (!code || code.trim().length < 10) {{
                        throw new Error('Empty or invalid diagram code');
                    }}
                    
                    console.log('Rendering diagram with code:', code);
                    
                    const renderPromise = mermaid.render('mermaid-svg-{unique_id}', code);
                    const timeoutPromise = new Promise((_, reject) => 
                        setTimeout(() => reject(new Error('Render timeout after 10s')), 10000)
                    );
                    
                    const result = await Promise.race([renderPromise, timeoutPromise]);
                    
                    element.innerHTML = result.svg;
                    console.log('✅ Diagram rendered successfully!');
                    
                    setTimeout(() => {{
                        const svg = element.querySelector('svg');
                        if (svg) {{
                            svg.style.maxWidth = '100%';
                            svg.style.height = 'auto';
                            const bbox = svg.getBBox();
                            if (bbox && bbox.width > 0 && bbox.height > 0) {{
                                svg.setAttribute('viewBox', `${{bbox.x}} ${{bbox.y}} ${{bbox.width}} ${{bbox.height}}`);
                            }}
                            svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
                        }}
                    }}, 100);
                    
                }} catch (error) {{
                    console.error('❌ Mermaid render error:', error);
                    hasError = true;
                    showErrorMessage(error.message || error.toString());
                }}
            }}
            
            window.addEventListener('error', (e) => {{
                console.error('Global error:', e);
                if (!hasError) showErrorMessage(e.message);
                return true;
            }});
            
            window.addEventListener('unhandledrejection', (e) => {{
                console.error('Unhandled rejection:', e);
                if (!hasError) showErrorMessage(e.reason);
                return true;
            }});
            
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', () => setTimeout(renderDiagram, 100));
            }} else {{
                setTimeout(renderDiagram, 100);
            }}
        </script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                background: {theme_vars['background']};
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 20px;
                font-family: {theme_vars['fontFamily']};
            }}
            #diagram-container {{
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 200px;
            }}
            .error-container {{
                background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
                border: 3px solid #ef4444;
                border-radius: 16px;
                padding: 40px;
                max-width: 650px;
                text-align: center;
                box-shadow: 0 20px 25px -5px rgba(239, 68, 68, 0.15);
            }}
            .error-icon {{ font-size: 4rem; margin-bottom: 1.5rem; }}
            .error-title {{ font-size: 1.875rem; font-weight: 800; color: #991b1b; margin-bottom: 1.5rem; }}
            .error-message {{ color: #7f1d1d; font-size: 1.1rem; line-height: 1.7; }}
            .error-details {{
                background: rgba(255, 255, 255, 0.4);
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                text-align: left;
                font-family: monospace;
                font-size: 0.9rem;
            }}
            .suggestions {{
                background: rgba(255, 255, 255, 0.6);
                border-radius: 10px;
                padding: 25px;
                margin: 20px 0;
                text-align: left;
            }}
            .suggestions ul {{ list-style: none; padding: 0; }}
            .suggestions li {{
                margin: 12px 0;
                padding-left: 25px;
                position: relative;
                line-height: 1.6;
            }}
            .suggestions li:before {{
                content: "→";
                position: absolute;
                left: 0;
                font-weight: bold;
                color: #dc2626;
            }}
            svg {{
                max-width: 100%;
                height: auto;
                filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
            }}
            .loading {{
                color: {theme_vars['textColor']};
                font-size: 1.1rem;
                animation: fadeInOut 1.5s infinite;
            }}
            @keyframes fadeInOut {{ 0%, 100% {{ opacity: 0.5; }} 50% {{ opacity: 1; }} }}
        </style>
    </head>
    <body>
        <div id="diagram-container">
            <div class="loading">⏳ Loading diagram...</div>
        </div>
    </body>
    </html>
    """
    
    try:
        components.html(mermaid_html, height=height, scrolling=True)
        return True
    except Exception as e:
        st.error(f"⚠️ Render Error: {str(e)}")
        with st.expander("🔍 View Fixed Code"):
            st.code(fixed_code, language="mermaid")
        return False