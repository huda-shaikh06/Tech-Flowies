from fastapi import APIRouter
from app.api.v1.endpoints import auth, requests, donors, blood_banks, whatsapp

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(requests.router, prefix="/requests", tags=["Blood Requests"])
api_router.include_router(donors.router, prefix="/donors", tags=["Standby Donors"])
api_router.include_router(blood_banks.router, prefix="/blood-banks", tags=["Hospital Blood Banks"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp Dispatch & Simulation"])
