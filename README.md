# Pro-English-Writing-Coach

An advanced AI-powered writing coach designed to elevate professional English writing skills to C1 proficiency and beyond, built with a scalable Python API backend and a dynamic JavaScript frontend.

---

## 🚀 Overview

Welcome to the Pro-English-Writing-Coach project! This initiative marks a fresh start for developing a sophisticated English writing assistant. Our goal is to provide comprehensive, AI-driven feedback for non-native speakers targeting C1-level proficiency in professional contexts.

Moving beyond a simple MVP, this project adopts a modern decoupled architecture, separating the core AI logic and data processing into a robust Python backend API and focusing on a rich, interactive user experience with a dedicated JavaScript frontend. This approach ensures scalability, maintainability, and the flexibility to integrate advanced UI/UX features and future functionalities.

---

## ✨ Core Features (Initial Focus)

For our initial "blank canvas" phase, we will implement the following essential functionalities, establishing a strong foundation:

**Intelligent Text Analysis (Backend):**
* Utilizes Large Language Models (LLMs) (e.g., OpenAI's GPT models or Google's Gemini) to perform deep linguistic analysis.
* Identifies and corrects grammar errors, spelling mistakes, and awkward phrasing.
* Provides a structured output containing the corrected text and a detailed list of specific changes with brief, educational explanations.

**Intuitive User Interface (Frontend):**
* A clean, responsive web interface for users to input their English text.
* Clearly displays the AI's corrected version of the text.
* Presents the list of specific changes in an easy-to-read, actionable format for learning.
* Handles loading states and error messages gracefully.

---

## 🛠️ Technology Stack

This project will be built with a clear separation of concerns, utilizing distinct technologies for the backend and frontend:

**Backend (API Server)**
* **Python**: The core programming language.
* **FastAPI (Recommended) / Flask**: A modern, fast, and robust web framework for building the RESTful API. FastAPI is preferred for its performance, built-in data validation (Pydantic), and automatic interactive API documentation (Swagger UI).
* **Large Language Models (LLMs)**: Accessed via API (e.g., OpenAI, Google Gemini) for all linguistic processing.
* **python-dotenv**: For secure management of environment variables (like API keys) during local development.
* **uvicorn**: An ASGI server for running FastAPI applications efficiently.
* **python-multipart**: For handling form data if needed (e.g., file uploads, though not in initial MVP).

**Frontend (Client-Side Application)**
* **JavaScript**: The primary language for all client-side logic.
* **React (Recommended)**: A powerful and popular JavaScript library for building dynamic, component-based user interfaces. React's ecosystem and community support are extensive.
* **Vite**: A next-generation frontend tooling that provides an extremely fast development server and build tool for React (and other frameworks).
* **HTML5/CSS3**: For structuring and styling the web application, with a strong focus on modern UI/UX principles and responsiveness.
* **axios (or native fetch)**: For making HTTP requests from the frontend to the backend API.

---

## 📂 Project Structure (Planned)

The project will follow a clear, organized directory structure:

```Markdown
pro-english-writing-coach/
├── backend/                  # Contains all Python backend API code
│   ├── app/                  # Main FastAPI/Flask application
│   │   ├── init.py
│   │   ├── main.py           # Main API entry point (or app.py for Flask)
│   │   └── api/              # API routes/endpoints
│   │       └── v1/
│   │           └── feedback.py # Logic for the /api/v1/feedback endpoint
│   ├── core/                 # Core AI/LLM interaction logic
│   │   └── ai_assistant.py   # Encapsulates LLM calls and response parsing
│   ├── config.py             # Configuration settings (e.g., LLM provider)
│   ├── .env.example          # Example file for environment variables
│   ├── requirements.txt      # Python dependencies for the backend
│   └── README.md             # Backend-specific README (optional, but good practice)
│
├── frontend/                 # Contains all JavaScript/React frontend code
│   ├── public/               # Static assets
│   ├── src/                  # Source code for the React app
│   │   ├── App.jsx           # Main application component
│   │   ├── index.css         # Global styles
│   │   ├── main.jsx          # React entry point
│   │   └── components/       # Reusable UI components
│   │       ├── TextInput.jsx
│   │       ├── FeedbackDisplay.jsx
│   │       └── ChangesList.jsx
│   ├── package.json          # Node.js/npm dependencies for the frontend
│   ├── vite.config.js        # Vite configuration
│   └── README.md             # Frontend-specific README (optional)
│
├── .gitignore                # Specifies intentionally untracked files to ignore
├── LICENSE                   # Project license
└── README.md                 # This main project README
```
---

## ⚙️ Getting Started (Step-by-Step Setup)

To get this project running locally, you'll need to set up both the backend and the frontend.

**Prerequisites**
* Python 3.9+ (recommended for FastAPI features)
* Node.js (LTS version) and npm (comes with Node.js)

