from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    ENV: str = "example"
    BASE_URL: str="/dev"
    APP_NAME: str = "Odoo External API"
    APP_AUTHOR: str = "Hung Chang"
    APP_VERSION: str = "0.0.1"
    APP_DESCRIPTION: str = "Odoo 外部接口服務器"

    # SSO Configuration
    SSO_CLIENT_ID: str = "your-sso-client-id"
    SSO_CLIENT_SECRET: str = "your-sso-client-secret"
    SSO_AUTHORIZE_URL: str = "https://your-sso-provider/oauth/authorize"
    SSO_TOKEN_URL: str = "https://your-sso-provider/oauth/token"
    SSO_USERINFO_URL: str = "https://your-sso-provider/oauth/userinfo"
    SSO_CALLBACK_URL: str = "http://your-domain/oauth/callback"
    
    # OpenID Configuration
    OPENID_SECRET_KEY: str = "your-openid-secret-key"
    OPENID_ISSUER: str = "http://your-domain"
    OPENID_TOKEN_EXPIRE_MINUTES: int = 80

    model_config = SettingsConfigDict(env_file=".env.example", env_file_encoding="utf-8")

# @lru_cache()
def get_settings():
    return Settings()