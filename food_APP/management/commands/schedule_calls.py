from django.core.management.base import BaseCommand
from food_APP.AI.tts import generate_speech
from food_APP.AI.telephony import make_call
from food_APP.models import B2BLead, B2CLead

class Command(BaseCommand):
    help = "Schedule AI calls to leads"

    def handle(self, *args, **kwargs):
        leads = B2BLead.objects.filter(status="pending") | B2CLead.objects.filter(status="pending")

        for lead in leads:
            speech_file = generate_speech(f"Hello {lead.name}, we have an exclusive offer for your event.")
            make_call(lead.contact_number, speech_file)

        self.stdout.write(self.style.SUCCESS(f"✅ {len(leads)} calls scheduled"))
