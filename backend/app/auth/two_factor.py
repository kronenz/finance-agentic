"""
Two-factor authentication.
"""
import pyotp
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User

def generate_2fa_secret(db: Session, user: User) -> str:
    """Generate a new 2FA secret and save it to the user."""
    secret = pyotp.random_base32()
    user.two_factor_secret = secret
    db.commit()
    return secret

def verify_2fa_code(user: User, code: str) -> bool:
    """Verify a 2FA code."""
    if not user.two_factor_secret:
        raise HTTPException(status_code=400, detail="2FA not enabled")
    
    totp = pyotp.TOTP(user.two_factor_secret)
    if not totp.verify(code):
        raise HTTPException(status_code=400, detail="Invalid 2FA code")
    
    return True
