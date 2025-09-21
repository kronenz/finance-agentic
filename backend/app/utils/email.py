"""
이메일 전송 유틸리티
"""

import asyncio
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings

class EmailService:
    """이메일 서비스 클래스"""
    
    def __init__(self):
        self.sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    
    async def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """이메일 전송"""
        try:
            message = Mail(
                from_email=settings.FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            response = self.sg.send(message)
            return response.status_code == 202
        except Exception as e:
            print(f"이메일 전송 실패: {e}")
            return False

# 전역 이메일 서비스 인스턴스
email_service = EmailService()

async def send_verification_email(email: str, token: str) -> bool:
    """이메일 인증 이메일 전송"""
    subject = "이메일 인증을 완료해주세요"
    html_content = f"""
    <html>
    <body>
        <h2>이메일 인증</h2>
        <p>안녕하세요! 계정 생성을 완료하려면 아래 링크를 클릭해주세요.</p>
        <p><a href="{settings.FRONTEND_URL}/verify-email?token={token}">이메일 인증하기</a></p>
        <p>링크는 24시간 후에 만료됩니다.</p>
        <p>만약 이 이메일을 요청하지 않으셨다면 무시해주세요.</p>
    </body>
    </html>
    """
    
    return await email_service.send_email(email, subject, html_content)

async def send_password_reset_email(email: str, token: str) -> bool:
    """비밀번호 재설정 이메일 전송"""
    subject = "비밀번호 재설정"
    html_content = f"""
    <html>
    <body>
        <h2>비밀번호 재설정</h2>
        <p>비밀번호 재설정을 요청하셨습니다. 아래 링크를 클릭하여 새 비밀번호를 설정해주세요.</p>
        <p><a href="{settings.FRONTEND_URL}/reset-password?token={token}">비밀번호 재설정하기</a></p>
        <p>링크는 1시간 후에 만료됩니다.</p>
        <p>만약 이 이메일을 요청하지 않으셨다면 무시해주세요.</p>
    </body>
    </html>
    """
    
    return await email_service.send_email(email, subject, html_content)

async def send_welcome_email(email: str, first_name: str) -> bool:
    """환영 이메일 전송"""
    subject = "Crypto Trading 서비스에 오신 것을 환영합니다!"
    html_content = f"""
    <html>
    <body>
        <h2>환영합니다, {first_name}님!</h2>
        <p>Crypto Trading 서비스에 가입해주셔서 감사합니다.</p>
        <p>이제 다음과 같은 기능을 이용하실 수 있습니다:</p>
        <ul>
            <li>자동화된 거래 전략</li>
            <li>실시간 시장 분석</li>
            <li>개인화된 투자 인사이트</li>
        </ul>
        <p>서비스를 시작하려면 <a href="{settings.FRONTEND_URL}/dashboard">대시보드</a>로 이동해주세요.</p>
    </body>
    </html>
    """
    
    return await email_service.send_email(email, subject, html_content)

async def send_subscription_confirmation(email: str, plan_name: str) -> bool:
    """구독 확인 이메일 전송"""
    subject = f"{plan_name} 플랜 구독이 완료되었습니다"
    html_content = f"""
    <html>
    <body>
        <h2>구독 완료</h2>
        <p>{plan_name} 플랜 구독이 성공적으로 완료되었습니다.</p>
        <p>이제 프리미엄 기능을 이용하실 수 있습니다.</p>
        <p><a href="{settings.FRONTEND_URL}/dashboard">대시보드로 이동</a></p>
    </body>
    </html>
    """
    
    return await email_service.send_email(email, subject, html_content)
