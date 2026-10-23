from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Query
from app.services.matching import haversine_distance_km

router = APIRouter()


class BloodBankResponse(BaseModel):
    id: str
    name: str
    city: str
    area: str
    province: str
    phone: str
    hours: str
    latitude: float
    longitude: float
    services: List[str]
    distance_km: Optional[float] = None


VERIFIED_PAKISTAN_BLOOD_BANKS = [
    {
        "id": "bb-khi-1",
        "name": "JPMC Blood Bank & Transfusion Center",
        "city": "Karachi",
        "area": "Rafiqui Shaheed Road, Karachi Cantt",
        "province": "Sindh",
        "phone": "021-99201300",
        "hours": "24/7 Emergency Transfusion Desk",
        "latitude": 24.8532,
        "longitude": 67.0457,
        "services": ["Emergency Trauma OT", "Platelets", "Component Separation"],
    },
    {
        "id": "bb-khi-2",
        "name": "The Indus Hospital Blood Center",
        "city": "Karachi",
        "area": "Korangi Crossing, Korangi",
        "province": "Sindh",
        "phone": "021-111111880",
        "hours": "24/7 Central Blood Screening",
        "latitude": 24.8239,
        "longitude": 67.1264,
        "services": ["100% Voluntarily Screened", "NAT Testing", "Platelet Apheresis"],
    },
    {
        "id": "bb-lhr-1",
        "name": "Shaukat Khanum Memorial Blood Center",
        "city": "Lahore",
        "area": "7A Block R-3, Johar Town",
        "province": "Punjab",
        "phone": "042-35905000",
        "hours": "24/7 Oncology Transfusion Services",
        "latitude": 31.4725,
        "longitude": 74.2691,
        "services": ["Apheresis Platelets", "NAT Screened PRBC", "Plasma Exchange"],
    },
    {
        "id": "bb-isb-1",
        "name": "PIMS Hospital Central Blood Bank",
        "city": "Islamabad",
        "area": "G-8/3, Sector G-8",
        "province": "Islamabad Capital",
        "phone": "051-9261170",
        "hours": "24/7 Federal Emergency Supply",
        "latitude": 33.7045,
        "longitude": 73.0567,
        "services": ["Whole Blood", "Emergency Trauma Support", "FFP Plasma"],
    },
    {
        "id": "bb-hyd-1",
        "name": "LUMHS Diagnostic & Research Blood Bank",
        "city": "Hyderabad",
        "area": "Civil Hospital Road, Saddar",
        "province": "Sindh",
        "phone": "022-9210207",
        "hours": "24/7 Regional Emergency Hub",
        "latitude": 25.3942,
        "longitude": 68.3685,
        "services": ["24/7 Cross-Match", "Component Separation", "Trauma Supply"],
    },
    {
        "id": "bb-pesh-1",
        "name": "Lady Reading Hospital (LRH) Blood Bank",
        "city": "Peshawar",
        "area": "Soekarno Square, Andar Shehr",
        "province": "Khyber Pakhtunkhwa",
        "phone": "091-9211430",
        "hours": "24/7 Provincial Emergency Desk",
        "latitude": 34.0094,
        "longitude": 71.5732,
        "services": ["Trauma Emergency", "Platelet Apheresis", "Cross Matching"],
    },
]


from app.core.supabase import get_supabase_client, is_supabase_configured

@router.get("", response_model=List[BloodBankResponse])
async def get_nearest_blood_banks(
    lat: Optional[float] = Query(None, description="User latitude"),
    lng: Optional[float] = Query(None, description="User longitude"),
    city: Optional[str] = Query(None, description="Filter by city name"),
):
    """
    Returns verified 24/7 hospital blood banks.
    Queries Supabase hospital_blood_banks with local fallback.
    If coordinates are provided, results are sorted by proximity.
    """
    client = get_supabase_client()
    banks = []

    if client and is_supabase_configured():
        try:
            q = client.table("hospital_blood_banks").select("*")
            if city and city.lower() != "all pakistan":
                q = q.ilike("city", f"%{city}%")
            res = q.execute()
            if res.data:
                banks = res.data
        except Exception as e:
            print(f"Supabase hospital blood banks query error: {e}")

    if not banks:
        banks = list(VERIFIED_PAKISTAN_BLOOD_BANKS)
        if city and city.lower() != "all pakistan":
            filtered = [b for b in banks if b["city"].lower() == city.lower()]
            if filtered:
                banks = filtered

    results = []
    for b in banks:
        dist = None
        b_lat = float(b["latitude"])
        b_lng = float(b["longitude"])
        if lat is not None and lng is not None:
            dist = haversine_distance_km(lat, lng, b_lat, b_lng)

        results.append(
            BloodBankResponse(
                id=b["id"],
                name=b["name"],
                city=b["city"],
                area=b["area"],
                province=b["province"],
                phone=b["phone"],
                hours=b["hours"],
                latitude=b_lat,
                longitude=b_lng,
                services=b.get("services", []),
                distance_km=dist,
            )
        )

    if lat is not None and lng is not None:
        results.sort(key=lambda x: x.distance_km if x.distance_km is not None else 9999)

    return results
