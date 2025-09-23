"""
OpenAPI/Swagger 설정 및 커스터마이징
"""

from fastapi.openapi.utils import get_openapi
from app.core.config import settings

def custom_openapi(app):
    """커스텀 OpenAPI 스키마 생성"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Crypto Trading Subscription Service API",
        version="2.0.0",
        description="""
        ## Phase 2 개인형 구독 서비스 API
        
        이 API는 암호화폐 자동화 거래 구독 서비스를 위한 RESTful API입니다.
        
        ### 주요 기능
        - **사용자 인증**: JWT 기반 인증 및 권한 관리
        - **구독 관리**: 구독 플랜 선택, 결제, 취소
        - **거래 기능**: 자동화된 거래 전략 실행
        - **AI 분석**: 개인화된 시장 분석 및 추천
        
        ### 인증
        대부분의 엔드포인트는 JWT 토큰을 통한 인증이 필요합니다.
        Authorization 헤더에 `Bearer <token>` 형식으로 토큰을 포함해주세요.
        
        ### 에러 처리
        API는 표준 HTTP 상태 코드를 사용합니다:
        - 200: 성공
        - 400: 잘못된 요청
        - 401: 인증 실패
        - 403: 권한 없음
        - 404: 리소스 없음
        - 500: 서버 오류
        """,
        routes=app.routes,
        servers=[
            {
                "url": "http://localhost:8000",
                "description": "개발 서버"
            },
            {
                "url": "https://api.crypto-trading.com",
                "description": "프로덕션 서버"
            }
        ]
    )
    
    # 커스텀 태그 추가
    openapi_schema["tags"] = [
        {
            "name": "authentication",
            "description": "사용자 인증 및 권한 관리"
        },
        {
            "name": "subscriptions",
            "description": "구독 관리 및 결제"
        },
        {
            "name": "trading",
            "description": "거래 전략 및 실행"
        },
        {
            "name": "dashboard",
            "description": "대시보드 및 분석"
        },
        {
            "name": "admin",
            "description": "관리자 기능"
        }
    ]
    
    # 보안 스키마 추가
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT 토큰을 사용한 인증"
        }
    }
    
    # 전역 보안 적용
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema