from fastapi import Header, HTTPException
from app.core.config import settings

def verify_admin_token(x_token: str = Header(None)):
    if x_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=403)
