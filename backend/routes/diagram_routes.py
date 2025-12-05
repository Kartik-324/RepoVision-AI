# backend/routes/diagram_routes.py
from fastapi import APIRouter, HTTPException
from models import DiagramRequest, DiagramResponse, CustomDiagramRequest
from services.github_service import fetch_github_repo_structure, format_file_structure, format_file_contents
from services.llm_service import get_llm, clean_mermaid_code, detect_diagram_type
from services.prompt_templates import get_diagram_prompt, get_custom_diagram_prompt

router = APIRouter()

@router.post("/generate-diagram", response_model=DiagramResponse)
async def generate_diagram(request: DiagramRequest):
    """Generate a specific type of diagram from repository analysis"""
    try:
        # Fetch repository data
        repo_data = fetch_github_repo_structure(request.repo_url, deep_fetch=True)
        
        # Get LLM
        llm = get_llm()
        
        # Build comprehensive context
        context = f"""
Repository: {repo_data['name']}
Description: {repo_data['description']}
Language: {repo_data['language']}

File Structure:
{format_file_structure(repo_data['file_structure'])}

File Contents:
{format_file_contents(repo_data['file_contents'])}

README:
{repo_data['readme'][:5000]}
"""
        
        # Get diagram-specific prompt
        prompt = get_diagram_prompt(request.diagram_type, context)
        
        # Generate diagram
        response = llm.invoke(prompt)
        mermaid_code = clean_mermaid_code(response.content)
        
        return DiagramResponse(
            mermaid_code=mermaid_code,
            diagram_type=request.diagram_type,
            repo_name=repo_data['name']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-custom-diagram", response_model=DiagramResponse)
async def generate_custom_diagram(request: CustomDiagramRequest):
    """Generate a custom diagram based on user's specific request"""
    try:
        # Fetch repository data
        repo_data = fetch_github_repo_structure(request.repo_url, deep_fetch=True)
        
        # Get LLM
        llm = get_llm()
        
        # Build context
        context = f"""
Repository: {repo_data['name']}
Description: {repo_data['description']}

File Structure:
{format_file_structure(repo_data['file_structure'])}

File Contents:
{format_file_contents(repo_data['file_contents'])}
"""
        
        # Get custom prompt
        prompt = get_custom_diagram_prompt(request.user_prompt, context)
        
        # Generate diagram
        response = llm.invoke(prompt)
        mermaid_code = clean_mermaid_code(response.content)
        diagram_type = detect_diagram_type(mermaid_code)
        
        return DiagramResponse(
            mermaid_code=mermaid_code,
            diagram_type=diagram_type,
            repo_name=repo_data['name']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))