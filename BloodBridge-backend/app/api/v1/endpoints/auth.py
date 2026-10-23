import uuid
import re
from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import SignupRequest, LoginRequest, AuthResponse, UserProfile
from app.core.supabase import get_supabase_client, get_supabase_admin_client, is_supabase_configured

router = APIRouter()


def sanitize_phone_to_email(phone: str) -> str:
    """Standardize Pakistani mobile phone number to an internal Supabase Auth email identity."""
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("92"):
        digits = digits[2:]
    if digits.startswith("0"):
        digits = digits[1:]
    return f"92{digits}@bloodbridge.internal"


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest):
    """
    Registers a new requester in Supabase Auth and saves their profile.
    Uses auto-confirmed internal email identity to bypass third-party SMS gateway requirements.
    """
    client = get_supabase_client()
    admin_client = get_supabase_admin_client()
    internal_email = sanitize_phone_to_email(payload.phone)

    if not is_supabase_configured() or not admin_client or not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase database is not configured. Please check your server environment.",
        )

    try:
        # Create user via Supabase Admin (auto-confirmed)
        auth_user = admin_client.auth.admin.create_user(
            {
                "email": internal_email,
                "password": payload.password,
                "email_confirm": True,
                "user_metadata": {
                    "name": payload.name,
                    "phone": payload.phone,
                    "city": payload.city or "Karachi",
                },
            }
        )
        user_id = auth_user.user.id

        # Insert or update in public.profiles table
        try:
            admin_client.table("profiles").upsert(
                {
                    "id": user_id,
                    "phone": payload.phone,
                    "name": payload.name,
                    "city": payload.city or "Karachi",
                }
            ).execute()
        except Exception as e:
            print(f"Profile creation warning: {e}")

        # Sign in to generate real JWT session token
        session = client.auth.sign_in_with_password(
            {
                "email": internal_email,
                "password": payload.password,
            }
        )

        return AuthResponse(
            access_token=session.session.access_token,
            user=UserProfile(
                id=user_id,
                phone=payload.phone,
                name=payload.name,
                city=payload.city or "Karachi",
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        err_msg = str(e)
        if (
            "already registered" in err_msg.lower()
            or "already exists" in err_msg.lower()
            or "already been registered" in err_msg.lower()
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This mobile number is already registered. Please switch to Sign In.",
            )
        # Strip any internal email wording so user only sees mobile number
        user_facing_msg = err_msg.replace("email address", "mobile number").replace("email", "mobile number")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration error: {user_facing_msg}",
        )


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    """
    Authenticates a requester using phone and password against Supabase Auth.
    Strictly validates credentials. Returns 401 if user does not exist or password is wrong.
    """
    client = get_supabase_client()
    admin_client = get_supabase_admin_client()
    internal_email = sanitize_phone_to_email(payload.phone)

    if not is_supabase_configured() or not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase database is not configured. Please check your server environment.",
        )

    try:
        session = client.auth.sign_in_with_password(
            {
                "email": internal_email,
                "password": payload.password,
            }
        )

        user_id = session.user.id
        name = session.user.user_metadata.get("name", "Requester")
        city = session.user.user_metadata.get("city", "Karachi")

        # Fetch latest profile from database if available
        if admin_client:
            try:
                p_res = admin_client.table("profiles").select("*").eq("id", user_id).single().execute()
                if p_res.data:
                    name = p_res.data.get("name", name)
                    city = p_res.data.get("city", city)
            except Exception:
                pass

        return AuthResponse(
            access_token=session.session.access_token,
            user=UserProfile(
                id=user_id,
                phone=payload.phone,
                name=name,
                city=city,
            ),
        )

    except Exception as e:
        # Strictly reject invalid login - do not fake login
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile number or password. If you don't have an account, please sign up first.",
        )
