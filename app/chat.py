import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key():
    # Try environment variable first
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    # Try Streamlit secrets
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except:
        pass
    return None

# Initialize Gemini
api_key = get_api_key()
if api_key:
    genai.configure(api_key=api_key)

MODEL_NAME = "gemini-2.5-flash"

# DEVELOPER INSTRUCTION
# This is the prompt that guides the model's behavior.
DEVELOPER_INSTRUCTION = """
You are a helpful assistant for a book generation project.
Your source of truth is the provided "Base Context". 
Refuse to answer questions that are entirely unrelated to the context, 
unless they are simple greetings or clarifications.

When answering:
1.  Relate your answer specifically to the concepts (Knowledge, Skill, Conviction) found in the text.
2.  If the answer is not in the context, state clearly that the information is missing from the provided documents.
3.  Keep the tone professional and educational.
"""

def chat_with_data(user_query: str, context_content: str, history: list = None, temperature: float = 0.7) -> str:
    """
    Sends a message to Gemini maintaining context.
    
    Args:
        user_query: The new message from the user.
        context_content: The base context (system knowledge).
        history: List of previous messages in the format expected by Gemini.
        temperature: Creativity of the model (0.0 to 1.0).
    """
    try:
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 65536,
        }

        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=DEVELOPER_INSTRUCTION,
            generation_config=generation_config
        )
        
        # Prepare history for Gemini
        # We need to convert our stored history format (if necessary) to Gemini's format.
        # Our `app.history` stores {"role": "user/assistant", "content": "..."}
        # Gemini expects {"role": "user/model", "parts": ["..."]}
        
        gemini_history = []
        if history:
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({
                    "role": role,
                    "parts": [msg["content"]]
                })
        
        # If this is a fresh chat, we might want to inject context differently.
        # However, for consistency, we'll prepend the context to the First message 
        # OR just rely on system_instruction (which we are doing).
        # WAIT. In the previous implementation, I attached context to the prompt.
        # Now that we have history, we should attach context to the system_instruction 
        # OR ensure it's always in the context window.
        
        # Improved Strategy:
        # Pass `context_content` inside `system_instruction` to save tokens in history 
        # and keep it authoritative.
        
        full_system_instruction = f"""{DEVELOPER_INSTRUCTION}
        
        --- BASE CONTEXT ---
        {context_content}
        --- END BASE CONTEXT ---
        """
        
        # Re-initialize model with the FULL system instruction containing context
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=full_system_instruction
        )
        
        chat_session = model.start_chat(history=gemini_history)
        response = chat_session.send_message(user_query)
        
        return response.text
        
    except Exception as e:
        print(f"Error in chat_with_data: {e}")
        raise e
