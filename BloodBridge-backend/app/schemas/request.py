from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

BloodGroupType = Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
UrgencyType = Literal["routine", "urgent", "emergency"]
StatusType = Literal["searching", "donor_matched", "fulfilled", "cancelled"]


class HospitalInfo(BaseModel):
    name: str
    area: Optional[str] = None
    city: str
    latitude: float
    longitude: float


class BloodRequestCreate(BaseModel):
    blood_group: BloodGroupType
    blood_component: str = "Whole Blood"
    units_needed: int = Field(default=1, ge=1, le=20)
    urgency: UrgencyType = "emergency"
    hospital_name: str
    hospital_area: Optional[str] = None
    hospital_city: str
    hospital_latitude: float
    hospital_longitude: float
    contact_person: str
    contact_phone: str
    notes: Optional[str] = None


class BloodRequestResponse(BaseModel):
    id: str
    reference_code: str
    blood_group: str
    blood_component: str
    units_needed: int
    urgency: str
    hospital: HospitalInfo
    contact_person: str
    contact_phone: str
    notes: Optional[str] = None
    status: str
    matched_donor_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BloodRequestStatusUpdate(BaseModel):
    status: StatusType
    matched_donor_id: Optional[str] = None