### A. Backend Setup

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/pro-english-writing-coach.git](https://github.com/your-username/pro-english-writing-coach.git)
    cd pro-english-writing-coach
    ```

2.  **Navigate to Backend Directory:**
    ```bash
    cd backend
    ```

3.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```

4.  **Activate the Virtual Environment:**
    * On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    * On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    (You'll see `(venv)` in your terminal prompt when activated.)

5.  **Install Python Dependencies:**
    Create a `requirements.txt` file in the `backend/` directory with the following content:
    ```
    fastapi
    uvicorn[standard]
    openai # Or google-generativeai
    python-dotenv
    python-multipart
    ```
    Then install:
    ```bash
    pip install -r requirements.txt
    ```

6.  **Set Up Your LLM API Key:**
    Obtain an API key from your chosen LLM provider (e.g., OpenAI, Google AI Studio).
    Create a file named `.env` in the `backend/` directory:
    ```
    # For OpenAI:
    OPENAI_API_KEY="your_openai_api_key_here"

    # OR (if using Google Gemini):
    # GEMINI_API_KEY="your_gemini_api_key_here"
    ```
    Replace `"your_api_key_here"` with your actual API key.
    **Important:** This `.env` file is excluded by `.gitignore` to prevent it from being committed to your public repository.

### B. Frontend Setup

1.  **Navigate to Frontend Directory:**
    ```bash
    cd ../frontend # Go back to project root, then into frontend
    ```

2.  **Install JavaScript Dependencies:**
    ```bash
    npm install
    ```
    (This command reads `package.json` and installs all necessary React, Vite, and other JavaScript libraries.)

3.  **Configure Frontend API URL:**
    Your frontend will make API requests to your backend. During local development, the backend will typically run on `http://localhost:5000`.
    Ensure your frontend code (e.g., in `src/App.jsx` or an API service file) points to this URL: `http://localhost:5000/api/v1/feedback`.
    For production deployment, this URL will need to be updated to your deployed backend's public URL.

---

## 🚀 How to Run the Application

You will need to run the backend and frontend servers concurrently in separate terminal windows.

### 1. Start the Backend API Server

Open your first terminal window.
Navigate to the `backend/` directory:
```bash
cd pro-english-writing-coach/backend
```
Activate your Python virtual environment.
Run the FastAPI backend server:
```bash
uvicorn app.main:app --reload --port 5000
```
(The `--reload` flag is useful for development as it restarts the server on code changes.) The backend API will be available at `http://localhost:5000`. You can also visit `http://localhost:5000/docs` to see the auto-generated API documentation (if using FastAPI).

### 2. Start the Frontend Development Server
Open your second terminal window.
Navigate to the frontend/ directory:
```bash
cd pro-english-writing-coach/frontend
```
Run the React development server:
```bash
npm run dev
```
Your default web browser should automatically open to `http://localhost:5173` (Vite's default port), displaying the application.

## 💡 Usage
* **Ensure both the backend API server and the frontend development server are running.**
* **Access the Frontend: Open your web browser and navigate to the frontend's address (e.g., `http://localhost:5173)`.**
* **Paste Your Text: Use the provided text area in the web interface to input the English text you want to analyze.**
* **Get Feedback: Click the "Get Feedback" button.**
* **Review Corrections: The frontend will send your text to the backend API. Once processed by the LLM, the corrected text and the detailed list of changes will be displayed directly in the user interface.**

## 🎯 Project Goal
This project's overarching goal is to become an indispensable tool for non-native English speakers to achieve and maintain C1 professional writing proficiency. By providing clear, actionable, and consistent feedback through a robust and user-friendly platform, we aim to facilitate continuous learning and mastery of advanced English writing skills.

## 📈 Future Enhancements (Roadmap)
As a blank canvas, the possibilities are vast! Planned future enhancements include:

* **Advanced Grammar & Style Focus: Granular control for users to target specific grammar rules (e.g., article usage, conditional sentences), conciseness, or tone.**
* **Vocabulary & Idiom Suggestions: Smart suggestions for synonyms, collocations, and idiomatic expressions to enrich writing.**
* **Personalized Progress Tracking: User accounts to track common errors over time, show improvement metrics, and offer tailored exercises.**
* **Interactive Learning Modules: Short, guided lessons or prompts based on identified weaknesses.**
* **Multi-Modal Input: Potentially allow voice input or document uploads.**
* **Real-time / Inline Feedback: Providing suggestions as the user types, similar to advanced grammar checkers.**
* **Advanced Analytics & Reporting: For users to understand their writing patterns and areas for improvement.**
* **User Authentication & Profiles: Secure user management for personalized experiences.**
* **Deployment Automation: CI/CD pipelines for automated testing and deployment.**

## 🤝 Contributing
We welcome contributions from the community! If you're interested in contributing, please review our (future) CONTRIBUTING.md guide and adhere to our (future) CODE_OF_CONDUCT.md.

## 📄 License
This project is licensed under the MIT License - see the `LICENSE` file for details.