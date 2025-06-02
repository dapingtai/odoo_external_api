from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
import httpx
import json
from app.core.config import get_settings
from app.infra.logging.console_logger import ConsoleLogger

router = APIRouter(
    prefix="/middleware/oauth",
    tags=["MiddleWare"]
)

@router.get("/callback")
async def get_sso_token(code: str, database: str, oauth_provider_id: int, redirect_uri: str = "/odoo"):
    oauth_logger = ConsoleLogger('Login Info')

    params = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": get_settings().SSO_CLIENT_ID,
        "client_secret": get_settings().SSO_CLIENT_SECRET,
        "redirect_uri": get_settings().SSO_CALLBACK_URL
    }

    oauth_logger.log_info(params)

    # Get Access token
    token_data = None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(get_settings().SSO_TOKEN_URL, data=params)
            response.raise_for_status()
            token_data = response.json()
    except httpx.HTTPStatusError as http_e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid SSO token: {str(http_e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    # Pass token to odoo
    state = f"{json.dumps({ "d": database, "p": oauth_provider_id, "r": redirect_uri })}"
    oauth_logger.log_info(state)
    return RedirectResponse(url=get_settings().SSO_CALLBACK_URL + f"?access_token={token_data['access_token']}&state={state}", status_code=status.HTTP_302_FOUND)