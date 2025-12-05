# backend/services/llm_service.py
import os
import re
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage, AIMessage

def get_llm():
    """Initialize and return LLM instance with optimized settings"""
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,  # Lower for more precise, fact-based responses
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

def validate_mermaid_syntax(mermaid_code: str) -> tuple:
    """Validate Mermaid syntax and return errors if any"""
    errors = []
    lines = mermaid_code.strip().split('\n')
    
    if not lines:
        return False, ["Empty diagram code"]
    
    first_line = lines[0].strip()
    valid_types = [
        'sequenceDiagram', 'graph', 'flowchart', 'classDiagram',
        'erDiagram', 'stateDiagram', 'journey', 'gantt', 'mindmap',
        'pie', 'gitGraph'
    ]
    
    if not any(first_line.startswith(t) for t in valid_types):
        errors.append(f"Invalid diagram type: {first_line[:50]}")
        return False, errors
    
    for i, line in enumerate(lines[1:], 1):
        line = line.strip()
        if not line or line.startswith('%%'):
            continue
        
        if line.count('[') != line.count(']'):
            errors.append(f"Line {i}: Unmatched brackets")
        if line.count('(') != line.count(')'):
            errors.append(f"Line {i}: Unmatched parentheses")
        if line.count('{') != line.count('}'):
            errors.append(f"Line {i}: Unmatched braces")
        
        invalid_arrows = ['--->', '....>', '-.-->', '====>', '<---']
        for arrow in invalid_arrows:
            if arrow in line:
                errors.append(f"Line {i}: Invalid arrow syntax '{arrow}'")
    
    return len(errors) == 0, errors

def fix_mermaid_syntax(mermaid_code: str) -> str:
    """Auto-fix common Mermaid syntax errors"""
    code = mermaid_code.strip()
    if code.startswith("```mermaid"):
        code = code.replace("```mermaid", "").replace("```", "").strip()
    elif code.startswith("```"):
        code = code.replace("```", "").strip()
    
    lines = code.split('\n')
    fixed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('%%'):
            fixed_lines.append(line)
            continue
        
        line = re.sub(r'-{3,}>', '-->', line)
        line = re.sub(r'\.{3,}>', '-..->', line)
        line = line.replace('===>', '-->')
        line = line.replace('....>', '-..->')
        line = re.sub(r'(\w+\s+\w+)(?=\[|\(|-->|-.->)', lambda m: m.group(1).replace(' ', '_'), line)
        
        if '"' in line:
            line = re.sub(r'\[([^\]]*)\]', lambda m: f'["{m.group(1)}"]' if any(c in m.group(1) for c in [':', ';', ',', '|']) else m.group(0), line)
        
        line = re.sub(r';+', ';', line)
        
        if line.startswith('subgraph'):
            parts = line.split()
            if len(parts) == 1:
                line = f"subgraph {parts[0]}_graph"
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def extract_detailed_repo_components(repo_data: dict) -> dict:
    """Extract and categorize ALL components from repository"""
    
    components = {
        'frontend_files': [],
        'backend_files': [],
        'services': [],
        'routes': [],
        'models': [],
        'components': [],
        'pages': [],
        'utils': [],
        'config_files': [],
        'database_files': [],
        'api_endpoints': [],
        'dependencies': [],
        'folders': []
    }
    
    # Extract from file structure
    file_structure = repo_data.get('file_structure', {})
    
    def traverse_structure(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}/{key}" if path else key
                
                # Categorize by file type and location
                if isinstance(value, dict):
                    components['folders'].append(current_path)
                    traverse_structure(value, current_path)
                else:
                    # Categorize files
                    if 'frontend' in current_path.lower() or 'client' in current_path.lower():
                        components['frontend_files'].append(current_path)
                    if 'backend' in current_path.lower() or 'server' in current_path.lower():
                        components['backend_files'].append(current_path)
                    if 'service' in current_path.lower():
                        components['services'].append(current_path)
                    if 'route' in current_path.lower() or 'router' in current_path.lower():
                        components['routes'].append(current_path)
                    if 'model' in current_path.lower() or 'schema' in current_path.lower():
                        components['models'].append(current_path)
                    if 'component' in current_path.lower():
                        components['components'].append(current_path)
                    if 'page' in current_path.lower() or 'view' in current_path.lower():
                        components['pages'].append(current_path)
                    if 'util' in current_path.lower() or 'helper' in current_path.lower():
                        components['utils'].append(current_path)
                    if current_path.endswith(('.json', '.yaml', '.yml', '.env', '.toml', '.ini')):
                        components['config_files'].append(current_path)
                    if 'database' in current_path.lower() or 'db' in current_path.lower() or current_path.endswith('.sql'):
                        components['database_files'].append(current_path)
    
    traverse_structure(file_structure)
    
    # Extract dependencies from package files
    file_contents = repo_data.get('file_contents', {})
    for filename, content in file_contents.items():
        if 'requirements.txt' in filename or 'package.json' in filename or 'pyproject.toml' in filename:
            # Parse dependencies
            if isinstance(content, str):
                lines = content.split('\n')
                for line in lines[:50]:  # First 50 lines
                    line = line.strip()
                    if line and not line.startswith('#'):
                        components['dependencies'].append(line.split('==')[0].split('>=')[0].strip())
    
    return components

