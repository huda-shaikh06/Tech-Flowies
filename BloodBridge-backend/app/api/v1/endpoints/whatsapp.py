from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Query, Body, Request, Response
from app.core.supabase import get_supabase_client, is_supabase_configured

router = APIRouter()


class SimulateAcceptPayload(BaseModel):
    request_id: str
    donor_id: Optional[str] = "donor-mock-1"
    donor_name: Optional[str] = "Hamza Tariq Shaikh"
    donor_phone: Optional[str] = "3019827140"
    blood_group: Optional[str] = "O+"
    location: Optional[str] = "Clifton, Karachi"
    distance_km: Optional[float] = 2.8
    eta_mins: Optional[int] = 20


@router.get("/dispatch-status")
async def get_dispatch_status(request_id: str = Query(...)):
    """
    Returns the real-time WhatsApp dispatch and response status for a case.
    """
    client = get_supabase_client()
    if client and is_supabase_configured():
        try:
            res = (
                client.table("donor_dispatches")
                .select("*, standby_donors(*)")
                .eq("request_id", request_id)
                .execute()
            )
            dispatches = res.data or []
            accepted = [d for d in dispatches if d.get("status") == "accepted"]

            return {
                "request_id": request_id,
                "total_dispatched": len(dispatches),
                "accepted": len(accepted) > 0,
                "matched_donor": accepted[0]["standby_donors"] if accepted else None,
                "dispatches": dispatches,
            }
        except Exception as e:
            print(f"Supabase dispatch status query error: {e}")

    # Fallback status
    return {
        "request_id": request_id,
        "total_dispatched": 4,
        "accepted": False,
        "matched_donor": None,
        "message": "Dispatched emergency WhatsApp request alerts to nearby active donors.",
    }


@router.post("/simulate-accept")
async def simulate_donor_acceptance(payload: SimulateAcceptPayload):
    """
    Simulates a donor replying 'YES' on WhatsApp.
    Updates case status in Supabase to 'donor_matched'.
    """
    client = get_supabase_client()
    if client and is_supabase_configured():
        try:
            # Update blood request status
            client.table("blood_requests").update(
                {
                    "status": "donor_matched",
                    "matched_donor_id": payload.donor_id,
                }
            ).eq("id", payload.request_id).execute()

            # Update dispatch status
            client.table("donor_dispatches").update(
                {
                    "status": "accepted",
                    "responded_at": datetime.now(timezone.utc).isoformat(),
                }
            ).eq("request_id", payload.request_id).execute()
        except Exception as e:
            print(f"Simulation update warning: {e}")

    return {
        "success": True,
        "message": "Donor accepted request via WhatsApp!",
        "matched_donor": {
            "id": payload.donor_id,
            "name": payload.donor_name,
            "phone": payload.donor_phone,
            "blood_group": payload.blood_group,
            "location": payload.location,
            "distance_km": payload.distance_km,
            "eta_mins": payload.eta_mins,
            "donations_count": 7,
        },
    }


@router.get("/webhook")
async def verify_whatsapp_webhook(request: Request):
    """Meta WhatsApp Webhook verification handshake."""
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == "bloodbridge_webhook_secret":
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Verification failed", status_code=403)


@router.post("/webhook")
async def receive_whatsapp_webhook(payload: Dict[str, Any] = Body(...)):
    """Receives live incoming messages and replies from Meta WhatsApp Cloud API."""
    print("Received WhatsApp Webhook payload:", payload)
    return {"status": "received"}
