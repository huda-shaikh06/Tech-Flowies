from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "BloodBridge API"
    APP_ENV: str = "development"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]

    # Supabase Configuration (supports both naming styles)
    SUPABASE_URL: str = "https://placeholder.supabase.co"
    SUPABASE_ANON_KEY: str = "placeholder-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "placeholder-service-role-key"
    SUPABASE_PUBLISHABLE_KEY: Union[str, None] = None
    SUPABASE_SECRET_KEY: Union[str, None] = None
    SUPABASE_JWKS_URL: Union[str, None] = None

    @property
    def effective_anon_key(self) -> str:
        return self.SUPABASE_PUBLISHABLE_KEY or self.SUPABASE_ANON_KEY

    @property
    def effective_service_role_key(self) -> str:
        return self.SUPABASE_SECRET_KEY or self.SUPABASE_SERVICE_ROLE_KEY or self.effective_anon_key

    # WhatsApp API (Optional)
    WHATSAPP_API_URL: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""


settings = Settings()
