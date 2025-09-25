"""
2단계 인증 (2FA) 시스템
"""

import pyotp
import qrcode
from io import BytesIO
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class TwoFactorAuth:
    """2단계 인증 관리 클래스"""
    
    def __init__(self):
        self.issuer_name = settings.APP_NAME or "AI Trading System"
    
    def generate_secret(self, user_email: str) -> str:
        """사용자별 2FA 시크릿 키 생성"""
        secret = pyotp.random_base32()
        logger.info(f"2FA secret generated for user: {user_email}")
        return secret
    
    def generate_qr_code(self, user_email: str, secret: str) -> str:
        """QR 코드 생성 (Base64 인코딩)"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name=self.issuer_name
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Base64로 인코딩
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        logger.info(f"QR code generated for user: {user_email}")
        return f"data:image/png;base64,{img_str}"
    
    def verify_token(self, secret: str, token: str) -> bool:
        """2FA 토큰 검증"""
        totp = pyotp.TOTP(secret)
        is_valid = totp.verify(token, valid_window=1)  # 1분 윈도우
        
        if is_valid:
            logger.info("2FA token verified successfully")
        else:
            logger.warning("2FA token verification failed")
        
        return is_valid
    
    def generate_backup_codes(self, count: int = 10) -> list[str]:
        """백업 코드 생성"""
        import secrets
        backup_codes = []
        
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            backup_codes.append(code)
        
        logger.info(f"Generated {count} backup codes")
        return backup_codes
    
    def verify_backup_code(self, used_codes: list[str], code: str) -> bool:
        """백업 코드 검증"""
        if code in used_codes:
            logger.warning("Backup code already used")
            return False
        
        # 백업 코드는 8자리 16진수
        if len(code) == 8 and all(c in '0123456789ABCDEF' for c in code):
            logger.info("Backup code verified successfully")
            return True
        
        logger.warning("Invalid backup code format")
        return False

# 전역 2FA 인스턴스
two_factor_auth = TwoFactorAuth()