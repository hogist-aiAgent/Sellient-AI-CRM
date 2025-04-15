# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OutsorceDBLead, InpersonLead, B2BLead, B2CLead
from .chatbot import get_lead_score_from_gemini
import logging

logger = logging.getLogger(__name__)  # Put this at the top of your file



@receiver(post_save, sender=OutsorceDBLead)
def update_b2b_contact_from_outsource(sender, instance, **kwargs):
    if instance.status.lower() == "called":
        b2b = B2BLead.objects.filter(from_outsource=instance).first()
        if b2b:
            b2b.contact_number = instance.contact_number
            b2b.save()


@receiver(post_save, sender=InpersonLead)
def update_b2b_contact_from_inperson(sender, instance, **kwargs):
    if instance.status.lower() == "called":
        b2b = B2BLead.objects.filter(from_inperson=instance).first()
        if b2b:
            b2b.contact_number = instance.contact_number
            b2b.save()

# --- B2B Signal ---
@receiver(post_save, sender=B2BLead)
def assign_b2b_lead_score(sender, instance, created, **kwargs):
    if created:
        lead_data = {
            "lead_status": instance.lead_status or "not provided",
            "status": instance.status or "not provided",
            "remark": instance.remark or "no remark",
            "count": instance.count or 0,
            "location": instance.delivery_location or "unknown",
            "budget": instance.prefered_menu_budget or 0,
            "company_name": instance.company_name or "unknown"
        }

        # 🔍 Log missing fields for debugging
        missing_fields = [k for k, v in lead_data.items() if v in [None, "", 0, "not provided", "unknown", "no remark"]]
        if missing_fields:
            logger.warning(f"[B2B] Missing fields for lead ID {instance.id}: {', '.join(missing_fields)}")

        try:
            score = get_lead_score_from_gemini(lead_data, lead_type="B2B")
            instance.lead_score = score
            instance.save(update_fields=["lead_score"])
        except Exception as e:
            logger.error(f"❌ Error calculating B2B lead score for ID {instance.id}: {e}")


# --- B2C Signal ---
@receiver(post_save, sender=B2CLead)
def assign_b2c_lead_score(sender, instance, created, **kwargs):
    if created:
        lead_data = {
            "lead_status": instance.lead_status or "not provided",
            "status": instance.status or "not provided",
            "remark": instance.remark or "no remark",
            "count": instance.count or 0,
            "location": instance.delivery_location or "unknown",
            "budget": instance.prefered_menu_budget or 0
        }

        # 🔍 Log missing fields
        missing_fields = [k for k, v in lead_data.items() if v in [None, "", 0, "not provided", "unknown", "no remark"]]
        if missing_fields:
            logger.warning(f"[B2C] Missing fields for lead ID {instance.id}: {', '.join(missing_fields)}")

        try:
            score = get_lead_score_from_gemini(lead_data, lead_type="B2C")
            instance.lead_score = score
            instance.save(update_fields=["lead_score"])
        except Exception as e:
            logger.error(f"❌ Error calculating B2C lead score for ID {instance.id}: {e}")