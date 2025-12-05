# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from dotenv import load_dotenv
import base64
import requests

from routes import diagram_routes, chat_routes

load_dotenv()

app = FastAPI(title="GitHub Mermaid Diagram Generator")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(diagram_routes.router)
app.include_router(chat_routes.router)

# NEW: Export diagram as image endpoint
@app.post("/export-diagram")
async def export_diagram(request: dict):
    """Convert Mermaid diagram to PNG or SVG image"""
    try:
        mermaid_code = request.get("mermaid_code", "")
        format_type = request.get("format", "png").lower()  # png or svg
        
        if not mermaid_code:
            raise HTTPException(status_code=400, detail="No mermaid code provided")
        
        # Use mermaid.ink API to convert diagram to image
        # Encode mermaid code to base64
        encoded = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
        
        # Choose endpoint based on format
        if format_type == "svg":
            url = f"https://mermaid.ink/svg/{encoded}"
            media_type = "image/svg+xml"
        else:  # default to png
            url = f"https://mermaid.ink/img/{encoded}"
            media_type = "image/png"
        
        # Fetch the image
        print(f"📥 Fetching {format_type.upper()} from mermaid.ink...")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Successfully generated {format_type.upper()} image")
            return Response(
                content=response.content,
                media_type=media_type,
                headers={
                    "Content-Disposition": f"attachment; filename=diagram.{format_type}"
                }
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate image: {response.status_code}"
            )
            
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Image generation timed out")
    except Exception as e:
        print(f"❌ Error exporting diagram: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Enhanced GitHub Mermaid Diagram Generator",
        "version": "2.0",
        "endpoints": {
            "/generate-diagram": "POST - Generate detailed diagram",
            "/generate-custom-diagram": "POST - Custom detailed diagram",
            "/chat": "POST - Chat with detailed diagram generation",
            "/export-diagram": "POST - Export diagram as PNG/SVG"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)