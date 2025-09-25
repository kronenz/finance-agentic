"""
세션 관리 시스템
"""

from datetime import datetime, timedelta
from fastapi import Request, Response, HTTPException, Depends
import uuid
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.session import Session as SessionModel

SESSION_COOKIE_NAME = "session_id"
SESSION_EXPIRATION_MINUTES = 60

async def create_session(user_id: int, db: Session = Depends(get_db)) -> str:
    """Create a new session."""
    session_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=SESSION_EXPIRATION_MINUTES)
    session = SessionModel(id=session_id, user_id=user_id, expires_at=expires_at)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session_id

async def get_session(request: Request, db: Session = Depends(get_db)) -> Optional[int]:
    """Get the session ID from the request."""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        return None
    
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session or session.expires_at < datetime.utcnow():
        return None
    
    return session.user_id

async def delete_session(response: Response, request: Request, db: Session = Depends(get_db)):
    """Delete the session."""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if session_id:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
        response.delete_cookie(SESSION_COOKIE_NAME)