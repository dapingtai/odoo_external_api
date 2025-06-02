from fastapi import FastAPI, APIRouter, Request, Response, HTTPException, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel
import jwt
import time
import httpx
from typing import Optional
from app.core.config import get_settings

router = APIRouter(
    prefix=get_settings().BASE_URL + "/oauth",
    tags=["OAuth Provider"]
)

settings = get_settings()

# Models
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    id_token: str

class OAuthProvider:
    def __init__(self):
        self.clients = {}  # Store registered OAuth clients
        self.auth_codes = {}  # Store temporary authorization codes and tokens

    def register_client(self, client_id: str, client_secret: str, redirect_uri: str):
        """Register a new OAuth client application"""
        self.clients[client_id] = {
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }
        
    def cleanup_expired_codes(self):
        """Remove expired authorization codes"""
        current_time = time.time()
        expired_codes = [
            code for code, data in self.auth_codes.items()
            if data.get('expires', 0) < current_time
        ]
        for code in expired_codes:
            self.auth_codes.pop(code, None)

oauth_provider = OAuthProvider()

# Endpoints
@router.post("/register")
async def register_client(client_id: str, client_secret: str, redirect_uri: str):
    """Register a new OAuth client"""
    oauth_provider.register_client(client_id, client_secret, redirect_uri)
    return {"message": "Client registered successfully"}

@router.get("/authorize")
async def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: Optional[str] = None,
    state: Optional[str] = None
):
    """Authorization endpoint that redirects to SSO provider"""
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Invalid response type")
    
    if client_id not in oauth_provider.clients:
        raise HTTPException(status_code=400, detail="Invalid client ID")
    
    # Store the client's redirect URI and state for later use
    oauth_provider.auth_codes[state or secrets.token_urlsafe(32)] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "expires": time.time() + 600  # 10 minutes expiration
    }

    # Construct SSO provider authorization URL
    params = {
        "response_type": "code",
        "client_id": settings.SSO_CLIENT_ID,
        "redirect_uri": settings.SSO_CALLBACK_URL,
        "state": state or "",
        "scope": scope or "openid profile email"
    }
    
    # Redirect to SSO provider's authorization endpoint
    authorization_url = f"{settings.SSO_AUTHORIZE_URL}?{'&'.join(f'{k}={v}' for k, v in params.items() if v)}"
    
    return Response(
        status_code=302,
        headers={"Location": authorization_url}
    )

@router.post("/token")
async def token(
    grant_type: str,
    code: str,
    redirect_uri: str,
    client_id: str,
    client_secret: str
):
    """Token endpoint for OAuth 2.0 flow"""
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail="Invalid grant type")

    if code not in oauth_provider.auth_codes:
        raise HTTPException(status_code=400, detail="Invalid authorization code")

    auth_code_data = oauth_provider.auth_codes[code]
    if auth_code_data["client_id"] != client_id:
        raise HTTPException(status_code=400, detail="Invalid client")

    # Generate tokens
    expires_in = Config.TOKEN_EXPIRE_MINUTES * 60
    exp_timestamp = int(time.time()) + expires_in

    access_token = jwt.encode(
        {
            "sub": client_id,
            "exp": exp_timestamp
        },
        Config.OPENID_SECRET,
        algorithm="HS256"
    )

    id_token = jwt.encode(
        {
            "sub": client_id,
            "iss": "your-domain",
            "aud": client_id,
            "exp": exp_timestamp,
            "iat": int(time.time())
        },
        Config.OPENID_SECRET,
        algorithm="HS256"
    )

    # Remove used authorization code
    del oauth_provider.auth_codes[code]

    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=expires_in,
        id_token=id_token
    )

@router.get("/callback")
async def callback(code: str, state: Optional[str] = None):
    """SSO callback handler that processes the SSO callback and redirects to client application"""
    try:
        # Exchange authorization code for access token with SSO provider
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                settings.SSO_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.SSO_CLIENT_ID,
                    "client_secret": settings.SSO_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.SSO_CALLBACK_URL
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to exchange authorization code with SSO provider"
                )
            
            sso_token_data = token_response.json()
            
            # Get user info from SSO provider
            userinfo_response = await client.get(
                settings.SSO_USERINFO_URL,
                headers={"Authorization": f"Bearer {sso_token_data['access_token']}"}
            )
            
            if userinfo_response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to get user info from SSO provider"
                )
            
            user_info = userinfo_response.json()
        
        # Generate new OpenID token
        openid_token = jwt.encode(
            {
                "sub": user_info.get("sub", f"user_{code[:8]}"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "iss": settings.OPENID_ISSUER,
                "aud": settings.SSO_CLIENT_ID,
                "iat": int(time.time()),
                "exp": int(time.time()) + settings.OPENID_TOKEN_EXPIRE_MINUTES * 60
            },
            settings.OPENID_SECRET_KEY,
            algorithm="HS256"
        )

        # Get the original client's redirect URI
        if not state or state not in oauth_provider.auth_codes:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired state parameter"
            )
        
        client_data = oauth_provider.auth_codes[state]
        if time.time() > client_data['expires']:
            del oauth_provider.auth_codes[state]
            raise HTTPException(
                status_code=400,
                detail="Authorization request has expired"
            )
            
        # Generate a new authorization code for the client
        client_auth_code = jwt.encode(
            {
                "sub": user_info.get("sub", f"user_{code[:8]}"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "exp": int(time.time()) + 600,  # 10 minutes expiration
                "original_state": state
            },
            settings.OPENID_SECRET_KEY,
            algorithm="HS256"
        )
        
        # Store the SSO tokens and user info for later use
        oauth_provider.auth_codes[client_auth_code] = {
            "sso_token": sso_token_data,
            "user_info": user_info,
            "client_id": client_data["client_id"],
            "expires": int(time.time()) + 600
        }
        
        # Redirect back to client application
        redirect_url = f"{client_data['redirect_uri']}?code={client_auth_code}"
        if state:
            redirect_url += f"&state={state}"
            
        return Response(
            status_code=302,
            headers={"Location": redirect_url}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process SSO callback: {str(e)}"
        )