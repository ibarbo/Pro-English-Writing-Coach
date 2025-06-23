import os
import openai
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file at the very beginning.
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
        self.llm_provider = llm_provider.lower()
        self.model_name = model_name

        if self.llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables.")
            self.client = openai.OpenAI(api_key=api_key)
        elif self.llm_provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables.")
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model_name)
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}. Supported are 'openai' or 'gemini'.")

        print(f"AI Assistant initialized successfully using {self.llm_provider} with model {self.model_name}.")


    def get_feedback(self, text: str) -> dict:
        """
        Sends the user's text to the LLM and processes its response to extract
        corrected text and a list of changes.
        """
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
            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful English writing assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1000,
                )
                raw_response_content = response.choices[0].message.content.strip()
            elif self.llm_provider == "gemini":
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        max_output_tokens=1000,
                    )
                )
                raw_response_content = response.text.strip()
            else:
                raise ValueError(f"Unknown LLM provider: {self.llm_provider}")

            print("--- RAW LLM RESPONSE ---")
            print(raw_response_content)
            print("------------------------")

            corrected_text = ""
            changes_list = []
            parsing_successful = False

            lines = raw_response_content.replace('\r\n', '\n').split('\n')

            state = "INITIAL"

            for line in lines:
                stripped_line = line.strip()

                if stripped_line == "---START_RESPONSE---":
                    state = "IN_RESPONSE_BLOCK"
                    continue

                if stripped_line == "---END_RESPONSE---":
                    if state == "IN_CHANGES_LIST" or state == "IN_CORRECTED_TEXT" or corrected_text:
                        parsing_successful = True
                    break

                if state == "IN_RESPONSE_BLOCK":
                    if stripped_line.startswith("CORRECTED_TEXT:"):
                        corrected_text = stripped_line[len("CORRECTED_TEXT:"):].strip()
                        state = "IN_CORRECTED_TEXT"
                    elif stripped_line.startswith("CHANGES_LIST:"):
                        state = "IN_CHANGES_LIST"

                elif state == "IN_CORRECTED_TEXT":
                    if stripped_line.startswith("CHANGES_LIST:"):
                        state = "IN_CHANGES_LIST"
                    else:
                        corrected_text += (" " if corrected_text else "") + stripped_line

                elif state == "IN_CHANGES_LIST":
                    if stripped_line.startswith('- ') or stripped_line.startswith('* '):
                        changes_list.append(stripped_line[2:].strip())
                    elif stripped_line and stripped_line[0].isdigit() and stripped_line.find('. ') == 1:
                         changes_list.append(stripped_line[stripped_line.find('. ') + 2:].strip())
                    elif stripped_line:
                        changes_list.append(stripped_line)


            if not parsing_successful or not corrected_text:
                print("Warning: Inner parsing failed. Markers not found as expected or essential data missing. Providing raw LLM output as fallback.")
                corrected_text = raw_response_content
                changes_list = ["Error: Could not parse structured feedback. Raw LLM output is provided.", f"Raw Output (truncated): {raw_response_content[:150]}..."]

            if "No changes needed." in changes_list and len(changes_list) > 1:
                changes_list = [c for c in changes_list if c != "No changes needed."]
                if not changes_list:
                    changes_list = ["No changes needed."]

            return {
                "corrected_text": corrected_text.strip(),
                "changes_list": changes_list
            }

        except (openai.APIError, genai.APIError) as e:
            print(f"LLM API Error: {e}")
            raise RuntimeError(f"LLM API Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during feedback generation: {e}")
            raise RuntimeError(f"An unexpected error occurred during feedback generation: {e}")


    def generate_daily_task(self) -> str:
        """
        Generates a new, unique daily writing task using the LLM.
        The task focuses on C1-level English writing practice and includes a suggested word count.
        """
        # --- MODIFIED: More diverse task types and example prompts ---
        task_types = [
            "Write a persuasive essay",
            "Give your opinion on a current event or social issue",
            "Compose a professional email",
            "Describe a personal or professional experience",
            "Summarize a given text or concept",
            "Write a short reflective journal entry",
            "Create a brief report or memo",
            "Draft a proposal or a recommendation",
            "Develop a narrative scene or character description",
            "Explain a complex idea in simple terms"
        ]

        example_prompts = [
            "Write a concise summary of a complex topic (e.g., climate change impacts or AI ethics) suitable for a professional audience.",
            "Compose an argumentative paragraph supporting or opposing a current social issue, ensuring logical flow and strong vocabulary.",
            "Draft a short, compelling email to a client or colleague, requesting information or proposing a solution to a problem.",
            "Describe a challenging professional situation you've encountered and how you effectively resolved it, focusing on clear narration and appropriate business vocabulary.",
            "Write a reflective piece on the importance of adaptability in today's rapidly changing work environment.",
            "Explain the concept of 'supply and demand' to someone with no economic background.",
            "Imagine you are pitching a new product to investors. Write a brief overview of its key features and benefits.",
            "Describe your favorite place and explain why it holds special meaning for you.",
            "Write a memo to your team outlining the new remote work policy.",
            "Express your opinion on the impact of social media on modern communication."
        ]

        import random
        selected_task_type = random.choice(task_types)
        selected_example = random.choice(example_prompts)

        # Craft the prompt for the LLM to generate a new task
        task_prompt = f"""
        You are an expert English language instructor creating daily writing tasks for C1-level students.
        Generate ONE unique, concise, and engaging writing task (1-3 sentences) focused on professional or academic English.
        The task should be of the type: "{selected_task_type}".
        It should encourage the use of advanced vocabulary, complex sentence structures, and logical reasoning.
        Crucially, include a suggested length for the response, such as "(approximately 100-150 words)". Vary the suggested length.
        Do NOT generate a task that is exactly like the example. Make it fresh and original.

        Example of a good task: "{selected_example}"

        Your output MUST ONLY be the task itself, with no additional formatting, preamble, or numbering.
        """

        try:
            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful English writing task generator."},
                        {"role": "user", "content": task_prompt}
                    ],
                    temperature=0.8, # Increased temperature for more variety
                    max_tokens=250,  # Increased max_tokens to allow for more diverse and slightly longer tasks
                )
                generated_task = response.choices[0].message.content.strip()
            elif self.llm_provider == "gemini":
                response = self.client.generate_content(
                    task_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.8, # Increased temperature for more variety
                        max_output_tokens=250, # Increased max_output_tokens
                    )
                )
                generated_task = response.text.strip()
            else:
                raise ValueError(f"Unknown LLM provider: {self.llm_provider}")

            if generated_task.startswith('"') and generated_task.endswith('"'):
                generated_task = generated_task[1:-1].strip()
            if generated_task.startswith("'") and generated_task.endswith("'"):
                generated_task = generated_task[1:-1].strip()

            print("--- GENERATED DAILY TASK ---")
            print(generated_task)
            print("----------------------------")

            return generated_task

        except (openai.APIError, genai.APIError) as e:
            print(f"LLM API Error during task generation: {e}")
            raise RuntimeError(f"LLM API Error during task generation: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during daily task generation: {e}")
            raise RuntimeError(f"An unexpected error occurred during daily task generation: {e}")


# --- Self-testing block ---
if __name__ == "__main__":
    print("--- Running AI Assistant Self-Test ---")
    try:
        assistant = EnglishWritingAssistant(llm_provider="openai", model_name="gpt-3.5-turbo")
        # assistant = EnglishWritingAssistant(llm_provider="gemini", model_name="gemini-pro")

        print("\nTesting daily task generation (expect more variety):")
        for _ in range(3): # Generate a few to see variety
            daily_task = assistant.generate_daily_task()
            print("Generated Daily Task:", daily_task)

    except ValueError as ve:
        print(f"Initialization Error: {ve}")
    except RuntimeError as re:
        print(f"Feedback Generation Error: {re}")
    except Exception as e:
        print(f"An unhandled error occurred during self-test: {e}")
    print("\n--- Self-Test Complete ---")