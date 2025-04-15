from django.core.management.base import BaseCommand
import requests
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

VAPI_BASE_URL = "https://api.vapi.ai/"
HEADERS = {
    "Authorization": f"Bearer {settings.VAPI_API_KEY}"
}

def delete_old_vapi_calls(assistant_id, days_old=7):
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_old)
    deleted = 0
    skipped = 0

    url = f"{VAPI_BASE_URL}call"
    response = requests.get(url, headers=HEADERS)

    print("🔍 Request URL:", url)
    print("🔍 Status Code:", response.status_code)
    print("🔍 Response Text:", response.text)

    response.raise_for_status()

    calls = response.json()
    if not calls:
        return {"deleted": 0, "skipped_recent_calls": 0}

    for call in calls:
        if call.get("assistantId") != assistant_id:
            continue

        call_id = call.get("id")
        created_at_str = call.get("createdAt")

        if not call_id or not created_at_str:
            continue

        created_at = date_parser.parse(created_at_str)
        if created_at < cutoff_time:
            del_url = f"{VAPI_BASE_URL}call/{call_id}"
            del_response = requests.delete(del_url, headers=HEADERS)

            if del_response.status_code == 200:
                print(f"✅ Deleted call {call_id}")
                deleted += 1
            else:
                print(f"❌ Failed to delete call {call_id} - {del_response.status_code}")
        else:
            skipped += 1

    return {
        "deleted": deleted,
        "skipped_recent_calls": skipped
    }

class Command(BaseCommand):
    help = "Delete VAPI conversations older than specified days"

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=7, help='Delete calls older than N days')

    def handle(self, *args, **options):
        days = options['days']
        result = delete_old_vapi_calls(
            assistant_id='b132f51d-a5ad-430f-abbd-c95059cef883',
            days_old=days
        )

        self.stdout.write(self.style.SUCCESS(f"✅ Deleted: {result.get('deleted', 0)} calls"))
        self.stdout.write(self.style.WARNING(f"⏭️ Skipped (recent): {result.get('skipped_recent_calls', 0)} calls"))

        if "error" in result:
            self.stdout.write(self.style.ERROR(f"❌ Error: {result['error']}"))
