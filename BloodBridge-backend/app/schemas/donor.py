from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime, date

BloodGroupType = Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]


class StandbyDonorCreate(BaseModel):
    name: str = Field(..., min_length=2)
    phone: str = Field(..., description="Mobile number, e.g. 3019827140")
    blood_group: BloodGroupType
    city: str
    area: Optional[str] = None
    latitude: float
    longitude: float


class StandbyDonorResponse(BaseModel):
    id: str
    name: str
    phone: str
    blood_group: str
    city: str
    area: Optional[str] = None
    latitude: float
    longitude: float
    is_available: bool = True
    total_donations: int = 0
    distance_km: Optional[float] = None
    eta_mins: Optional[int] = None
    created_at: Optional[datetime] = None


class DonorMatchResult(BaseModel):
    matched: bool
    donor: Optional[StandbyDonorResponse] = None
    message: str
