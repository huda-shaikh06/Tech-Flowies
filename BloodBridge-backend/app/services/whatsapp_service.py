import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.core.config import settings
from app.core.supabase import get_supabase_client, is_supabase_configured

logger = logging.getLogger(__name__)


def build_emergency_whatsapp_message(
    donor_name: str,
    blood_group: str,
    hospital_name: str,
    hospital_city: str,
    units: int,
    reference_code: str,
    attendant_name: str,
    attendant_phone: str,
) -> str:
    """Format standardized WhatsApp alert sent to registered standby donors."""
    return (
        f"🚨 *BloodBridge Emergency Alert*\n\n"
        f"Assalam-o-Alaikum *{donor_name}*,\n"
        f"An urgent blood request matching your blood group (*{blood_group}*) has just been created nearby.\n\n"
        f"📋 *Case Reference:* #{reference_code}\n"
        f"🏥 *Hospital:* {hospital_name}, {hospital_city}\n"
        f"🩸 *Requirement:* {units} Unit(s) of {blood_group}\n"
        f"👤 *Attendant:* {attendant_name} (+92 {attendant_phone})\n\n"
        f"If you are available to donate, please reply *YES* immediately to accept this case and receive direct hospital directions.\n"
        f"Reply *NO* if you are currently unavailable."
    )


async def dispatch_whatsapp_notification(
    donor_id: str,
    donor_phone: str,
    donor_name: str,
    request_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Sends WhatsApp message via Meta Cloud API if configured,
    or creates a simulated dispatch log in Supabase.
    """
    reference_code = request_data.get("reference_code", "BB-URGENT")
    hospital = request_data.get("hospital", {})
    hospital_name = hospital.get("name", "Hospital")
    hospital_city = hospital.get("city", "Pakistan")
    blood_group = request_data.get("blood_group", "O+")
    units = request_data.get("units_needed", 1)
    attendant_name = request_data.get("contact_person", "Attendant")
    attendant_phone = request_data.get("contact_phone", "")

    message_body = build_emergency_whatsapp_message(
        donor_name=donor_name,
        blood_group=blood_group,
        hospital_name=hospital_name,
        hospital_city=hospital_city,
        units=units,
        reference_code=reference_code,
        attendant_name=attendant_name,
        attendant_phone=attendant_phone,
    )

    # If WhatsApp Cloud API credentials exist, attempt real send
    whatsapp_msg_id = f"sim_{int(datetime.now(timezone.utc).timestamp())}_{donor_id[:8]}"
    if settings.WHATSAPP_ACCESS_TOKEN and settings.WHATSAPP_PHONE_NUMBER_ID:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
                headers = {
                    "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": f"92{donor_phone.lstrip('0')}",
                    "type": "text",
                    "text": {"preview_url": False, "body": message_body},
                }
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    whatsapp_msg_id = data.get("messages", [{}])[0].get("id", whatsapp_msg_id)
        except Exception as e:
            logger.warning(f"Real WhatsApp send failed, falling back to simulated dispatch: {e}")

    # Record dispatch in Supabase if configured
    client = get_supabase_client()
    if client and is_supabase_configured():
        try:
            client.table("donor_dispatches").insert(
                {
                    "request_id": request_data.get("id"),
                    "donor_id": donor_id,
                    "whatsapp_message_id": whatsapp_msg_id,
                    "status": "dispatched",
                }
            ).execute()
        except Exception as e:
            logger.warning(f"Could not log dispatch to Supabase: {e}")

    return {
        "status": "dispatched",
        "donor_id": donor_id,
        "donor_phone": donor_phone,
        "whatsapp_message_id": whatsapp_msg_id,
        "preview_message": message_body,
    }
