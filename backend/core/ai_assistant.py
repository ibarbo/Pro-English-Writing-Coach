import os
import openai
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional, List, Dict

# Load environment variables from .env file at the very beginning.
load_dotenv()

class EnglishWritingAssistant:
    """
    A class to interact with Large Language Models (LLMs) to provide English writing feedback,
    daily tasks, and vocabulary. It supports different LLM providers.
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


    def get_feedback(self, text: str, level: Optional[str] = None, context: Optional[str] = None) -> dict:
        """
        Sends the user's text to the LLM and processes its response to extract
        corrected text and a list of changes, tailored by English level and optional context.
        """
        system_message = "You are an English writing assistant."
        level_focus = ""
        if level:
            if level.upper() == "B1":
                system_message = "You are an English writing assistant specializing in B1-level intermediate proficiency."
                level_focus = "Focus on fundamental grammar, spelling, basic sentence structure, and clear communication. Provide simple, direct explanations for changes."
            elif level.upper() == "B2":
                system_message = "You are an English writing assistant specializing in B2-level upper-intermediate proficiency."
                level_focus = "Focus on improving sentence fluency, vocabulary choice, common grammatical errors, and overall coherence. Explanations should be concise and helpful."
            elif level.upper() == "C1":
                system_message = "You are an English writing assistant specializing in C1-level advanced professional proficiency."
                level_focus = "Focus on refining style, advanced grammar, idiomatic expressions, conciseness, and natural flow. Provide sophisticated and insightful explanations."
            else:
                level_focus = "Maintain a general C1-level focus." # Default for invalid/unrecognized level

        # --- MODIFIED: Incorporate context into the prompt ---
        context_instruction = ""
        if context:
            context_instruction = f" The user is writing about the context of: '{context}'. Adapt your feedback tone and suggestions accordingly."

        prompt = f"""
        {system_message}
        Your task is to review the provided text for grammar, spelling, punctuation, awkward phrasing, and clarity.
        Do NOT change the meaning or intent of the original text.
        {level_focus}
        {context_instruction}
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
        Ensure all explanations in CHANGES_LIST are clear and helpful for the specified learner level and context.

        TEXT TO ANALYZE:
        {text}
        """

        try:
            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_message + (f" The context is: {context}" if context else "")}, # Using context in system message
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1000,
                )
                raw_response_content = response.choices[0].message.content.strip()
            elif self.llm_provider == "gemini":
                # For Gemini, it's often better to put the full prompt in the user part
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
                print(f"Warning: Inner parsing failed. Markers not found as expected or essential data missing. Providing raw LLM output as fallback. Raw output starts with: {raw_response_content[:100]}...")
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


    # --- MODIFIED: Added optional level and context parameter ---
    def generate_daily_task(self, level: Optional[str] = None, context: Optional[str] = None) -> str:
        """
        Generates a new, unique daily writing task using the LLM, tailored by English level and optional context.
        """
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

        example_prompts = {
            "B1": [
                "Write a short paragraph describing your favorite hobby. (approx. 50-80 words)",
                "Compose a simple email to a friend inviting them to a casual event. (approx. 60-90 words)",
                "Describe a typical day in your life, using present simple tense. (approx. 70-100 words)",
                "Explain why it's important to learn English in simple terms. (approx. 50-80 words)",
                "Summarize a short news article in your own words. (approx. 70-100 words)"
            ],
            "B2": [
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
            ],
            "C1": [
                "Draft an executive summary for a complex project proposal, highlighting key findings and recommendations.",
                "Write a critical analysis of a recent technological advancement, discussing both its potential and ethical implications.",
                "Compose a formal letter of complaint to a service provider, ensuring a professional tone and clear articulation of the issue and desired resolution.",
                "Narrate a significant turning point in your career or personal life, employing vivid descriptions and sophisticated vocabulary.",
                "Synthesize information from two contrasting viewpoints on a global issue, presenting a balanced overview and your nuanced conclusion.",
                "Formulate a persuasive argument for or against mandatory continuing education in a specific profession.",
                "Elaborate on the cultural impact of globalization, supporting your points with specific examples and insightful commentary.",
                "Design a persuasive speech advocating for increased funding for arts education in schools.",
                "Discuss the challenges and opportunities of remote work, addressing both individual and organizational perspectives.",
                "Write an opinion piece on the future of traditional media in the digital age."
            ]
        }

        import random
        selected_task_type = random.choice(task_types)

        level_key = level.upper() if level and level.upper() in example_prompts else "C1"
        selected_example = random.choice(example_prompts[level_key])

        # --- MODIFIED: Incorporate context into the prompt for daily task ---
        context_instruction = ""
        if context:
            context_instruction = f" The user specifically wants a task related to: '{context}'."

        task_prompt = f"""
        You are an expert English language instructor creating daily writing tasks for {level_key}-level students.
        Generate ONE unique, concise, and engaging writing task (1-3 sentences) focused on professional or academic English.
        The task should be of the type: "{selected_task_type}".
        It should encourage the use of advanced vocabulary, complex sentence structures, and logical reasoning suitable for a {level_key} learner.
        {context_instruction}
        Crucially, include a suggested length for the response, such as "(approximately 100-150 words)". Vary the suggested length.
        Do NOT generate a task that is exactly like the example. Make it fresh and original.

        Example of a good task for a {level_key} level: "{selected_example}"

        Your output MUST ONLY be the task itself, with no additional formatting, preamble, or numbering.
        """

        try:
            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": f"You are a helpful English writing task generator for {level_key} level." + (f" The context is: {context}" if context else "")}, # Using context in system message
                        {"role": "user", "content": task_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=250,
                )
                generated_task = response.choices[0].message.content.strip()
            elif self.llm_provider == "gemini":
                response = self.client.generate_content(
                    task_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.8,
                        max_output_tokens=250,
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

    # --- ADDED: New method for Vocabulary List generation ---
    def generate_vocabulary(self, level: Optional[str] = None, topic: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Generates a list of vocabulary words, definitions, and examples using the LLM,
        tailored by English level and optional topic.
        """
        level_key = level.upper() if level and level.upper() in ["B1", "B2", "C1"] else "B2" # Default to B2 for vocab
        topic_instruction = f" on the topic of '{topic}'" if topic else ""

        system_message = f"You are a helpful English vocabulary generator for {level_key}-level learners."
        prompt = f"""
        Generate 5-7 English vocabulary words suitable for an English learner at the {level_key} level{topic_instruction}.
        For each word, provide:
        1. The word itself.
        2. Its clear and concise definition.
        3. One example sentence demonstrating its usage.

        Format your output as a numbered list. Each item should clearly label the word, definition, and example sentence.

        Example:
        1. Word: Serendipity
           Definition: The occurrence and development of events by chance in a happy or beneficial way.
           Example: Discovering that old photograph tucked inside a book was a moment of pure serendipity.

        2. Word: [word]
           Definition: [definition]
           Example: [example sentence]
        ...
        """

        try:
            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500, # Increased tokens for multiple entries
                )
                raw_response_content = response.choices[0].message.content.strip()
            elif self.llm_provider == "gemini":
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=500, # Increased tokens for multiple entries
                    ),
                )
                raw_response_content = response.text.strip()
            else:
                raise ValueError(f"Unknown LLM provider: {self.llm_provider}")

            print("--- RAW LLM VOCABULARY RESPONSE ---")
            print(raw_response_content)
            print("-----------------------------------")

            # --- Simple Parsing for Vocabulary ---
            vocabulary_list_parsed = []
            current_vocab = {}
            lines = raw_response_content.replace('\r\n', '\n').split('\n')

            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                if line_stripped.startswith(tuple(str(i) + "." for i in range(1, 10))): # Starts with "1.", "2.", etc.
                    if current_vocab: # Save previous entry
                        vocabulary_list_parsed.append(current_vocab)
                    current_vocab = {"word": "", "definition": "", "example": ""}
                    # Extract content after "X. "
                    parts = line_stripped.split(". ", 1)
                    if len(parts) > 1 and parts[1].startswith("Word:"):
                        current_vocab["word"] = parts[1][len("Word:"):].strip()
                    elif len(parts) > 1: # If it's just "X. Some text"
                         current_vocab["word"] = parts[1].strip() # Treat as word for now

                elif line_stripped.startswith("Word:"):
                    current_vocab["word"] = line_stripped[len("Word:"):].strip()
                elif line_stripped.startswith("Definition:"):
                    current_vocab["definition"] = line_stripped[len("Definition:"):].strip()
                elif line_stripped.startswith("Example:"):
                    current_vocab["example"] = line_stripped[len("Example:"):].strip()

            if current_vocab: # Add the last entry
                vocabulary_list_parsed.append(current_vocab)

            # Basic validation
            if not vocabulary_list_parsed or not any(v.get('word') for v in vocabulary_list_parsed):
                raise RuntimeError("Failed to parse vocabulary list from LLM response.")

            return vocabulary_list_parsed

        except (openai.APIError, genai.APIError) as e:
            print(f"LLM API Error during vocabulary generation: {e}")
            raise RuntimeError(f"LLM API Error during vocabulary generation: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during vocabulary generation: {e}")
            raise RuntimeError(f"An unexpected error occurred during vocabulary generation: {e}")


