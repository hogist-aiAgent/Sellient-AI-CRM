import requests
import os
import json
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import B2BLead, B2CLead, B2BFollowUp, B2CFollowUp,OutsorceDBLead,InpersonLead
from .serializers import B2BLeadSerializer, B2CLeadSerializer
from .chatbot import generate_followup_message, extract_lead_details_from_conversation, get_lead_score_from_gemini
from django.conf import settings
import logging
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import re
from django.db.models.signals import post_save
from django.dispatch import receiver
from twilio.rest import Client
#from food_APP.AI.tts import generate_speech
#from food_APP.AI.stt import transcribe_audio
from food_APP.AI.chat_ai import generate_ai_response
from food_APP.AI.telephony import make_call
#from food_APP.AI.sentiment import analyze_sentiment
import pandas as pd
from food_APP.column_mapper import COLUMN_ALIASES, auto_map_columns
import time
import joblib
import numpy as np
import calendar


logger = logging.getLogger(__name__)

# API Configuration
BOT_API_URL = "https://beloved-sponge-fitting.ngrok-free.app/get-all-leads/"
VAPI_BASE_URL = "https://api.vapi.ai/"
VAPI_ASSISTANT_ID = "b132f51d-a5ad-430f-abbd-c95059cef883"
VAPI_PHONENUM_ID = "c4a71e4b-5081-4a91-b6d2-68bca75d7dd0"

TWILIO_FALLBACK_ENABLED = True  # Toggle fallback to Twilio

HEADERS = {
    "Authorization": f"Bearer {settings.VAPI_API_KEY}",
    "Content-Type": "application/json"
}

