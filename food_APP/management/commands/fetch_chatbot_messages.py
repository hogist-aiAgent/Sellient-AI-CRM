from django.core.management.base import BaseCommand
from food_APP.views import fetch_bot_leads  # Import chatbot processing function

class Command(BaseCommand):
    help = "Fetch chatbot messages and process responses."

    def handle(self, *args, **kwargs):
        print("Running chatbot_process() from views.py...")
        fetch_bot_leads()  # Call the chatbot function from views
        print("✅ Chatbot messages processed successfully!")
