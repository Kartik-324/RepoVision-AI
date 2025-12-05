# backend/routes/chat_routes.py
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from models import ChatRequest, ChatResponse
from services.github_service import fetch_github_repo_structure
from services.llm_service import analyze_repo_with_chat

router = APIRouter()

# Simple in-memory cache
repo_cache = {}

@router.post("/chat", response_model=ChatResponse)
async def chat_with_repo(
    request: ChatRequest,
    x_github_token: Optional[str] = Header(None)  # NEW: Accept GitHub token from headers
):
    """Chat about repository with AI - supports private repos"""
    try:
        print(f"\n{'='*60}")
        print(f"💬 Chat request for: {request.repo_url}")
        print(f"❓ Question: {request.question}")
        
        # Check if repo is in cache
        cache_key = request.repo_url
        if x_github_token:
            cache_key = f"{request.repo_url}::{x_github_token[:10]}"  # Include token prefix in cache key
            print(f"🔒 Private repository access enabled")
        
        if cache_key in repo_cache:
            print("⚡ Using cached data")
            repo_data = repo_cache[cache_key]
        else:
            print("🔄 Fetching fresh data")
            # NEW: Pass GitHub token to fetch function
            repo_data = fetch_github_repo_structure(
                request.repo_url, 
                deep_fetch=True,
                github_token=x_github_token
            )
            
            # Cache for 5 minutes (in production, use Redis with TTL)
            repo_cache[cache_key] = repo_data
            print(f"✅ Cached {len(repo_data.get('file_contents', {}))} files")
        
        # Analyze with chat
        print(f"🤖 Sending to LLM: {request.question[:100]}...")
        
        # Convert chat_history to dicts if needed
        chat_history_dicts = []
        for msg in (request.chat_history or []):
            if hasattr(msg, 'dict'):
                chat_history_dicts.append(msg.dict())
            elif isinstance(msg, dict):
                chat_history_dicts.append(msg)
            else:
                # Handle Pydantic model
                chat_history_dicts.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        result = analyze_repo_with_chat(
            repo_data=repo_data,
            question=request.question,
            chat_history=chat_history_dicts
        )
        
        return ChatResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))