# backend/core/ai_assistant.py

import os
# --- Choose ONE of these imports based on your LLM provider ---
import openai
# import google.generativeai as genai

class EnglishWritingAssistant:
    def __init__(self, llm_provider: str = "openai", model_name: str = None):
        """
        Initializes the EnglishWritingAssistant with the specified LLM provider.
        Loads API key from environment variables.

        Args:
            llm_provider (str): The LLM provider to use ('openai' or 'gemini').
            model_name (str, optional): Specific model name to use.
                                        Defaults to "gpt-3.5-turbo" for OpenAI,
                                        "gemini-pro" for Gemini.
        """
        self.llm_provider = llm_provider.lower()
        self.client = None
        self.model_name = model_name

        if self.llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set for OpenAI.")
            self.client = openai.OpenAI(api_key=api_key)
            if not self.model_name:
                self.model_name = "gpt-3.5-turbo" # Default for OpenAI
        # elif self.llm_provider == "gemini":
        #     api_key = os.getenv("GEMINI_API_KEY")
        #     if not api_key:
        #         raise ValueError("GEMINI_API_KEY environment variable not set for Gemini.")
        #     genai.configure(api_key=api_key)
        #     if not self.model_name:
        #         self.model_name = 'gemini-pro' # Default for Gemini
        #     self.client = genai.GenerativeModel(self.model_name)
        else:
            raise ValueError(f"Unsupported LLM provider: '{llm_provider}'. Choose 'openai' or 'gemini'.")

        print(f"AI Assistant initialized using {self.llm_provider} with model {self.model_name}")

    def get_feedback(self, text: str) -> dict:
        """
        Sends the user text to the configured LLM and returns parsed feedback.
        The parsing logic strictly expects a specific output format from the LLM.

        Args:
            text (str): The English text provided by the user for analysis.

        Returns:
            dict: A dictionary containing:
                - "corrected_text" (str): The AI's refined version of the input text.
                - "changes_list" (list[str]): A list of specific changes with explanations.
        """
        if not self.client:
            raise RuntimeError(f"LLM client not initialized for {self.llm_provider}. Check API key configuration.")

        # --- LLM Prompt (Crucial Part!) ---
        # This prompt is engineered to encourage the LLM to provide structured output
        prompt = f"""You are an English writing assistant specializing in C1-level proficiency for professional contexts.
Review the following text for any grammatical errors, spelling mistakes, and awkward phrasing that a non-native speaker might make.
Provide the corrected text and then list the specific changes you made, with a brief explanation for each change.
Focus on clarity, naturalness, and grammatical accuracy suitable for professional communication.

Format your response strictly as follows:
---START_RESPONSE---
CORRECTED_TEXT: [The corrected version of the input text goes here.]
CHANGES_LIST:
- [Change 1 with brief explanation. e.g., 'Changed "an apple" to "a apple" - corrected article usage.']
- [Change 2 with brief explanation. e.g., 'Rephrased "I want to do" to "I would like to do" - improved formality.']
---END_RESPONSE---

Original Text:
"{text}"
"""

        full_feedback_text = ""
        try:
            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are an English writing assistant that provides clear, concise, and structured feedback for professional C1 English."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7, # Adjust temperature for creativity/determinism (0.0-1.0)
                    max_tokens=1000 # Limit response length to avoid excessively long outputs
                )
                full_feedback_text = response.choices[0].message.content
            # elif self.llm_provider == "gemini":
            #     response = self.client.generate_content(prompt)
            #     full_feedback_text = response.text
            else:
                raise ValueError("LLM provider not correctly configured or supported.")

            # --- Parsing the LLM's structured output ---
            corrected_text = ""
            changes_list = []

            # Look for the start and end markers to isolate the relevant part
            start_marker = "---START_RESPONSE---"
            end_marker = "---END_RESPONSE---"

            start_index = full_feedback_text.find(start_marker)
            end_index = full_feedback_text.find(end_marker)

            if start_index != -1 and end_index != -1 and end_index > start_index:
                # Extract the content between markers
                parsed_content = full_feedback_text[start_index + len(start_marker):end_index].strip()

                corrected_text_marker = "CORRECTED_TEXT:"
                changes_list_marker = "CHANGES_LIST:"

                corrected_text_start = parsed_content.find(corrected_text_marker)
                changes_list_start = parsed_content.find(changes_list_marker)

                if corrected_text_start != -1 and changes_list_start != -1 and changes_list_start > corrected_text_start:
                    corrected_text = parsed_content[corrected_text_start + len(corrected_text_marker):changes_list_start].strip()
                    changes_raw = parsed_content[changes_list_start + len(changes_list_marker):].strip()
                    
                    # Split by newlines and filter/clean lines starting with '-'
                    changes_list = [
                        line.strip().lstrip('- ').strip()
                        for line in changes_raw.split('\n')
                        if line.strip().startswith('-') and line.strip().lstrip('- ').strip() # Ensure content after '-' exists
                    ]
                else:
                    print(f"Warning: Inner parsing failed. Markers not found as expected. Raw content:\n{parsed_content}")
                    corrected_text = "AI output format error: Could not parse corrected text or changes list. Please see raw output below."
                    changes_list = [f"Raw LLM output (parsing failed): {parsed_content}"]
            else:
                # Fallback if the ---START_RESPONSE--- / ---END_RESPONSE--- markers are not found
                print(f"Warning: LLM did not follow expected outer response format. Raw output:\n{full_feedback_text}")
                corrected_text = "AI output format error: Could not find structured response markers. Please see raw output below."
                changes_list = [f"Raw LLM output: {full_feedback_text}"]

            return {
                "corrected_text": corrected_text,
                "changes_list": changes_list
            }

        except openai.APIError as e: # <--- CHANGE 'APIErrors' to 'APIError'
            print(f"OpenAI API Error: {e}")
            # Note: e.status_code and e.response might not always be present for all APIError types.
            # A safer generic message for all APIError types might be:
            raise RuntimeError(f"OpenAI API Error: {e}")
            # If you want to try to access status_code, you can, but wrap it in a check:
            # error_detail = f"Status: {e.status_code}" if hasattr(e, 'status_code') else "No status code."
            # raise RuntimeError(f"OpenAI API Error: {e} - {error_detail}")

