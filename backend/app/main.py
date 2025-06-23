import os
import logging
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import the EnglishWritingAssistant from your core logic module
from core.ai_assistant import EnglishWritingAssistant

# --- Configuration and Initialization ---

# Load environment variables from .env file.
# This must be called before accessing any os.getenv() calls for API keys.
load_dotenv()

# Configure logging for better error visibility in the console/logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI application
# Add descriptive title, description, and version for auto-generated documentation (Swagger UI)
app = FastAPI(
    title="Pro-English-Writing-Coach API",
    description="Backend API for an AI-powered English writing assistant, providing C1-level feedback.",
    version="1.0.0",
)

# --- CORS Middleware Configuration ---
# CORS (Cross-Origin Resource Sharing) is a security feature in web browsers.
# It prevents a web page from making requests to a different domain than the one the page originated from.
# Since our frontend (e.g., localhost:5173) will run on a different port than our backend (localhost:5000),
# we need to explicitly allow requests from the frontend's origin.
origins = [
    "http://localhost",        # Base URL
    "http://localhost:5173",   # Default Vite development server port
    "http://localhost:3000",   # Common React development server port (e.g., Create React App)
    "http://127.0.0.1:5173",   # Alternative localhost IP
    "http://127.0.0.1:3000",   # Alternative localhost IP
    # Add your deployed frontend URL here when you deploy to production, e.g.:
    # "https://your-deployed-frontend.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # List of allowed origins
    allow_credentials=True,         # Allow cookies to be included in cross-origin requests
    allow_methods=["*"],            # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],            # Allow all headers in the request
)

# Global variable to hold the AI assistant instance.
# It will be initialized once when the application starts.
ai_assistant_instance: EnglishWritingAssistant = None

# --- Application Lifecycle Events ---

@app.on_event("startup")
async def startup_event():
    """
    This function runs once when the FastAPI application starts up.
    It's used to initialize resources that should only be created once,
    like our LLM client.
    """
    global ai_assistant_instance # Declare that we are modifying the global variable

    try:
        # Initialize the AI assistant.
        # You can specify "openai" or "gemini" and the desired model name here.
        # Ensure the corresponding API key is set in your .env file.
        ai_assistant_instance = EnglishWritingAssistant(
            llm_provider=os.getenv("LLM_PROVIDER", "openai"), # Default to openai if not specified in .env
            model_name=os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo") # Default model
        )
        logger.info("AI Assistant initialized successfully at API startup.")
    except ValueError as e:
        # Catch errors specifically from the AI Assistant's initialization (e.g., missing API key)
        logger.error(f"Failed to initialize AI Assistant: {e}. API endpoints may not function.")
        # In a real production app, you might raise an exception here to prevent startup,
        # but for dev, we allow it to start and handle it in endpoints.
        ai_assistant_instance = None # Ensure it's None if initialization failed
    except Exception as e:
        logger.critical(f"An unexpected error occurred during AI Assistant startup: {e}")
        ai_assistant_instance = None


@app.on_event("shutdown")
async def shutdown_event():
    """
    This function runs once when the FastAPI application is shutting down.
    Use it to clean up resources, like closing database connections or
    releasing external client connections, if necessary.
    """
    logger.info("FastAPI application shutting down.")
    # No specific cleanup needed for OpenAI/Gemini clients for now,
    # but this is where you'd put it if there were.

# --- Pydantic Models for Request/Response Validation ---

class FeedbackRequest(BaseModel):
    """
    Defines the expected structure of the JSON request body for the /feedback endpoint.
    FastAPI uses this to automatically validate incoming data.
    """
    text: str # Expects a single field 'text' which must be a string.

# --- API Endpoints ---

@app.get("/")
async def root():
    """
    A simple root endpoint to confirm the API is running.
    Access at http://localhost:5000/
    """
    return {"message": "Pro-English-Writing-Coach API is running!"}

@app.post("/api/v1/feedback")
async def get_writing_feedback(request_body: FeedbackRequest):
    """
    Endpoint to receive user text and return AI-powered writing feedback.
    Access at http://localhost:5000/api/v1/feedback
    Expects a POST request with JSON body: {"text": "Your text here."}
    """
    # Check if the AI assistant was successfully initialized at startup
    if ai_assistant_instance is None:
        logger.error("AI Assistant not initialized. Cannot process feedback request.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, # 503 Service Unavailable
            detail="AI Assistant is not ready. Please check server logs for initialization errors."
        )

    user_text = request_body.text.strip()

    # Basic input validation: ensure the text is not empty
    if not user_text:
        logger.warning("Received empty text for feedback request.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # 400 Bad Request
            detail="Text cannot be empty. Please provide content for analysis."
        )

    try:
        # Call the core AI assistant logic to get feedback
        feedback_result = ai_assistant_instance.get_feedback(user_text)
        logger.info("Successfully generated feedback.")
        return feedback_result
    except RuntimeError as e:
        # Catch RuntimeError raised from ai_assistant.py for LLM or parsing errors
        logger.error(f"Error processing feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, # 500 Internal Server Error
            detail=f"An error occurred while generating feedback: {e}"
        )
    except Exception as e:
        # Catch any other unexpected errors that might occur
        logger.critical(f"An unhandled exception occurred in feedback endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred. Please try again later."
        )

# --- Daily Task Endpoint (MODIFIED to use LLM Generation) ---
@app.get("/api/v1/daily-task")
async def get_daily_writing_task():
    """
    Provides a daily writing task or prompt, generated by the LLM.
    Access at http://localhost:5000/api/v1/daily-task
    """
    # Ensure the AI assistant was successfully initialized at startup
    if ai_assistant_instance is None:
        logger.error("AI Assistant not initialized. Cannot generate daily task.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Assistant is not ready to generate tasks. Please check server logs."
        )

    try:
        # Call the new method in the AI assistant to generate the task
        selected_task = ai_assistant_instance.generate_daily_task()
        logger.info("Daily writing task generated by LLM.")
        return {"task": selected_task}
    except RuntimeError as e:
        logger.error(f"Error generating daily task with LLM: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating a daily task: {e}"
        )
    except Exception as e:
        logger.critical(f"An unhandled exception occurred in daily task endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred while fetching daily task. Please try again later."
        )