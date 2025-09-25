"""
API 키 관리 시스템
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class APIKeyType(str, Enum):
    """API 키 타입"""
    READ_ONLY = "read_only"
    TRADE = "trade"
    ADMIN = "admin"
    SYSTEM = "system"

class APIKeyManager:
    """API 키 관리 클래스"""
    
    def __init__(self):
        self.key_prefix = "ak_"  # API Key prefix
        self.secret_length = 32
    
    def generate_api_key(self, user_id: str, key_type: APIKeyType, 
                        permissions: List[str], expires_days: Optional[int] = None) -> Dict[str, Any]:
        """API 키 생성"""
        # 키 ID 생성
        key_id = f"{self.key_prefix}{secrets.token_urlsafe(16)}"
        
        # 시크릿 생성
        secret = secrets.token_urlsafe(self.secret_length)
        
        # 해시된 시크릿 (저장용)
        hashed_secret = hashlib.sha256(secret.encode()).hexdigest()
        
        # 만료 시간 설정
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        api_key_data = {
            "key_id": key_id,
            "secret": secret,  # 클라이언트에게 전달할 원본
            "hashed_secret": hashed_secret,  # 데이터베이스에 저장할 해시
            "user_id": user_id,
            "key_type": key_type,
            "permissions": permissions,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "is_active": True,
            "last_used": None
        }
        
        logger.info(f"API key generated for user {user_id}, type: {key_type}")
        return api_key_data
    
    def verify_api_key(self, key_id: str, secret: str, stored_data: Dict[str, Any]) -> bool:
        """API 키 검증"""
        # 키가 활성화되어 있는지 확인
        if not stored_data.get("is_active", False):
            logger.warning(f"API key {key_id} is not active")
            return False
        
        # 만료 시간 확인
        expires_at = stored_data.get("expires_at")
        if expires_at and datetime.utcnow() > expires_at:
            logger.warning(f"API key {key_id} has expired")
            return False
        
        # 시크릿 검증
        hashed_secret = hashlib.sha256(secret.encode()).hexdigest()
        if hashed_secret != stored_data.get("hashed_secret"):
            logger.warning(f"Invalid secret for API key {key_id}")
            return False
        
        # 사용 시간 업데이트
        logger.info(f"API key {key_id} verified successfully")
        return True
    
    def revoke_api_key(self, key_id: str) -> bool:
        """API 키 비활성화"""
        logger.info(f"API key {key_id} revoked")
        return True
    
    def get_key_permissions(self, stored_data: Dict[str, Any]) -> List[str]:
        """API 키 권한 조회"""
        return stored_data.get("permissions", [])
    
    def check_permission(self, stored_data: Dict[str, Any], required_permission: str) -> bool:
        """특정 권한 확인"""
        permissions = self.get_key_permissions(stored_data)
        return required_permission in permissions
    
    def get_key_info(self, stored_data: Dict[str, Any]) -> Dict[str, Any]:
        """API 키 정보 조회 (시크릿 제외)"""
        return {
            "key_id": stored_data.get("key_id"),
            "user_id": stored_data.get("user_id"),
            "key_type": stored_data.get("key_type"),
            "permissions": stored_data.get("permissions", []),
            "created_at": stored_data.get("created_at"),
            "expires_at": stored_data.get("expires_at"),
            "is_active": stored_data.get("is_active", False),
            "last_used": stored_data.get("last_used")
        }

# 전역 API 키 관리자 인스턴스
api_key_manager = APIKeyManager()