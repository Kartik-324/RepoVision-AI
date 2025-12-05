# backend/models.py
from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class DiagramRequest(BaseModel):
    repo_url: str
    diagram_type: Literal["sequence", "component", "database", "flowchart", "class", "state", "journey", "gantt", "mindmap"]

class CustomDiagramRequest(BaseModel):
    repo_url: str
    user_prompt: str
    diagram_type: Optional[str] = None

class DiagramResponse(BaseModel):
    mermaid_code: str
    diagram_type: str
    repo_name: str

class ChatMessage(BaseModel):
    role: str
    content: str
    
    class Config:
        # Allow the model to work with dict conversion
        from_attributes = True

class ChatRequest(BaseModel):
    repo_url: str
    question: str
    chat_history: Optional[List[ChatMessage]] = []
    
    class Config:
        # Allow dict conversion
        from_attributes = True

class ChatResponse(BaseModel):
    answer: str
    repo_name: str
    has_diagram: bool = False
    mermaid_code: Optional[str] = None
    diagram_type: Optional[str] = None
    follow_up_questions: Optional[List[str]] = []