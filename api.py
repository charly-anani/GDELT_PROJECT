from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import traceback
import os
import base64
from assistant.core.nl2sql import process_user_question
from assistant.core.explainer import get_data_insights

# Load GCP credentials from environment variable (Render compatibility)
if 'GOOGLE_CREDENTIALS_B64' in os.environ and not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
    try:
        creds = base64.b64decode(os.environ['GOOGLE_CREDENTIALS_B64'])
        creds_path = '/tmp/credentials.json'
        with open(creds_path, 'wb') as f:
            f.write(creds)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        print("Loaded GCP credentials from GOOGLE_CREDENTIALS_B64")
    except Exception as e:
        print("Error loading GOOGLE_CREDENTIALS_B64:", e)

app = FastAPI(title="GDELT Bénin Assistant API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def serve_root():
    """Serve the main HTML interface v2"""
    html_path = Path(__file__).parent / "assistant" / "ui" / "gdelt-assistant_v2.html"
    return FileResponse(html_path)

@app.post("/api/question")
def ask(req: QuestionRequest):
    """Process a natural language question and return structured results"""
    try:
        response = process_user_question(req.question)
        
        # Ajouter un insight basé sur les résultats réels
        if response.get("status") == "success" and response.get("data"):
            try:
                insight = get_data_insights(
                    req.question,
                    response.get('data', []),
                    response.get('sql', '')
                )
                response["insight"] = insight
            except Exception as e:
                print(f"Error generating insight: {str(e)}")
                # Continue sans insight plutôt que de fail
        
        return response
    except Exception as e:
        print(f"Error processing question: {str(e)}")
        traceback.print_exc()
        return {
            "status": "error",
            "user_message": "Une erreur est survenue lors du traitement de votre question.",
            "message": str(e),
            "details": str(e),
            "data": None,
        }

@app.get("/api/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "version": "2.0"}