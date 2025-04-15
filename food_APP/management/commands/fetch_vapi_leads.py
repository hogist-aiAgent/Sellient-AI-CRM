from django.core.management.base import BaseCommand
from food_APP.views import fetch_vapi_leads  # Import existing function

class Command(BaseCommand):
    help = "Fetch and process leads from VAPI API periodically."

    def handle(self, *args, **kwargs):
        print("Running fetch_vapi_leads() from views.py...")
        response = fetch_vapi_leads(None)  # Call function without request
        print("Response:", response.content.decode())
        print("✅ Leads successfully processed and stored!")
