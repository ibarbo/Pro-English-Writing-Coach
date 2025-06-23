from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Ensure correct relative import
from core.ai_assistant import EnglishWritingAssistant

app = FastAPI(
    title="English Writing Coach API",
    description="API for providing English writing feedback, daily tasks, and vocabulary using LLMs.",
    version="1.0.0",
)

# CORS configuration to allow frontend to communicate with backend
origins = [
    "http://localhost:5173",  # Your frontend's address
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Assistant outside of endpoint functions to reuse the instance
# Defaulting to OpenAI's gpt-3.5-turbo, but you can change these
# Error handling for missing API keys is in the EnglishWritingAssistant constructor
try:
    ai_assistant = EnglishWritingAssistant(llm_provider="openai", model_name="gpt-3.5-turbo")
    # For Gemini: ai_assistant = EnglishWritingAssistant(llm_provider="gemini", model_name="gemini-pro")
except ValueError as e:
    print(f"Failed to initialize AI Assistant: {e}")
    # Consider more robust error handling for production (e.g., exit or disable features)
    ai_assistant = None  # Set to None if initialization fails


class FeedbackRequest(BaseModel):
    text: str
    level: Optional[str] = None
    # --- ADDED: Optional context for feedback ---
    context: Optional[str] = None


@app.get("/")
async def read_root():
    return {"message": "Welcome to the English Writing Coach API! Visit /docs for API documentation."}

@app.get("/api/v1/daily-task")
# --- MODIFIED: Add optional context parameter ---
async def daily_task(
    level: Optional[str] = Query(None, description="Target English level (e.g., B1, B2, C1)"),
    context: Optional[str] = Query(None, description="Optional writing context (e.g., 'professional email', 'essay for college')")
):
    if not ai_assistant:
        raise HTTPException(status_code=503, detail="AI Assistant not initialized. Check backend configuration.")
    try:
        # --- MODIFIED: Pass level and context to generate_daily_task ---
        task = ai_assistant.generate_daily_task(level=level, context=context)
        return {"task": task}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ADDED: New endpoint for Vocabulary List generation ---
@app.get("/api/v1/vocabulary-list")
async def vocabulary_list(
    level: Optional[str] = Query(None, description="Target English level (e.g., B1, B2, C1)"),
    # --- ADDED: Optional topic for vocabulary ---
    topic: Optional[str] = Query(None, description="Optional topic for vocabulary (e.g., 'finance', 'travel')")
):
    if not ai_assistant:
        raise HTTPException(status_code=503, detail="AI Assistant not initialized. Check backend configuration.")
    try:
        # Call the new method in your AI assistant
        vocabulary_data = ai_assistant.generate_vocabulary(level=level, topic=topic)
        return {"vocabulary": vocabulary_data}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/feedback")
async def get_feedback(request: FeedbackRequest):
    if not ai_assistant:
        raise HTTPException(status_code=503, detail="AI Assistant not initialized. Check backend configuration.")
    try:
        # --- MODIFIED: Pass level and context from request body to get_feedback ---
        feedback_data = ai_assistant.get_feedback(request.text, level=request.level, context=request.context)
        return feedback_data
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))