# --- Self-testing block ---
if __name__ == "__main__":
    print("--- Running AI Assistant Self-Test with New Features ---")
    try:
        assistant = EnglishWritingAssistant(llm_provider="openai", model_name="gpt-3.5-turbo")
        # assistant = EnglishWritingAssistant(llm_provider="gemini", model_name="gemini-pro")

        print("\nTesting daily task generation for B1 with context 'personal journal':")
        task_b1_personal = assistant.generate_daily_task(level="B1", context="personal journal")
        print("B1 Personal Task:", task_b1_personal)

        print("\nTesting daily task generation for C1 with context 'academic research paper':")
        task_c1_academic = assistant.generate_daily_task(level="C1", context="academic research paper")
        print("C1 Academic Task:", task_c1_academic)

        print("\nTesting vocabulary generation for B2 with no topic:")
        vocab_b2_general = assistant.generate_vocabulary(level="B2")
        print("B2 General Vocabulary:", vocab_b2_general)

        print("\nTesting vocabulary generation for C1 with topic 'technology':")
        vocab_c1_tech = assistant.generate_vocabulary(level="C1", topic="technology")
        print("C1 Tech Vocabulary:", vocab_c1_tech)


        print("\nTesting feedback for B1 with context 'email to friend':")
        text_b1 = "I goes to the store everyday. I like to eat pizza and watch movies, but my freind don't like it."
        feedback_b1 = assistant.get_feedback(text_b1, level="B1", context="email to friend")
        print("B1 Feedback:", feedback_b1)

        print("\nTesting feedback for C1 with context 'business report':")
        text_c1 = "The intricate nuances of intertextual discourse often obfuscate the underlying thematic cohesion. However, in light of recent findings, a more robust paradigm must be considered for future implementation, lest the current trajectory precipitate an untenable outcome."
        feedback_c1 = assistant.get_feedback(text_c1, level="C1", context="business report")
        print("C1 Feedback:", feedback_c1)


    except ValueError as ve:
        print(f"Initialization Error: {ve}")
    except RuntimeError as re:
        print(f"Feature Generation Error: {re}")
    except Exception as e:
        print(f"An unhandled error occurred during self-test: {e}")
    print("\n--- Self-Test Complete ---")