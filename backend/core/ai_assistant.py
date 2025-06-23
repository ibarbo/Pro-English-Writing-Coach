import os
import openai # OpenAI Python client library
import google.generativeai as genai # Google Generative AI Python client library
from dotenv import load_dotenv # Library to load environment variables from .env file

# Load environment variables from .env file at the very beginning.
# This ensures that API keys are available when the application starts.
load_dotenv()

class EnglishWritingAssistant:
    """
    A class to interact with Large Language Models (LLMs) to provide English writing feedback.
    It supports different LLM providers like OpenAI (GPT models) and Google (Gemini models).
    """

    def __init__(self, llm_provider: str = "openai", model_name: str = "gpt-3.5-turbo"):
        """
        Initializes the EnglishWritingAssistant with a specific LLM provider and model.

        Args:
            llm_provider (str): The name of the LLM provider (e.g., "openai", "gemini").
            model_name (str): The specific model name to use (e.g., "gpt-3.5-turbo", "gemini-pro").

        Raises:
            ValueError: If the API key is missing or an unsupported LLM provider is specified.
        """
        self.llm_provider = llm_provider.lower() # Convert to lowercase for consistent comparison
        self.model_name = model_name

        # --- Initialize LLM Client based on provider ---
        if self.llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                # Raise an error if API key is not found, preventing the app from running without it
                raise ValueError("OPENAI_API_KEY not found in environment variables.")
            # Initialize OpenAI client
            self.client = openai.OpenAI(api_key=api_key)
        elif self.llm_provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                # Raise an error if API key is not found
                raise ValueError("GEMINI_API_KEY not found in environment variables.")
            # Configure Google Generative AI client
            genai.configure(api_key=api_key)
            # Get the Generative Model instance
            self.client = genai.GenerativeModel(model_name)
        else:
            # Handle unsupported LLM providers gracefully
            raise ValueError(f"Unsupported LLM provider: {llm_provider}. Supported are 'openai' or 'gemini'.")

        print(f"AI Assistant initialized successfully using {self.llm_provider} with model {self.model_name}.")


    def get_feedback(self, text: str) -> dict:
        """
        Sends the user's text to the LLM and processes its response to extract
        corrected text and a list of changes.

        Args:
            text (str): The input English text provided by the user.

        Returns:
            dict: A dictionary containing 'corrected_text' (str) and 'changes_list' (list of str).

        Raises:
            RuntimeError: If there's an error during the LLM API call or during response parsing.
        """
        # --- Prompt Engineering ---
        # This is the core instruction given to the LLM. It defines the AI's role,
        # the task it needs to perform, and crucially, the *desired output format*.
        # A structured output format helps in reliably parsing the LLM's response.
        prompt = f"""
        You are an advanced English writing assistant specializing in C1-level professional proficiency.
        Your task is to review the provided text for grammar, spelling, punctuation, awkward phrasing, and clarity.
        Do NOT change the meaning or intent of the original text.
        Your output MUST follow this exact structure:

        ---START_RESPONSE---
        CORRECTED_TEXT: [Your corrected version of the input text here]
        CHANGES_LIST:
        - [Description of Change 1. Be concise and educational. E.g., "Changed 'was' to 'were' - subject-verb agreement."]
        - [Description of Change 2. E.g., "Removed 'very' - improved conciseness."]
        - [Description of Change 3.]
        ...
        ---END_RESPONSE---

        If no corrections or changes are needed, state that clearly in the CHANGES_LIST as "- No changes needed."
        Ensure all explanations in CHANGES_LIST are clear and helpful for a C1 learner.

        TEXT TO ANALYZE:
        {text}
        """

        try:
            # --- LLM API Call ---
            if self.llm_provider == "openai":
                # OpenAI specific API call parameters
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful English writing assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2, # Lower temperature for more deterministic and less creative output (good for correction)
                    max_tokens=1000, # Limit the length of the LLM's response
                )
                raw_response_content = response.choices[0].message.content.strip()
            elif self.llm_provider == "gemini":
                # Google Gemini specific API call parameters
                # For Gemini, system instructions are often part of the first user message or set in model config.
                # Here, the prompt is self-contained.
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        max_output_tokens=1000,
                    )
                )
                raw_response_content = response.text.strip()
            else:
                # Should not be reached if __init__ handles unsupported providers
                raise ValueError(f"Unknown LLM provider: {self.llm_provider}")

            # Print raw response for debugging purposes (can be removed in production)
            print("--- RAW LLM RESPONSE ---")
            print(raw_response_content)
            print("------------------------")

            # --- Response Parsing Logic ---
            # This logic is designed to be robust against slight variations in LLM output,
            # by looking for specific markers.

            corrected_text = ""
            changes_list = []

            # 1. Find the main response block using start/end markers
            start_marker = "---START_RESPONSE---"
            end_marker = "---END_RESPONSE---"

            start_index = raw_response_content.find(start_marker)
            end_index = raw_response_content.find(end_marker)

            if start_index == -1 or end_index == -1:
                # If markers are not found, the LLM did not follow the format
                raise RuntimeError("LLM response format markers not found. Cannot parse.")

            # Extract the content between the markers
            response_block = raw_response_content[start_index + len(start_marker):end_index].strip()

            # 2. Parse CORRECTED_TEXT and CHANGES_LIST within the block
            corrected_text_marker = "CORRECTED_TEXT:"
            changes_list_marker = "CHANGES_LIST:"

            corrected_text_start = response_block.find(corrected_text_marker)
            changes_list_start = response_block.find(changes_list_marker)

            if corrected_text_start == -1 or changes_list_start == -1:
                # If internal markers are missing
                raise RuntimeError("LLM response missing 'CORRECTED_TEXT:' or 'CHANGES_LIST:' markers.")

            # Extract corrected text content
            corrected_text = response_block[corrected_text_start + len(corrected_text_marker):changes_list_start].strip()

            # Extract changes list content
            changes_raw = response_block[changes_list_start + len(changes_list_marker):].strip()

            # Split changes into a list, cleaning up bullet points and empty lines
            for line in changes_raw.split('\n'):
                stripped_line = line.strip()
                if stripped_line and stripped_line != "- No changes needed.": # Handle "no changes" specifically
                    # Remove common bullet point prefixes like '-', '*', '1.' etc.
                    if stripped_line.startswith('- '):
                        changes_list.append(stripped_line[2:].strip())
                    elif stripped_line.startswith('* '):
                        changes_list.append(stripped_line[2:].strip())
                    elif stripped_line[0].isdigit() and stripped_line[1:2] == '. ': # Basic number. format
                         changes_list.append(stripped_line[stripped_line.find('. ') + 2:].strip())
                    else:
                        changes_list.append(stripped_line) # Add as is if no standard bullet detected

            # Special case: If LLM explicitly said "No changes needed." but list is empty after parsing
            if not changes_list and "- No changes needed." in changes_raw:
                changes_list.append("No changes needed.")


            return {
                "corrected_text": corrected_text,
                "changes_list": changes_list
            }

        # --- Error Handling for LLM API Calls ---
        except (openai.APIError, genai.APIError) as e: # Catch specific API errors from providers
            print(f"LLM API Error: {e}")
            # Re-raise as a generic RuntimeError to be caught by the FastAPI endpoint
            raise RuntimeError(f"LLM API Error: {e}")
        except Exception as e:
            # Catch any other unexpected errors during the process (e.g., parsing errors)
            print(f"An unexpected error occurred during feedback generation: {e}")
            raise RuntimeError(f"An unexpected error occurred during feedback generation: {e}")


# --- Self-testing block