@csrf_exempt
def generate_twiml(request, lead_id):
    """
    Generate TwiML XML for Twilio to connect the call to VAPI AI.
    """
    # ✅ Allow Twilio to bypass ngrok browser warning
    #if "ngrok-skip-browser-warning" not in request.headers:
        #return HttpResponse("Missing ngrok-skip-browser-warning", status=403)
    
    #print(f"Generating TwiML for Lead ID: {lead_id}")  # ✅ Log lead_id

    # ✅ WebSocket URL for VAPI AI Assistant
    vapi_stream_url = f"wss://api.vapi.ai/stream/{settings.VAPI_ASSISTANT_ID}"

    twiml = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Connect>
            <Stream url="{vapi_stream_url}"/>
        </Connect>
    </Response>
    """

    return HttpResponse(twiml, content_type="text/xml")

# ✅ Step 1: Fetch Pending Leads from CRM
def get_pending_leads():
    """Fetch leads from MakeLead table that need outbound calls."""
    return OutsorceDBLead.objects.filter(status="New")

# Stop call process - set the flag to true
CALL_STOPPED = False  # Initially, calling is allowed

@api_view(['POST'])
def stop_call(request):
    global CALL_STOPPED
    CALL_STOPPED = True  # Set the flag to True to stop the calls
    return JsonResponse({"message": "Call process stopped."}, status=200)


# ✅ Step 2: Trigger Outbound Calls Using VAPI
@api_view(['GET'])
def call_ai_agent(request):

    #url = f"{VAPI_BASE_URL}/call?assistant_id={ASSISTANT_ID}"
    """
    Trigger AI outbound calls from CRM using VAPI.
    If VAPI fails, fallback to Twilio using `telephony.py`.
    """
    global CALL_STOPPED

    # If calls are stopped, don't process any calls
    if CALL_STOPPED:
        leads = get_pending_leads()
        if not leads:
            return JsonResponse({"message": "Calls are stopped. No leads to process."}, status=200)
        CALL_STOPPED = False  # Auto-resume ✅

    leads = get_pending_leads()
    if not leads:
        return JsonResponse({"message": "No pending leads to call."}, status=200)

    successful_calls = 0
    failed_calls = 0

    for lead in leads:

        # ✅ Break mid-way if stop button was clicked
        if CALL_STOPPED:
            logger.info("🚫 Call stopped mid-way!")
            break

        phone_number = f"+91{lead.contact_number}"  # Ensure correct format
        lead_id = lead.id  # ✅ Get the lead's ID from the database

        #print("Calling:", phone_number)

        # ✅ Try calling using VAPI
        payload = {
            "phoneNumberId": VAPI_PHONENUM_ID,
            "assistantId": VAPI_ASSISTANT_ID,
            "customer": {
                "name": lead.org_name or "your company",
                "number": phone_number
            }
        }

        vapi_url = f"{VAPI_BASE_URL}call"

        try:
            response = requests.post(vapi_url,json=payload, headers=HEADERS, timeout=10)
            #print("response:",response)
            response.raise_for_status()  # Ensure the request is successful
            lead.status = "initiated"
            lead.save()
            successful_calls += 1

            # ✅ Add a delay between each call to prevent overload
            time.sleep(20)  # Adjust delay time if needed
            continue  # Skip Twilio if VAPI succeeds

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"❌ VAPI HTTP Error for {phone_number}: {http_err}")
            logger.error(f"🔍 VAPI Response: {response.text}")  # ✅ Print VAPI error details
        except requests.exceptions.RequestException as req_err:
            logger.error(f"❌ VAPI Request Failed for {phone_number}: {req_err}")

        if TWILIO_FALLBACK_ENABLED:
            try:
                #speech_url = f"https://api.vapi.ai/twilio/outbound"  # Modify if needed
                twilio_response = make_call(phone_number, lead_id)  # ✅ Fix function call
                if "call_sid" in twilio_response:
                    lead.status = "initiated"
                    lead.save()
                    successful_calls += 1
                else:
                    logger.error(f"❌ Twilio Call Failed for {phone_number}: {twilio_response.get('error')}")
                    failed_calls += 1
            except Exception as e:
                logger.error(f"❌ Error in Twilio Fallback for {phone_number}: {e}")
                failed_calls += 1

    message = "Outbound calls processed."
    if CALL_STOPPED:
        message = "Call process was stopped midway."

    return JsonResponse({
        "message": "Outbound calls processed.",
        "successful_calls": successful_calls,
        "failed_calls": failed_calls
    }, status=200)

@csrf_exempt
def vapi_webhook(request):
    if request.method == 'POST':
        try:
            print(f"Request Body: {request.body}")
            data = json.loads(request.body)
            wh_status = data.get("message", {}).get("status")
            contact_number = data.get("message", {}).get("call", {}).get("customer", {}).get("number")
            ended_reason = data.get("message", {}).get("endedReason", "").lower()

            print("📞 Raw contact_number:", contact_number)
            normalized_number = contact_number[-10:] if contact_number else None
            print("🔢 Normalized:", normalized_number)
            print("🔚 Ended Reason:", ended_reason)
            
            if wh_status == "ended" and normalized_number:
                leads = OutsorceDBLead.objects.filter(contact_number__endswith=normalized_number)
                print("🎯 Matched Leads:", list(leads.values_list('id', 'contact_number', 'status')))

                lead = leads.filter(status__in=["new", "pending","initiated"]).first()

                if lead:
                    if (
                        "customer-did-not-answer" in ended_reason
                        or "busy" in ended_reason
                        or "failed" in ended_reason
                    ):
                        lead.status = "pending"
                        print(f"⚠️ Lead {lead.id} marked as pending")
                    else:
                        lead.status = "called"
                        print(f"✅ Lead {lead.id} marked as called")

                    lead.save()
                    return JsonResponse({"status": f"Lead {lead.id} updated"}, status=200)

                else:
                    print("❌ No matching lead found for this number")
                    return JsonResponse({"status": "No matching lead found"}, status=404)

            return JsonResponse({"status": "No update needed"}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({"error": f"Invalid JSON: {str(e)}"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)



# ✅ Step 3: Fetch Call Responses from VAPI and Update CRM
@api_view(['GET'])
def process_vapi_responses(request):
    """Fetch call responses from VAPI, analyze and store in CRM."""
    try:
        call_ids = get_calls_for_assistant()
        if not call_ids:
            return JsonResponse({"message": "No completed calls found."}, status=200)

        for call_id in call_ids:
            # ✅ Skip already processed calls
            if B2BLead.objects.filter(call_id=call_id).exists() or B2CLead.objects.filter(call_id=call_id).exists():
                logger.info(f"⏭️ Skipping already processed call: {call_id}")
                continue

            conversation_json = fetch_vapi_conversations(call_id)

            # ✅ Skip calls that didn't have a conversation
            if "transcript" not in conversation_json and "messages" not in conversation_json:
                logger.warning(f"⏭️ Skipping call without conversation: {call_id} - Reason: {conversation_json.get('endedReason', 'unknown')}")
                continue

            if not conversation_json:
                logger.error(f"❌ No conversation found for Call ID: {call_id}")
                continue

            # ✅ Rebuild conversation_text locally in views.py
            transcript = conversation_json.get("messages") or \
                        conversation_json.get("model", {}).get("messages") or \
                        conversation_json.get("transcript", [])
            
            conversation_text = "\n".join([
                f"{entry['role'].upper()}: {entry['message']}"
                for entry in transcript if "message" in entry
            ])
            
            #print(f"🔍 DEBUG: Received conversation JSON for Call {call_id} ->", json.dumps(conversation_json, indent=2))

            extracted_leads = extract_lead_details_from_conversation(conversation_json)
            if not extracted_leads or not isinstance(extracted_leads, list):
                continue  # Skip if no leads found or invalid format

            if not isinstance(extracted_leads, list) or not all(isinstance(lead, dict) for lead in extracted_leads):
                logger.error(f"❌ Invalid extracted_leads format: {extracted_leads}")
                continue  # Skip this call

            for lead in extracted_leads:  # ✅ Loop through the extracted leads
                #phone_number = extracted_lead.get("contact_number")  
                #if not phone_number:
                    #logger.error(f"⚠️ Missing contact number in extracted lead: {extracted_lead}")
                    #continue

                event_type = classify_lead_type(conversation_text)

                lead["created_at"] = make_aware(datetime.now())
                lead["call_id"] = call_id  # Store to avoid future reprocessing
                lead["event_type"] = event_type

                save_leads_to_db(extracted_leads)

                # ✅ Save lead into B2B or B2C table
                #save_lead(phone_number, extracted_lead, event_type, lead_score)

        return JsonResponse({"message": "Leads processed successfully and updated in CRM!"}, status=200)

    except Exception as e:
        logger.error(f"❌ Error processing VAPI responses: {e}")
        return JsonResponse({"error": str(e)}, status=500)

# 🚀 Step 1: Fetch Calls for a Specific Assistant
def get_calls_for_assistant():
    url = f"{VAPI_BASE_URL}/call?assistant_id={settings.VAPI_ASSISTANT_ID}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        #print("get_call_for_ass",response)
        call_ids = [call["id"] for call in response.json() if "id" in call]
        #print("call_ids:",call_ids)
        return call_ids
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error fetching calls: {e}")
        return []

# 🚀 Step 2: Fetch Conversation Details for a Call
def fetch_vapi_conversations(call_id):
    url = f"{VAPI_BASE_URL}/call/{call_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        #print("fetch_vapi_conv",response)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error fetching conversation for {call_id}: {e}")
        return None
    
# ✅ Step 6: Classify Lead Type Using AI (B2B or B2C)
def classify_lead_type(conversation_text):
    """Use AI to determine if the lead is B2B or B2C."""
    prompt = f"""
    You are an AI classifying leads:
    - If the event is corporate/business-related, classify it as B2B.
    - If the event is a wedding, birthday, or personal event, classify it as B2C.
    
    Conversation: {conversation_text}
    Classify as B2B or B2C.
    """
    
    ai_response = generate_ai_response(prompt)
    if "B2B" in ai_response:
        return "B2B"
    elif "B2C" in ai_response:
        return "B2C"
    return "Unknown"
    
# 🟢 Helper Functions
def validate_event_type(event_type):
    """Validate if event type is B2B."""
    return event_type if event_type in ["Corporate", "Industrial"] else None

def format_datetime(date_str):
    """ Convert AI-generated date strings into a proper datetime format """
    if not date_str:
        return None  # Return None if date is missing

    date_str = date_str.strip().lower()
    now = datetime.now()

    # Handle "28th of March"
    month_mapping = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }

    match = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+of\s+([a-zA-Z]+)", date_str)
    if match:
        day = match.group(1)
        month_name = match.group(2).lower()
        month_num = month_mapping.get(month_name)
        if month_num:
            date_str = f"{now.year}-{month_num}-{day} 00:00"

    # Handle "tomorrow 5 PM"
    if "tomorrow" in date_str:
        base = now + timedelta(days=1)
        match = re.search(r"(\d{1,2})\s*(am|pm)", date_str)
        if match:
            hour = int(match.group(1))
            if match.group(2) == "pm" and hour != 12:
                hour += 12
            base = base.replace(hour=hour, minute=0, second=0, microsecond=0)
        return make_aware(base)

    # Handle "today 5 PM"
    if "today" in date_str:
        base = now
        match = re.search(r"(\d{1,2})\s*(am|pm)", date_str)
        if match:
            hour = int(match.group(1))
            if match.group(2) == "pm" and hour != 12:
                hour += 12
            base = base.replace(hour=hour, minute=0, second=0, microsecond=0)
        return make_aware(base)

    # Handle weekday like "Monday, 3 PM"
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i, day in enumerate(weekdays):
        if day in date_str:
            today_idx = now.weekday()
            days_ahead = (i - today_idx + 7) % 7 or 7
            base = now + timedelta(days=days_ahead)
            match = re.search(r"(\d{1,2})\s*(am|pm)", date_str)
            if match:
                hour = int(match.group(1))
                if match.group(2) == "pm" and hour != 12:
                    hour += 12
                base = base.replace(hour=hour, minute=0, second=0, microsecond=0)
            return make_aware(base)

    # Known datetime formats
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d-%m-%Y %I:%M %p",
        "%B %d, %Y %I:%M %p",
        "%d-%m-%Y",
        "%Y-%m-%d",
    ]

    # Try dateutil parser
    try:
        return make_aware(date_parser.parse(date_str, fuzzy=True))
    except Exception:
        pass

    # Try fixed formats
    for fmt in formats:
        try:
            return make_aware(datetime.strptime(date_str, fmt))
        except Exception:
            continue

    print(f"⚠️ Invalid date format: {date_str}")
    return None

def validate_dietary_option(dietary_options):
    """Ensure dietary_options contains only valid choices."""
    valid_options = ["Veg", "Non_Veg", "Vegan"]
    return dietary_options if dietary_options in valid_options else "Veg"


def clean_lead_data(lead):
    """ Standardize lead data before saving """

    event_type = (lead.get("event_type") or "").strip().upper()
    is_b2b = event_type == "B2B"

    cleaned_data = {
        "contact_number": lead.get("contact_number"),
        "alternate_number": lead.get("alternate_number"),
        "email": lead.get("email", ""),
        "event_type": lead.get("event_type"),
        "delivery_location": lead.get("delivery_location", "Unknown"),
        "count": int(lead["count"]) if lead.get("count") else None,  # Keep None if missing
        "required_meal_service": lead.get("required_meal_service"),  # No default; avoid false data
        "dietary_options": validate_dietary_option(lead.get("dietary_options")),
        "service_choice": lead.get("service_choice"),  # No default; avoid false data
        "choice_of_menu": lead.get("choice_of_menu", ""),
        "existing_menu_budget": lead.get("existing_menu_budget"),
        "prefered_menu_budget": lead.get("prefered_menu_budget"),
        "meeting_date_time": format_datetime(lead.get("meeting_date_time") or ""),
        "lead_status": lead.get("lead_status"),
        "status": lead.get("status"),  # No default; avoid false data
        "remark": lead.get("remark"),
        "lead_score": get_lead_score_from_gemini(lead, "B2B" if is_b2b else "B2C"),
        "created_at": lead.get("created_at", make_aware(datetime.now())),
        "call_id": lead.get("call_id"),
    }

    # Handle B2B-specific fields

    if is_b2b:
        cleaned_data["name"] = lead.get("name", "Unknown")
        cleaned_data["company_name"] = lead.get("company_name")
        cleaned_data["designation"] = lead.get("designation")
        cleaned_data["service_type"] = lead.get("service_type")
    else:
        cleaned_data["customer_name"] = lead.get("customer_name", lead.get("name", "Unknown"))
        # Fallback to meeting_date_time if event_date_time is missing
        cleaned_data["event_date_time"] = format_datetime(lead.get("event_date_time") or "") or format_datetime(lead.get("meeting_date_time") or "")


        #if not cleaned_data["event_date_time"]:
            #lead_type = "B2B" if is_b2b else "B2C"
            #print(f"⚠️ Skipping {lead_type} lead due to missing event_date_time: {lead}")
            #return None  # Skip invalid B2C leads
        
    #if "created_at" in lead:
        #del lead["created_at"]

    return cleaned_data    

# 🟢 Function to Save Leads into Database
def save_leads_to_db(extracted_leads):
    """ Saves leads into B2BLead or B2CLead models """
    successful_saves = 0
    failed_saves = 0

    for lead in extracted_leads:
        try:
            event_type = (lead.get("event_type") or "").strip().upper()
            is_b2b = event_type == "B2B"

            cleaned_lead = clean_lead_data(lead)

            #if not cleaned_lead or not cleaned_lead.get("contact_number"):
                #logger.warning(f"⚠️ Skipping lead due to missing contact number or cleaned data: {lead}")
                #failed_saves += 1
                #continue

            if not cleaned_lead:
                logger.warning(f"⚠️ Skipping lead due to invalid data: {lead}")
                failed_saves += 1
                continue


            if is_b2b:
                B2BLead.objects.create(**cleaned_lead)
            else:
                B2CLead.objects.create(**cleaned_lead)

            successful_saves += 1

        except Exception as e:
            failed_saves += 1
            logger.error(f"❌ Failed to save lead: {lead}. Error: {e}")

    return successful_saves, failed_saves# 🚀 FETCH LEADS FROM BOT API


@api_view(['GET'])
def fetch_bot_leads(request):
    """
    Fetch leads from the external bot API via ngrok and save them to the database.
    """
    try:
        response = requests.get(BOT_API_URL)
        response.raise_for_status()
        leads = response.json()

        for lead in leads:
            if lead.get("type") == "B2B":
                B2BLead.objects.create(
                    name=lead.get("name"),
                    contact_number = lead.get("contact_number"),
                    alternate_number = lead.get("alternate_number"),
                    email = lead.get("email"),
                    event_type = lead.get("event_type"),
                    company_name = lead.get("company_name"),
                    designation = lead.get("designation"),
                    delivery_location =lead.get("delivery_location"),
                    count = lead.get("count"),
                    required_meal_service=lead.get("required_meal_service"),
                    service_type=lead.get("service_type"),
                    service_choice=lead.get("service_choice"),
                    choice_of_menu=lead.get("choice_of_menu"),
                    existing_menu_budget=lead.get("existing_menu_budget"),
                    prefered_menu_budget=lead.get("prefered_menu_budget"),
                    meeting_date_time=lead.get("meeting_date_time"),
                    status=lead.get("status"),
                    created_at = lead.get("created_at"),
                )
            elif lead.get("type") == "B2C":
                B2CLead.objects.create(
                    customer_name = lead.get("customer_name"),
                    contact_number = lead.get("contact_number"),
                    alternate_number = lead.get("alternate_number"),
                    email = lead.get("email"),
                    event_type = lead.get("event_type"),
                    event_date_time = lead.get("event_date_time"),
                    delivery_location = lead.get("delivery_location"),
                    count = lead.get("count"),
                    required_meal_service = lead.get("required_meal_service"),
                    dietary_options = lead.get("dietary_options"),
                    service_choice = lead.get("service_choice"),
                    choice_of_menu = lead.get("choice_of_menu"),
                    existing_menu_budget = lead.get("existing_menu_budget"),
                    prefered_menu_budget = lead.get("prefered_menu_budget"),
                    meeting_date_time = lead.get("meeting_date_time"),
                    status = lead.get("status"),
                    created_at = lead.get("created_at"), 
                )

        return JsonResponse({"message": "Leads fetched and stored successfully!"}, status=200)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Failed to fetch leads: {str(e)}"}, status=500)

@csrf_exempt
def upload_excel(request):
    if request.method == "POST" and request.FILES.get("file"):
        excel_file = request.FILES["file"]
        df = pd.read_excel(excel_file)

        # Auto map
        df = auto_map_columns(df, COLUMN_ALIASES)

        # Required fields only
        fields = ["org_name","designation","name","contact_number", "mail_id", "Address"]
        df = df[[col for col in fields if col in df.columns]]

        # Drop rows without contact number
        df = df[df["contact_number"].notnull()]
        df["contact_number"] = df["contact_number"].astype(str).str.split(".").str[0]

        leads = [
            OutsorceDBLead(
                name=row.get("name", "Unknown"),  # Default value for name
                org_name=row.get("org_name", "Unknown"),  # Default value for org_name
                designation=row.get("designation", "Unknown"),  # Default value for designation
                contact_number=row.get("contact_number", ""),  # Default to empty string if contact_number is missing
                mail_id=row.get("mail_id", "Unknown"),  # Default value for mail_id
                Address=row.get("Address", "Unknown"),  # Default value for Address
                created_at=datetime.now(),
                source_come_from="PDataBase",  # Assuming this is fixed value
                status="new"  # Default status to "New"
    )
    for row in df.to_dict(orient="records")
]
        OutsorceDBLead.objects.bulk_create(leads)
        return JsonResponse({"message": "✅ Uploaded successfully!"})

    return JsonResponse({"error": "No file uploaded."}, status=400)

@api_view(['GET'])
def get_outsource_leads(request):
    data = OutsorceDBLead.objects.all().values()
    return JsonResponse(list(data), safe=False)
    
@api_view(['GET'])
def get_inperson_leads(request):
    data = InpersonLead.objects.all().values()
    return JsonResponse(list(data), safe=False)

@api_view(['GET'])
def get_b2b_leads(request):
    data = B2BLead.objects.all().values()
    return JsonResponse(list(data), safe=False)

@api_view(['GET'])
def get_b2c_leads(request):
    data = B2CLead.objects.all().values()
    return JsonResponse(list(data), safe=False)

def export_b2b_excel(request):
    date = request.GET.get("date")
    month = request.GET.get("month")
    year = request.GET.get("year")

    # Convert month name to number if it's a month name (e.g., 'March' -> '03')
    if month:
        try:
            if month.isdigit():  # If the month is already numeric (e.g., '03')
                month = int(month)
            else:  # If the month is a name (e.g., 'March')
                month = list(calendar.month_name).index(month.capitalize())
        except ValueError:
            return JsonResponse({"error": "Invalid month name"}, status=400)

    queryset = B2BLead.objects.all()

    if date:
        queryset = queryset.filter(created_at__date=date)
    if month:
        queryset = queryset.filter(created_at__month=month)
    if year:
        queryset = queryset.filter(created_at__year=year)

    df = pd.DataFrame(list(queryset.values()))

    
    # Ensure created_at is timezone naive (no timezone information)
    if 'created_at' in df.columns:
        df['created_at'] = df['created_at'].apply(lambda x: x.replace(tzinfo=None) if pd.notnull(x) else x)

    if 'meeting_date_time' in df.columns:
        df['meeting_date_time'] = df['meeting_date_time'].apply(lambda x: x.replace(tzinfo=None) if pd.notnull(x) else x)

    # Ensure all datetime columns are timezone naive before writing to Excel
    for column in df.select_dtypes(include=['datetime']).columns:
        df[column] = df[column].apply(lambda x: x.replace(tzinfo=None) if pd.notnull(x) else x)

    # Generate dynamic filename based on the provided filters
    filename = "b2b_leads"
    if year:
        filename += f"_{year}"
    if month:
        filename += f"_{month:02d}"  # Ensuring the month is two digits
    if date:
        filename += f"_{date}"

    filename += ".xlsx"  # Add file extension

    # Save the file to the server directory
    file_path = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
    print(f"File will be saved at: {file_path}")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save the dataframe to the file path
    df.to_excel(file_path, index=False)

    # Provide the download link to the frontend
    file_url = f"{settings.MEDIA_URL}exports/{filename}"

    return JsonResponse({"file_url": file_url})

def export_b2c_excel(request):
    date = request.GET.get("date")
    month = request.GET.get("month")
    year = request.GET.get("year")

    try:

        queryset = B2CLead.objects.all()

        if date:
            queryset = queryset.filter(created_at__date=date)
        if month:
            queryset = queryset.filter(created_at__month=month)
        if year:
            queryset = queryset.filter(created_at__year=year)

        df = pd.DataFrame(list(queryset.values()))

        # Generate dynamic filename based on the provided filters
        filename = "b2b_leads"
        if year:
            filename += f"_{year}"
        if month:
            filename += f"_{month:02d}"  # Ensuring the month is two digits
        if date:
            filename += f"_{date}"

        filename += ".xlsx"  # Add file extension

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, response, index=False)

        #df.to_excel(response, index=False)
        return response
    except Exception as e:
        logger.error(f"Error while exporting B2B leads: {e}")
        return HttpResponse("Error generating file", status=500)

    
# 🚀 WhatsApp Follow-Up Bot
@csrf_exempt
def followup_bot(request):
    """
    AI-powered WhatsApp follow-up bot.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            phone = data.get("phone")
            status = data.get("status")
            feedback = data.get("feedback")

            if not phone or not status:
                return JsonResponse({"error": "Phone and status are required."}, status=400)

            # Generate AI follow-up message
            ai_message = generate_followup_message(status, feedback)

            # Send WhatsApp message
            whatsapp_response = send_whatsapp_message(phone, ai_message)

            # Store follow-up in the database
            followup = None
            if B2BLead.objects.filter(contact_number=phone).exists():
                followup = B2BFollowUp.objects.create(
                    contact_number=phone,
                    followup_message=ai_message,
                    followup_status=status,
                    feedback=feedback
                )
            elif B2CLead.objects.filter(contact_number=phone).exists():
                followup = B2CFollowUp.objects.create(
                    contact_number=phone,
                    followup_message=ai_message,
                    followup_status=status,
                    feedback=feedback
                )
            else:
                return JsonResponse({"error": "Lead not found."}, status=404)

            return JsonResponse({
                "message": ai_message,
                "whatsapp_response": whatsapp_response,
                "followup_id": followup.id
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)


def send_whatsapp_message(phone, message):
    """
    Send a WhatsApp message using Twilio API.
    """
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+16012285963")
    
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    try:
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{phone}",
            body=message
        )
        return {"status": "success", "sid": message.sid}
    except Exception as e:
        return {"error": str(e)}

