import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import logging

logger = logging.getLogger(__name__)

# Configure Gemini API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")
genai.configure(api_key=api_key)

def generate_ai_response(customer_input):
    """Generate a response dynamically using GPT-4"""
    prompt = f"""
    You are an AI telemarketing agent. Speak with a persuasive, natural tone. 
    Customer: {customer_input}
    AI Agent:
    """

    model = genai.GenerativeModel('gemini-2.0-flash')
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Error generating message."
    
