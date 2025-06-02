from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.v18.main import basic
from pydantic import BaseModel
from app.core.config import get_settings

class IAccount(BaseModel):
    url: str
    db: str
    username: str
    password: str
    
router = APIRouter(
    prefix="/api/v18",
    tags=["Base"]
)

@router.get("/")
async def test ():
    print('Start test')
    return {"message": "Service is running"}

@router.post("/login")
async def login(account: IAccount):
    connect = basic(account.url, account.db, account.username, account.password)
    await connect.login()
    return {"message": "Login successful", "version": connect.version, "uid": connect.uid }