# ---- Automatically Activate Follow-Up Bot for B2B Leads ----
# 🚀 Auto Follow-Up Trigger for B2B
@receiver(post_save, sender=B2BLead)
def activate_b2b_followup(sender, instance, created, **kwargs):
    """
    Automatically create a follow-up when the lead status changes to 'Meeting Scheduled'
    """
    if instance.status == "meeting_scheduled":
        followup_message = generate_followup_message(instance.status)

        followup, created = B2BFollowUp.objects.update_or_create(
            contact_number=instance.contact_number,
            defaults={
                "followup_message": followup_message,
                "followup_status": "meeting_scheduled",
            }
        )

        send_whatsapp_message(instance.contact_number, followup_message)

# 🚀 Auto Follow-Up Trigger for B2C
@receiver(post_save, sender=B2CLead)
def activate_b2c_followup(sender, instance, created, **kwargs):
    """
    Automatically create a follow-up when the lead status changes to 'Meeting Scheduled'
    """
    if instance.status == "meeting_scheduled":
        followup_message = generate_followup_message(instance.status)

        followup, created = B2CFollowUp.objects.update_or_create(
            contact_number=instance.contact_number,
            defaults={
                "followup_message": followup_message,
                "followup_status": "meeting_scheduled",
            }
        )

        send_whatsapp_message(instance.contact_number, followup_message)