def analyze_repo_with_chat(repo_data: dict, question: str, chat_history: list = None) -> dict:
    """Analyze repository with ULTRA DETAILED diagram generation using ONLY repo data"""
    llm = get_llm()
    
    if chat_history is None:
        chat_history = []
    
    from .github_service import format_file_structure, format_file_contents
    
    # Extract detailed components
    components = extract_detailed_repo_components(repo_data)
    
    # Build COMPREHENSIVE context with ALL repository details
    context = f"""# COMPLETE Repository Analysis - USE ONLY THIS DATA

## Repository Metadata
**Name:** {repo_data.get('name', 'Unknown')}
**Description:** {repo_data.get('description', 'No description')}
**Primary Language:** {repo_data.get('language', 'Unknown')}
**All Languages:** {', '.join(repo_data.get('languages', {}).keys())}
**Stars:** {repo_data.get('stars', 0)} | **Forks:** {repo_data.get('forks', 0)}
**Topics/Tags:** {', '.join(repo_data.get('topics', []))}

## COMPLETE File Structure (ALL FILES)
{format_file_structure(repo_data.get('file_structure', {}))}

## Analyzed Components from Repository:

### Frontend Files ({len(components['frontend_files'])} files):
{chr(10).join('- ' + f for f in components['frontend_files'][:30])}

### Backend Files ({len(components['backend_files'])} files):
{chr(10).join('- ' + f for f in components['backend_files'][:30])}

### Services ({len(components['services'])} files):
{chr(10).join('- ' + f for f in components['services'])}

### Routes/API ({len(components['routes'])} files):
{chr(10).join('- ' + f for f in components['routes'])}

### Models/Schemas ({len(components['models'])} files):
{chr(10).join('- ' + f for f in components['models'])}

### UI Components ({len(components['components'])} files):
{chr(10).join('- ' + f for f in components['components'])}

### Pages/Views ({len(components['pages'])} files):
{chr(10).join('- ' + f for f in components['pages'])}

### Utilities ({len(components['utils'])} files):
{chr(10).join('- ' + f for f in components['utils'])}

### Configuration Files ({len(components['config_files'])} files):
{chr(10).join('- ' + f for f in components['config_files'])}

### Database Files ({len(components['database_files'])} files):
{chr(10).join('- ' + f for f in components['database_files'])}

### Key Dependencies:
{chr(10).join('- ' + d for d in components['dependencies'][:20])}

### All Folders/Directories:
{chr(10).join('- ' + f for f in components['folders'])}

## COMPLETE File Contents (ACTUAL CODE)
{format_file_contents(repo_data.get('file_contents', {}))}

## README Documentation (FULL TEXT)
{repo_data.get('readme', 'No README available')}

---

## CRITICAL INSTRUCTIONS - READ CAREFULLY

You are analyzing THIS SPECIFIC REPOSITORY. You have COMPLETE ACCESS to:
- Every single file and folder
- All code contents
- All configuration files
- All dependencies
- Complete structure

**MANDATORY RULES FOR DIAGRAMS:**

1. **USE ONLY REAL DATA FROM ABOVE**
   - ❌ DO NOT invent generic names like "UserService", "ApiGateway"
   - ✅ USE ACTUAL filenames: "github_service.py", "chat_routes.py"
   - ❌ DO NOT create placeholder components
   - ✅ USE ONLY components listed above

2. **BE EXTREMELY DETAILED**
   - Include ALL major files (not just 3-4)
   - Show actual folder structure
   - Use real service names
   - Show real route endpoints
   - Include real component names

3. **ACCURATE RELATIONSHIPS**
   - Only show connections that ACTUALLY exist in code
   - Base on imports and function calls you see in file contents
   - Don't assume connections - verify from code

4. **DIAGRAM RULES (CRITICAL):**
   - NO markdown code blocks (``` ```)
   - Use [DIAGRAM_START] and [DIAGRAM_END] markers
   - Node IDs: NO SPACES (use underscores)
   - Arrows: only --> -.-> ==>
   - Use subgraphs to organize by folder

5. **DETAILED COMPONENT DIAGRAM STRUCTURE:**

For component diagrams, include:
- All major folders as subgraphs
- All service files with their actual names
- All route files with their actual names
- All component files with their actual names
- Configuration and utility files
- External dependencies

Example structure for THIS repo:
[DIAGRAM_START]
flowchart TB
    subgraph Frontend["Frontend (Streamlit)"]
        subgraph Pages["pages/"]
            chat_interface["chat_interface.py"]
            diagram_history["diagram_history.py"]
            quick_diagrams["quick_diagrams.py"]
        end
        subgraph Components["components/"]
            mermaid_renderer["mermaid_renderer.py"]
            voice_input["voice_input.py"]
            sidebar["sidebar.py"]
            theme_manager["theme_manager.py"]
        end
        subgraph Utils["utils/"]
            state_manager["state_manager.py"]
            helpers["helpers.py"]
        end
    end
    
    subgraph Backend["Backend (FastAPI)"]
        subgraph Routes["routes/"]
            chat_routes["chat_routes.py"]
            diagram_routes["diagram_routes.py"]
        end
        subgraph Services["services/"]
            llm_service["llm_service.py"]
            github_service["github_service.py"]
            prompt_templates["prompt_templates.py"]
        end
        models["models.py"]
        main["main.py"]
    end
    
    subgraph External["External APIs"]
        github_api["GitHub REST API"]
        openai_api["OpenAI GPT-4"]
        mermaid_ink["Mermaid.ink"]
    end
    
    %% Show actual connections based on code
    chat_interface --> chat_routes
    chat_interface --> mermaid_renderer
    chat_interface --> voice_input
    
    chat_routes --> llm_service
    diagram_routes --> llm_service
    
    llm_service --> github_service
    llm_service --> openai_api
    
    github_service --> github_api
    
    mermaid_renderer --> mermaid_ink
[DIAGRAM_END]

**For sequence diagrams**, show ACTUAL flow:
- Use real function names from code
- Show actual API endpoints
- Include real data flow
- Show error handling from code

**For class diagrams**, use REAL classes:
- Extract actual class names from code
- Show real methods and properties
- Include actual inheritance relationships

**Response Format:**
1. Analyze the ACTUAL repository structure above
2. Identify ALL components from the lists provided
3. Answer the question using REAL file names and components
4. If diagram requested:
   - Use [DIAGRAM_START] ... [DIAGRAM_END]
   - Include ALL relevant files (not just 3-4)
   - Use actual names from above
   - Show real relationships
   - Organize with subgraphs
   - NO markdown blocks

Remember: You have the COMPLETE repository data above. Use it ALL to create comprehensive, accurate diagrams!
"""
    
    # Build message chain
    messages = [SystemMessage(content=context)]
    
    for msg in chat_history[-10:]:
        role = msg.get('role', '')
        content = msg.get('content', '')
        
        if role == 'user':
            messages.append(HumanMessage(content=content))
        elif role == 'assistant':
            messages.append(AIMessage(content=content))
    
    messages.append(HumanMessage(content=question))
    
    # Get LLM response with retry logic
    max_retries = 2
    attempt = 0
    
    while attempt < max_retries:
        try:
            response = llm.invoke(messages)
            answer_text = response.content
            
            # Extract diagram
            answer, mermaid_code, diagram_type = extract_diagram_from_response(answer_text)
            
            # Validate if diagram present
            if mermaid_code:
                mermaid_code = fix_mermaid_syntax(mermaid_code)
                is_valid, errors = validate_mermaid_syntax(mermaid_code)
                
                if not is_valid and attempt < max_retries - 1:
                    error_msg = f"""
The diagram had syntax errors: {', '.join(errors[:3])}

REGENERATE using these rules:
1. NO markdown blocks (``` ```)
2. Use [DIAGRAM_START] and [DIAGRAM_END]
3. Node IDs with underscores (no spaces)
4. Arrows: only --> -.-> ==>
5. Use ACTUAL file names from the repository data I provided
6. Include MORE components (at least 10-15 major files)
7. Use subgraphs to organize by folder

Generate a DETAILED, comprehensive diagram with ALL major components.
"""
                    messages.append(AIMessage(content=answer_text))
                    messages.append(HumanMessage(content=error_msg))
                    attempt += 1
                    continue
            
            follow_ups = generate_follow_up_questions(answer, mermaid_code is not None, diagram_type)
            
            return {
                "answer": answer,
                "mermaid_code": mermaid_code,
                "diagram_type": diagram_type,
                "has_diagram": mermaid_code is not None,
                "follow_up_questions": follow_ups,
                "repo_name": repo_data.get('name', 'Unknown')
            }
        
        except Exception as e:
            if attempt < max_retries - 1:
                attempt += 1
                continue
            
            return {
                "answer": f"Error analyzing repository: {str(e)}",
                "mermaid_code": None,
                "diagram_type": None,
                "has_diagram": False,
                "follow_up_questions": [],
                "repo_name": repo_data.get('name', 'Unknown')
            }
    
    return {
        "answer": answer if 'answer' in locals() else "Unable to generate valid diagram",
        "mermaid_code": None,
        "diagram_type": None,
        "has_diagram": False,
        "follow_up_questions": [],
        "repo_name": repo_data.get('name', 'Unknown')
    }

