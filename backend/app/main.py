# backend/app/main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Import your AI logic from the core module
from core.ai_assistant import EnglishWritingAssistant

# --- Load Environment Variables ---
# This ensures .env is loaded when the FastAPI app starts
# The dotenv_path needs to point to the .env file in the 'backend' directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Pro-English-Writing-Coach API",
    description="API for AI-powered English writing feedback.",
    version="1.0.0"
)

# --- CORS Configuration ---
# IMPORTANT: Adjust origins for production!
# For local development, allow frontend on localhost:5173 (Vite default) or localhost:3000 (CRA default)
# and any other ports your frontend might run on.
# You can also use a regex: r"http://localhost:\d+"
origins = [
    "http://localhost",
    "http://localhost:3000", # Common React default
    "http://localhost:5173", # Common Vite/React default
    # Add your deployed frontend URL here when you deploy!
    # "https://your-deployed-frontend.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- Initialize AI Assistant ---
# This is done once when the FastAPI app starts
ai_assistant_instance: EnglishWritingAssistant = None

@app.on_event("startup")
async def startup_event():
    """
    Initializes the EnglishWritingAssistant when the FastAPI application starts.
    """
    global ai_assistant_instance
    try:
        # You can make this configurable via environment variables in the future
        # For now, explicitly set 'openai'. Uncomment and change for Gemini.
        ai_assistant_instance = EnglishWritingAssistant(llm_provider="openai", model_name="gpt-3.5-turbo")
        print("AI Assistant initialized successfully at API startup.")
    except Exception as e:
        print(f"Failed to initialize AI Assistant: {e}")
        # In a production app, you might want to log this critical error
        # and perhaps prevent the app from starting fully or make it unhealthy.
        ai_assistant_instance = None # Ensure it's None if initialization failed

# --- Request Body Model ---
class FeedbackRequest(BaseModel):
    text: str # The input text from the user

# --- API Endpoint ---
@app.post("/api/v1/feedback")
async def get_writing_feedback(request_body: FeedbackRequest):
    """
    Receives user text and returns AI-powered writing feedback.
    """
    if ai_assistant_instance is None:
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail="AI Assistant is not initialized. Please check server logs for errors."
        )

    user_text = request_body.text

    if not user_text or not isinstance(user_text, str) or len(user_text.strip()) == 0:
        raise HTTPException(
            status_code=400, # Bad Request
            detail="Input 'text' is required and cannot be empty."
        )

    try:
        # Call the get_feedback method from your ai_assistant
        feedback_result = ai_assistant_instance.get_feedback(user_text)
        return feedback_result # FastAPI automatically converts dict to JSON
    except RuntimeError as e:
        # Catch specific RuntimeErrors from ai_assistant (e.g., LLM API errors)
        print(f"Error from AI Assistant: {e}")
        raise HTTPException(
            status_code=500, # Internal Server Error
            detail=f"An error occurred during AI processing: {e}"
        )
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected server error occurred: {e}")
        raise HTTPException(
            status_code=500, # Internal Server Error
            detail=f"An unexpected internal server error occurred."
        )

# --- Root Endpoint (Optional, for health check or welcome message) ---
@app.get("/")
async def root():
    return {"message": "Pro-English-Writing-Coach API is running!"}