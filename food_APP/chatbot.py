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

def generate_followup_message(status, feedback=None):
    """
    Uses Google Gemini AI to generate a follow-up WhatsApp message.
    """
    prompt = f"""
    You are a customer follow-up assistant for a business. Your job is to engage leads and encourage them to proceed to the next step.

    - Current Lead Status: {status}
    - Feedback Received: {feedback if feedback else "No feedback yet"}

    Generate a professional and friendly follow-up message for WhatsApp.
    """

    model = genai.GenerativeModel('gemini-2.0-flash')
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Error generating message."
    
    
def extract_lead_details_from_conversation(conversation_json):
    """
    Extract structured lead details from the VAPI conversation using Gemini AI.
    """

    # ✅ Check if "messages" exist at different possible locations
    if not isinstance(conversation_json, dict):

        logger.error(f"❌ Unexpected response format. Expected dict but got {type(conversation_json)}")
        return []
    
    # ✅ Extract conversation messages
    conversation_data = None

    if "messages" in conversation_json:
        conversation_data = conversation_json["messages"]
    elif "model" in conversation_json and isinstance(conversation_json["model"], dict) and "messages" in conversation_json["model"]:
        conversation_data = conversation_json["model"]["messages"]
    elif "transcript" in conversation_json and isinstance(conversation_json["transcript"], list):
        conversation_data = conversation_json["transcript"]
    
    # ✅ Validate conversation_data
    if not conversation_data or not isinstance(conversation_data, list) or all("message" not in msg for msg in conversation_data):
        logger.warning(f"⚠️ Skipping empty or invalid conversation for call: {conversation_json.get('id', 'unknown')}")
        return []
    
        # ✅ Add log before continuing
    logger.info(f"📞 Processing call_id: {conversation_json.get('id', 'unknown')} with {len(conversation_data)} messages.")

    
    # ✅ Convert conversation into a clean text format
    conversation_text = "\n".join([
    f"{entry['role'].upper()}: {entry['message']}"
    for entry in conversation_data if "message" in entry
    ])

    if not conversation_text.strip():
        logger.error("❌ Empty conversation text. Cannot extract leads.")
        return []

    # Define a structured prompt for Gemini
    prompt = f"""
You are an AI that extracts structured lead details from a conversation log between an AI telecalling agent and a potential customer.

### Task:
Your job is to analyze the conversation and extract **only relevant lead details** into a structured JSON format. 
Ignore system instructions, tool calls, and irrelevant responses. Focus only on extracting lead information from the **bot and user messages**.

### Expected Output:
Return a **JSON list** where each object represents a lead with the following fields:

if event_type is Corporate or Industrial,

- **"name"**  : The name of the lead 
- **"contact_number"**: The lead’s phone number (must be 10-digit Indian mobile number, or null if not mentioned)
- **"alternate_number"**: The alternate number (must be 10-digit Indian mobile number, or null if not mentioned)
- **"email"**: Email address of the lead (if provided)
- **"event_type"**: The type of event (corporate, Industrial)
- **"company_name"**: The company name (if B2B) 
- **"designation"**: The role/designation of the lead (if B2B) 
- **"delivery_location"**: The location where food will be delivered
- **"count"**: The number of meals requested
- **"required_meal_service"**: The type of meal service (if Breakfast,Lunch,Dinner,Tea & Snacks, Supper, All)
- **"dietary_options"**: The type of food options(if Veg, Non_Veg or Vegan)
- **"service_type"**: Type of service (In-House, Outsource)
- **"service_choice"**: Whether the service is a Just Delivery, buffet, With Service Person
- **"choice_of_menu"**: Any specific menu preferences mentioned 
- **"existing_menu_budget"**: Current budget per meal (if mentioned)
- **"prefered_menu_budget"**: Preferred budget per meal (if mentioned)
- **"meeting_date_time"**: Scheduled meeting date and time 
- **"lead_status"**: this filed act like a sales expert and ,you should analyze the whole conversation and give me a lead status as hot,cold,warm,or not interested.
- **"remark"**: this field will be use to summerize the whole conversation , and give me your remark based on customer's conversation , that would not be more than 100 words.
- **"status"**: Status of the lead (Meeting Scheduled, Meeting Not Scheduled, Not Interested)
- **"created_at"**: Timestamp of the conversation

if event_type is not Corporate nor Industrial,

- **"customer_name"** : The name of the lead 
- **"contact_number"**: The lead’s phone number (must be 10-digit Indian mobile number, or null if not mentioned)
- **"alternate_number"**: The alternate number (must be 10-digit Indian mobile number, or null if not mentioned)
- **"email"**: Email address of the lead (if provided)
- **"event_type"**: The type of event (ex: Birthday, Marriage)
- **"event_date_time"**: The date and time of the event
- **"delivery_location"**: The location where food will be delivered
- **"count"**: The number of meals requested(the count should be exact number what they provide, avoid the text)
- **"required_meal_service"**: The type of meal service (if Breakfast,Lunch,Dinner,Tea & Snacks, Supper, All)
- **"dietary_options"**: The type of food options(if Veg, Non_Veg or Vegan)
- **"service_choice"**: Whether the service is a Just Delivery, buffet, With Service Person
- **"choice_of_menu"**: Any specific menu preferences mentioned 
- **"existing_menu_budget"**: Current budget per meal (if mentioned)
- **"prefered_menu_budget"**: Preferred budget per meal (if mentioned)
- **"meeting_date_time"**: Scheduled meeting date and time 
- **"lead_status"**: this filed act like a sales expert and ,you should analyze the whole conversation and give me a lead status as hot - means interested,cold - means initial conversation only done need more informations ,warm - means provide the details but didn't confirm yet, or need some time to think, or already have vendor i will call you when need, not interested - means totally avoid not give any information.
- **"remark"**: this field will be use to summerize the whole conversation , and give me your remark based on customer's conversation , that would not be more than 100 words.
- **"status"**: Status of the lead (Meeting Scheduled, Meeting Not Scheduled)
- **"created_at"**: Timestamp of the conversation



### Important Extraction Rules:
1. **you need to split the customer B2B or B2C , accordingly you provide the data.
2. **If the event type is "Corporate" or "Industrial", format the response as B2B. Otherwise, format it as B2C**.
3. **Extract only lead-related details** and ignore system messages.
4. **If a field is not explicitly mentioned, set it as `null`**.
5. **Use direct responses from the user** to extract details.
6. **Don't assume data—only use explicitly stated information**.

{conversation_text}

"""

    try:
        # ✅ Step 1: Generate response from Gemini AI
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        # ✅ Step 2: Check if the response exists
        if not response or not response.text:
            logger.error("❌ Gemini AI returned an empty response!")
            return []

        response_text = response.text.strip()

        # ✅ Debugging: Print raw AI response before parsing
        print("🔍 DEBUG: Gemini AI Response:", response_text)

        # ✅ Step 3: Remove Markdown JSON formatting if present
        if response_text.startswith("```json") and response_text.endswith("```"):
            response_text = response_text[7:-3].strip()  # Remove ```json and ```

        # ✅ Step 4: Convert AI response to JSON safely
        try:
            extracted_data = json.loads(response_text)  # Convert AI response to JSON

            if isinstance(extracted_data, list) and all(isinstance(item, dict) for item in extracted_data):
                logger.info("✅ Extracted JSON Data: %s", json.dumps(extracted_data, indent=2))
                return extracted_data
            else:
                logger.error("❌ Gemini returned invalid format: not a list of dicts")
                return []
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Gemini AI response is not valid JSON: {response_text}, Error: {e}")
            return []  # Return empty list if JSON parsing fails

    except Exception as e:
        logger.error(f"❌ Unexpected error in extract_lead_details_from_conversation: {e}")
        return []   
    

def get_lead_score_from_gemini(lead_data, lead_type="B2B"):
    # Start the prompt
    prompt = f"""
    You are an AI model trained to evaluate lead quality for a food CRM. 
    Based on the following {lead_type} lead details, return a lead score from 0 (low quality) to 100 (high quality):

    Lead Details:
    - Lead Status: {lead_data.get('lead_status')}
    - Status: {lead_data.get('status')}
    - Remark: {lead_data.get('remark')}
    - Head Count: {lead_data.get('count')}
    - Location: {lead_data.get('location')}
    - Budget: {lead_data.get('budget')}
    """

    # Add company_name only for B2B
    if lead_type.upper() == "B2B" and "company_name" in lead_data:
        prompt += f"- Company Name: {lead_data.get('company_name')}\n"

    prompt += "\nOnly return the number."

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        score_str = response.text.strip()

        # Try to convert the score to float
        score = float(score_str)
        return round(score, 2)

    except Exception as e:
        print(f"Gemini API error: {e}")
        return 0.0