def clean_mermaid_code(mermaid_code: str) -> str:
    """Clean and validate Mermaid code"""
    cleaned = fix_mermaid_syntax(mermaid_code)
    is_valid, errors = validate_mermaid_syntax(cleaned)
    if not is_valid:
        raise ValueError(f"Invalid Mermaid syntax: {', '.join(errors)}")
    return cleaned

def detect_diagram_type(mermaid_code: str) -> str:
    """Detect the type of Mermaid diagram"""
    code_lower = mermaid_code.lower().strip()
    
    if code_lower.startswith("sequencediagram"):
        return "sequence"
    elif code_lower.startswith(("flowchart", "graph")):
        return "flowchart"
    elif code_lower.startswith("classdiagram"):
        return "class"
    elif code_lower.startswith("erdiagram"):
        return "database"
    elif code_lower.startswith("statediagram"):
        return "state"
    elif code_lower.startswith("journey"):
        return "journey"
    elif code_lower.startswith("gantt"):
        return "gantt"
    elif code_lower.startswith("mindmap"):
        return "mindmap"
    else:
        return "custom"

def extract_diagram_from_response(response_text: str) -> tuple:
    """Extract diagram code from chat response"""
    mermaid_code = None
    diagram_type = None
    answer = response_text.strip()
    
    if "[DIAGRAM_START]" in answer and "[DIAGRAM_END]" in answer:
        try:
            start_idx = answer.index("[DIAGRAM_START]") + len("[DIAGRAM_START]")
            end_idx = answer.index("[DIAGRAM_END]")
            raw_code = answer[start_idx:end_idx].strip()
            
            mermaid_code = clean_mermaid_code(raw_code)
            diagram_type = detect_diagram_type(mermaid_code)
            
            answer = answer[:answer.index("[DIAGRAM_START]")].strip()
            
        except Exception as e:
            print(f"Error extracting diagram: {e}")
            mermaid_code = None
            diagram_type = None
    
    return answer, mermaid_code, diagram_type

