# app/utils.py
import requests
from django.conf import settings

def send_whatsapp_message(lead, source="Lead"):

    print("🟡 [DEBUG] WhatsApp send function called")
    print("🔥 WhatsApp send function called!")
    print("Sending to:", settings.SALES_WHATSAPP_NUMBERS)
    print("Instance ID:", settings.ULTRAMSG_INSTANCE_ID)
    print("Token:", settings.ULTRAMSG_TOKEN)

    name = getattr(lead, 'name', getattr(lead, 'company_name', 'N/A'))

    message = f"""
 *Warm Lead Alert!*

 *Name/Company:* {name}
 *Designation:* {lead.designation}
 *Email:* {lead.email}
 *Phone:* {lead.contact_number}
 *Delivery Location:* {lead.delivery_location}
 *Count:* {lead.count}
 *Preferred Budget:* ₹{lead.prefered_menu_budget}
 *Choice of Menu:* {lead.choice_of_menu}
 *Remarks:* {lead.remark}
 *Source Table:* {source}
 *Lead Status:* {lead.lead_status}
 *Status:* {lead.status}
 *Meeting Date/Time:* {lead.meeting_date_time}
"""


    for phone in settings.SALES_WHATSAPP_NUMBERS:
        url = f"https://api.ultramsg.com/{settings.ULTRAMSG_INSTANCE_ID}/messages/chat"
        payload = {
            "token": settings.ULTRAMSG_TOKEN,
            "to": phone,
            "body": message
        }

        headers = {'content-type': 'application/x-www-form-urlencoded'}
        try:
            response = requests.post(url, data=payload, headers=headers) 
            print(f"UltraMsg response: {response.status_code} | {response.text}")
        except Exception as e:
            print(f"[UltraMsg ERROR] {e}")
