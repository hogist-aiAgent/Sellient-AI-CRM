from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def make_call(customer_phone, lead_id):
    """
    Trigger an AI-driven outbound call using Twilio.
    speech_url: URL containing the AI-generated speech file
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        twiml_url = f" https://fe50-49-204-118-43.ngrok-free.app/twiml/{lead_id}/?ngrok-skip-browser-warning=true"  # ✅ TwiML endpoint

        call = client.calls.create(
            to=customer_phone,
            from_=settings.TWILIO_PHONE_NUMBER,
            url=twiml_url    # Twilio will fetch and play this audio
        )

        logger.info(f"✅ Twilio call initiated to {customer_phone}, Call SID: {call.sid}")
        return {"status": "success", "call_sid": call.sid}

    except Exception as e:
        logger.error(f"❌ Twilio call failed for {customer_phone}: {str(e)}")
        return {"error": str(e)}