def generate_follow_up_questions(answer: str, has_diagram: bool, diagram_type: str = None) -> list:
    """Generate contextual follow-up questions"""
    
    if has_diagram and diagram_type:
        diagram_suggestions = {
            "sequence": [
                "Show error handling in this sequence",
                "Add authentication steps",
                "What happens on timeout?"
            ],
            "flowchart": [
                "Add more implementation details",
                "Show data validation steps",
                "Include error handling paths"
            ],
            "database": [
                "Show all table relationships",
                "Add indexes and constraints",
                "Include migration strategy"
            ],
            "class": [
                "Show all methods and properties",
                "Add design patterns used",
                "Include dependency injection"
            ]
        }
        
        return diagram_suggestions.get(diagram_type, [
            "Add more detail to this diagram",
            "Show internal implementations",
            "Include error handling"
        ])
    
    answer_lower = answer.lower()
    
    if any(w in answer_lower for w in ['auth', 'login', 'security', 'token']):
        return [
            "Show complete authentication flow with all steps",
            "Include session management details",
            "Add security validation points"
        ]
    elif any(w in answer_lower for w in ['database', 'data', 'model', 'schema']):
        return [
            "Show complete database schema with all tables",
            "Include all relationships and foreign keys",
            "Add data migration and seeding"
        ]
    elif any(w in answer_lower for w in ['api', 'endpoint', 'route']):
        return [
            "Show all API endpoints with details",
            "Include request/response schemas",
            "Add middleware and validators"
        ]
    else:
        return [
            "Show complete system architecture",
            "Include all components and connections",
            "Add deployment and infrastructure"
        ]