# Example usage (for testing ai_assistant.py directly)
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env')) # Load API keys from backend/.env

    print("--- Testing EnglishWritingAssistant ---")
    test_text_good = "I look forward to hear from you soonest regarding this matter."
    test_text_bad = "This is a example text where grammer errors might by present, and the flow is not good too. I wanna improve it and make it more professional like."

    try:
        # --- Configure your LLM provider here ---
        # For OpenAI:
        assistant = EnglishWritingAssistant(llm_provider="openai", model_name="gpt-3.5-turbo")
        # For Google Gemini (uncomment if you're using Gemini):
        # assistant = EnglishWritingAssistant(llm_provider="gemini", model_name="gemini-pro")

        print(f"\nAnalyzing Text 1: '{test_text_good}'")
        feedback_result_good = assistant.get_feedback(test_text_good)
        print("\n--- Parsed Feedback (Text 1) ---")
        print("Corrected Text:", feedback_result_good["corrected_text"])
        print("Changes List:")
        for change in feedback_result_good["changes_list"]:
            print(f"- {change}")

        print(f"\nAnalyzing Text 2: '{test_text_bad}'")
        feedback_result_bad = assistant.get_feedback(test_text_bad)
        print("\n--- Parsed Feedback (Text 2) ---")
        print("Corrected Text:", feedback_result_bad["corrected_text"])
        print("Changes List:")
        for change in feedback_result_bad["changes_list"]:
            print(f"- {change}")

    except Exception as e:
        print(f"\nInitialization or test error: {e}")