import uuid
import random
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.request import (
    BloodRequestCreate,
    BloodRequestResponse,
    BloodRequestStatusUpdate,
    HospitalInfo,
)
from app.core.supabase import get_supabase_client, is_supabase_configured
from app.services.matching import find_nearby_standby_donors
from app.services.whatsapp_service import dispatch_whatsapp_notification

router = APIRouter()


def generate_reference_code(city: str) -> str:
    """Generate clean case reference code e.g. BB-KHI-4812"""
    city_prefix = (city[:3] if city else "PAK").upper()
    random_digits = random.randint(1000, 9999)
    return f"BB-{city_prefix}-{random_digits}"


@router.post("", response_model=BloodRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_blood_request(payload: BloodRequestCreate):
    """
    Creates an emergency blood request, generates a reference code,
    and initiates standby donor search and notifications.
    """
    reference_code = generate_reference_code(payload.hospital_city)
    request_id = str(uuid.uuid4())
    client = get_supabase_client()

    db_record = {
        "id": request_id,
        "reference_code": reference_code,
        "blood_group": payload.blood_group,
        "blood_component": payload.blood_component,
        "units_needed": payload.units_needed,
        "urgency": payload.urgency,
        "hospital_name": payload.hospital_name,
        "hospital_area": payload.hospital_area,
        "hospital_city": payload.hospital_city,
        "hospital_latitude": payload.hospital_latitude,
        "hospital_longitude": payload.hospital_longitude,
        "contact_person": payload.contact_person,
        "contact_phone": payload.contact_phone,
        "notes": payload.notes,
        "status": "searching",
    }

    if client and is_supabase_configured():
        try:
            client.table("blood_requests").insert(db_record).execute()
        except Exception as e:
            print(f"Supabase request insert warning: {e}")

    # Initiate background matching & notifications to closest donors
    nearby_donors = await find_nearby_standby_donors(
        blood_group=payload.blood_group,
        target_lat=payload.hospital_latitude,
        target_lng=payload.hospital_longitude,
        city=payload.hospital_city,
        max_radius_km=30.0,
        limit=3,
    )

    for donor in nearby_donors:
        await dispatch_whatsapp_notification(
            donor_id=donor["id"],
            donor_phone=donor["phone"],
            donor_name=donor["name"],
            request_data={
                "id": request_id,
                "reference_code": reference_code,
                "blood_group": payload.blood_group,
                "units_needed": payload.units_needed,
                "hospital": {
                    "name": payload.hospital_name,
                    "city": payload.hospital_city,
                },
                "contact_person": payload.contact_person,
                "contact_phone": payload.contact_phone,
            },
        )

    return BloodRequestResponse(
        id=request_id,
        reference_code=reference_code,
        blood_group=payload.blood_group,
        blood_component=payload.blood_component,
        units_needed=payload.units_needed,
        urgency=payload.urgency,
        hospital=HospitalInfo(
            name=payload.hospital_name,
            area=payload.hospital_area,
            city=payload.hospital_city,
            latitude=payload.hospital_latitude,
            longitude=payload.hospital_longitude,
        ),
        contact_person=payload.contact_person,
        contact_phone=payload.contact_phone,
        notes=payload.notes,
        status="searching",
        created_at=datetime.now(timezone.utc),
    )


@router.get("", response_model=List[BloodRequestResponse])
async def list_blood_requests(
    city: Optional[str] = Query(None, description="Filter by city"),
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
):
    """Lists recent blood requests, optionally filtered by city and status."""
    client = get_supabase_client()
    results = []

    if client and is_supabase_configured():
        try:
            query = client.table("blood_requests").select("*")
            if city and city.lower() != "all pakistan":
                query = query.ilike("hospital_city", f"%{city}%")
            if status_filter:
                query = query.eq("status", status_filter)

            res = query.order("created_at", desc=True).limit(limit).execute()
            raw_data = res.data or []

            for row in raw_data:
                results.append(
                    BloodRequestResponse(
                        id=row["id"],
                        reference_code=row["reference_code"],
                        blood_group=row["blood_group"],
                        blood_component=row.get("blood_component", "Whole Blood"),
                        units_needed=row["units_needed"],
                        urgency=row["urgency"],
                        hospital=HospitalInfo(
                            name=row["hospital_name"],
                            area=row.get("hospital_area"),
                            city=row["hospital_city"],
                            latitude=float(row.get("hospital_latitude", 24.86)),
                            longitude=float(row.get("hospital_longitude", 67.00)),
                        ),
                        contact_person=row["contact_person"],
                        contact_phone=row["contact_phone"],
                        notes=row.get("notes"),
                        status=row.get("status", "searching"),
                        matched_donor_id=row.get("matched_donor_id"),
                    )
                )
            return results
        except Exception as e:
            print(f"Supabase list requests error: {e}")

    # Fallback mock response for local testing
    return [
        BloodRequestResponse(
            id="mock-req-1",
            reference_code="BB-KHI-4819",
            blood_group="O+",
            blood_component="Whole Blood",
            units_needed=2,
            urgency="emergency",
            hospital=HospitalInfo(
                name="Liaquat National Hospital",
                area="Gulshan-e-Iqbal",
                city="Karachi",
                latitude=24.8933,
                longitude=67.0678,
            ),
            contact_person="Tariq Memon",
            contact_phone="3001234567",
            status="searching",
            created_at=datetime.now(timezone.utc),
        )
    ]


@router.patch("/{request_id}/status", response_model=BloodRequestResponse)
async def update_request_status(request_id: str, payload: BloodRequestStatusUpdate):
    """Updates the request status (e.g. donor_matched, fulfilled, cancelled)."""
    client = get_supabase_client()
    if client and is_supabase_configured():
        try:
            update_data = {"status": payload.status}
            if payload.matched_donor_id:
                update_data["matched_donor_id"] = payload.matched_donor_id

            client.table("blood_requests").update(update_data).eq("id", request_id).execute()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return BloodRequestResponse(
        id=request_id,
        reference_code="BB-UPDATED",
        blood_group="O+",
        blood_component="Whole Blood",
        units_needed=1,
        urgency="urgent",
        hospital=HospitalInfo(
            name="Hospital",
            city="Pakistan",
            latitude=24.86,
            longitude=67.00,
        ),
        contact_person="Attendant",
        contact_phone="3001234567",
        status=payload.status,
        matched_donor_id=payload.matched_donor_id,
    )
