import uuid
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.donor import (
    StandbyDonorCreate,
    StandbyDonorResponse,
    DonorMatchResult,
)
from app.core.supabase import get_supabase_client, is_supabase_configured
from app.services.matching import find_nearby_standby_donors

router = APIRouter()


@router.post("", response_model=StandbyDonorResponse, status_code=status.HTTP_201_CREATED)
async def register_standby_donor(payload: StandbyDonorCreate):
    """
    Registers a new voluntary standby donor with live GPS coordinates.
    Standby donors register once and are alerted via WhatsApp during urgent matching.
    """
    client = get_supabase_client()
    donor_id = str(uuid.uuid4())

    record = {
        "id": donor_id,
        "name": payload.name,
        "phone": payload.phone,
        "blood_group": payload.blood_group,
        "city": payload.city,
        "area": payload.area,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "is_available": True,
        "total_donations": 0,
    }

    if client and is_supabase_configured():
        try:
            client.table("standby_donors").upsert(record, on_conflict="phone").execute()
        except Exception as e:
            print(f"Supabase donor registration warning: {e}")

    return StandbyDonorResponse(
        id=donor_id,
        name=payload.name,
        phone=payload.phone,
        blood_group=payload.blood_group,
        city=payload.city,
        area=payload.area,
        latitude=payload.latitude,
        longitude=payload.longitude,
        is_available=True,
        total_donations=0,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/match", response_model=List[StandbyDonorResponse])
async def match_nearby_donors(
    blood_group: str = Query(..., description="Recipient blood group, e.g. O+"),
    lat: float = Query(..., description="Hospital latitude"),
    lng: float = Query(..., description="Hospital longitude"),
    city: str = Query("Karachi", description="City name"),
    radius_km: float = Query(30.0, description="Search radius in km"),
):
    """Finds closest compatible standby donors sorted by geodesic distance."""
    donors = await find_nearby_standby_donors(
        blood_group=blood_group,
        target_lat=lat,
        target_lng=lng,
        city=city,
        max_radius_km=radius_km,
        limit=5,
    )

    return [
        StandbyDonorResponse(
            id=d["id"],
            name=d["name"],
            phone=d["phone"],
            blood_group=d["blood_group"],
            city=d["city"],
            area=d.get("area"),
            latitude=float(d["latitude"]),
            longitude=float(d["longitude"]),
            is_available=d.get("is_available", True),
            total_donations=d.get("total_donations", 0),
            distance_km=d.get("distance_km"),
            eta_mins=d.get("eta_mins"),
        )
        for d in donors
    ]
