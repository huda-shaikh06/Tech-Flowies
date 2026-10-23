import logging
from typing import Optional
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

_supabase_client: Optional[Client] = None
_supabase_admin_client: Optional[Client] = None


def is_supabase_configured() -> bool:
    """Checks whether valid Supabase credentials have been configured."""
    key = settings.effective_anon_key
    return (
        bool(settings.SUPABASE_URL)
        and "placeholder" not in settings.SUPABASE_URL
        and bool(key)
        and "placeholder" not in key
    )


def get_supabase_client() -> Optional[Client]:
    """Returns singleton Supabase client using ANON / PUBLISHABLE key."""
    global _supabase_client
    if not is_supabase_configured():
        return None

    if _supabase_client is None:
        try:
            _supabase_client = create_client(
                settings.SUPABASE_URL,
                settings.effective_anon_key,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            return None

    return _supabase_client


def get_supabase_admin_client() -> Optional[Client]:
    """Returns singleton Supabase client using SERVICE ROLE / SECRET key for privileged operations."""
    global _supabase_admin_client
    if not is_supabase_configured():
        return None

    if _supabase_admin_client is None:
        try:
            _supabase_admin_client = create_client(
                settings.SUPABASE_URL,
                settings.effective_service_role_key,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Supabase admin client: {e}")
            return None

    return _supabase_admin_client