# 🚀 CRUD OPERATIONS FOR B2B LEADS
@api_view(['GET'])
def b2b_list(request):
    """
    List all stored B2B leads.
    """
    leads = B2BLead.objects.all()
    serializer = B2BLeadSerializer(leads, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def b2b_create(request):
    """
    Create a new B2B lead.
    """
    serializer = B2BLeadSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def b2b_detail(request, pk):
    """
    Get a single B2B lead by ID.
    """
    try:
        lead = B2BLead.objects.get(pk=pk)
        serializer = B2BLeadSerializer(lead)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except B2BLead.DoesNotExist:
        return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def b2b_update(request, pk):
    """
    Update an existing B2B lead.
    """
    try:
        lead = B2BLead.objects.get(pk=pk)
        serializer = B2BLeadSerializer(lead, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except B2BLead.DoesNotExist:
        return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def b2b_delete(request, pk):
    """
    Delete a B2B lead.
    """
    try:
        lead = B2BLead.objects.get(pk=pk)
        lead.delete()
        return Response({"message": "Lead deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except B2BLead.DoesNotExist:
        return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)


# 🚀 CRUD OPERATIONS FOR B2C LEADS
@api_view(['GET'])
def b2c_list(request):
    """
    List all stored B2C leads.
    """
    leads = B2CLead.objects.all()
    serializer = B2CLeadSerializer(leads, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def b2c_create(request):
    """
    Create a new B2C lead.
    """
    serializer = B2CLeadSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def b2c_detail(request, pk):
    """
    Get a single B2C lead by ID.
    """
    try:
        lead = B2CLead.objects.get(pk=pk)
        serializer = B2CLeadSerializer(lead)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except B2CLead.DoesNotExist:
        return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def b2c_update(request, pk):
    """
    Update an existing B2C lead.
    """
    try:
        lead = B2CLead.objects.get(pk=pk)
        serializer = B2CLeadSerializer(lead, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except B2CLead.DoesNotExist:
        return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def b2c_delete(request, pk):
    """
    Delete a B2C lead.
    """
    try:
        lead = B2CLead.objects.get(pk=pk)
        lead.delete()
        return Response({"message": "Lead deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except B2CLead.DoesNotExist:
        return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)
