# 통합 테스트
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionPlan
from app.services.ai_service import ai_service
from app.services.cache_service import cache_service

@pytest.fixture
async def test_client():
    """테스트 클라이언트 생성"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_user_with_subscription(async_session: AsyncSession):
    """구독이 있는 테스트 사용자 생성"""
    # 사용자 생성
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    # 구독 플랜 생성
    plan = SubscriptionPlan(
        id="test_plan",
        name="Test Plan",
        display_name="Test Plan",
        description="Test subscription plan",
        price_monthly=29.99,
        price_yearly=299.99,
        features=["feature1", "feature2"],
        is_active=True
    )
    async_session.add(plan)
    await async_session.commit()
    await async_session.refresh(plan)
    
    # 구독 생성
    subscription = Subscription(
        user_id=user.id,
        plan_id=plan.id,
        status="active",
        current_period_start="2024-01-01T00:00:00Z",
        current_period_end="2024-02-01T00:00:00Z",
        stripe_subscription_id="sub_test123",
        stripe_customer_id="cus_test123"
    )
    async_session.add(subscription)
    await async_session.commit()
    await async_session.refresh(subscription)
    
    return user, subscription

class TestAuthenticationFlow:
    """인증 플로우 통합 테스트"""
    
    async def test_complete_auth_flow(self, test_client: AsyncClient):
        """완전한 인증 플로우 테스트"""
        # 1. 사용자 등록
        register_data = {
            "email": "integration@test.com",
            "password": "testpassword123",
            "first_name": "Integration",
            "last_name": "Test"
        }
        
        register_response = await test_client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == 200
        
        # 2. 사용자 로그인
        login_data = {
            "username": "integration@test.com",
            "password": "testpassword123"
        }
        
        login_response = await test_client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        assert "access_token" in token_data
        assert "token_type" in token_data
        
        # 3. 보호된 엔드포인트 접근
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        me_response = await test_client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        user_data = me_response.json()
        assert user_data["email"] == "integration@test.com"
        assert user_data["first_name"] == "Integration"

class TestSubscriptionFlow:
    """구독 플로우 통합 테스트"""
    
    async def test_complete_subscription_flow(self, test_client: AsyncClient, test_user_with_subscription):
        """완전한 구독 플로우 테스트"""
        user, subscription = test_user_with_subscription
        
        # 인증 토큰 생성 (실제로는 JWT 토큰을 생성해야 함)
        with patch("app.services.auth_service.get_current_user") as mock_auth:
            mock_auth.return_value = user
            
            # 1. 구독 플랜 조회
            plans_response = await test_client.get("/api/v1/subscriptions/plans")
            assert plans_response.status_code == 200
            
            plans_data = plans_response.json()
            assert len(plans_data) > 0
            assert "Basic Plan" in [plan["name"] for plan in plans_data]
            
            # 2. 사용자 구독 조회
            subscriptions_response = await test_client.get("/api/v1/subscriptions/")
            assert subscriptions_response.status_code == 200
            
            subscriptions_data = subscriptions_response.json()
            assert len(subscriptions_data) > 0
            assert subscriptions_data[0]["user_id"] == str(user.id)
            
            # 3. 활성 구독 조회
            active_response = await test_client.get("/api/v1/subscriptions/active")
            assert active_response.status_code == 200
            
            active_data = active_response.json()
            assert active_data["status"] == "active"
            assert active_data["user_id"] == str(user.id)

class TestAIFlow:
    """AI 기능 플로우 통합 테스트"""
    
    async def test_complete_ai_flow(self, test_client: AsyncClient, test_user_with_subscription):
        """완전한 AI 기능 플로우 테스트"""
        user, subscription = test_user_with_subscription
        
        with patch("app.services.auth_service.get_current_user") as mock_auth:
            mock_auth.return_value = user
            
            # 1. 시장 분석
            market_data = {
                "symbol": "BTCUSDT",
                "price_data": [
                    {"open": 50000, "high": 51000, "low": 49000, "close": 50500, "volume": 1000000}
                    for _ in range(100)
                ],
                "update_model": False
            }
            
            market_response = await test_client.post("/api/v1/ai/market/analyze", json=market_data)
            assert market_response.status_code == 200
            
            market_analysis = market_response.json()
            assert "regime" in market_analysis
            assert "confidence" in market_analysis
            assert "probabilities" in market_analysis
            
            # 2. 전략 추천
            strategy_response = await test_client.post("/api/v1/ai/strategies/recommend", json={})
            assert strategy_response.status_code == 200
            
            strategies = strategy_response.json()
            assert len(strategies) > 0
            assert "strategy_id" in strategies[0]
            assert "score" in strategies[0]
            
            # 3. 리스크 평가
            risk_data = {
                "market_data": {
                    "vix": 25,
                    "volatility": 0.15,
                    "trend": 0.3
                },
                "portfolio_data": {
                    "concentration": 0.3,
                    "leverage": 1.0,
                    "position_size": 0.1
                }
            }
            
            risk_response = await test_client.post("/api/v1/ai/risk/assess", json=risk_data)
            assert risk_response.status_code == 200
            
            risk_assessment = risk_response.json()
            assert "risk_level" in risk_assessment
            assert "total_risk_score" in risk_assessment
            assert "recommendations" in risk_assessment

class TestCacheIntegration:
    """캐시 통합 테스트"""
    
    async def test_cache_integration(self):
        """캐시 서비스 통합 테스트"""
        # 캐시 설정
        test_key = "test:cache:integration"
        test_value = {"test": "data", "timestamp": "2024-01-01T00:00:00Z"}
        
        # 캐시 저장
        result = await cache_service.set(test_key, test_value, ttl=60)
        assert result is True
        
        # 캐시 조회
        cached_value = await cache_service.get(test_key)
        assert cached_value == test_value
        
        # 캐시 존재 확인
        exists = await cache_service.exists(test_key)
        assert exists is True
        
        # 캐시 삭제
        deleted = await cache_service.delete(test_key)
        assert deleted is True
        
        # 삭제 후 조회
        cached_value_after_delete = await cache_service.get(test_key)
        assert cached_value_after_delete is None

class TestSecurityIntegration:
    """보안 통합 테스트"""
    
    async def test_rate_limiting(self, test_client: AsyncClient):
        """Rate limiting 테스트"""
        # 정상 요청
        response = await test_client.get("/api/v1/subscriptions/plans")
        assert response.status_code == 200
        
        # Rate limit 초과 시뮬레이션 (실제로는 더 많은 요청 필요)
        # 이 테스트는 실제 환경에서 더 정확하게 테스트해야 함
        pass
    
    async def test_security_headers(self, test_client: AsyncClient):
        """보안 헤더 테스트"""
        response = await test_client.get("/api/v1/subscriptions/plans")
        
        # 보안 헤더 확인
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"

class TestDatabaseIntegration:
    """데이터베이스 통합 테스트"""
    
    async def test_database_transactions(self, async_session: AsyncSession):
        """데이터베이스 트랜잭션 테스트"""
        # 트랜잭션 시작
        async with async_session.begin():
            # 사용자 생성
            user = User(
                email="transaction@test.com",
                hashed_password="hashed_password",
                is_active=True,
                is_verified=True
            )
            async_session.add(user)
            await async_session.flush()  # ID 생성
            
            # 구독 생성
            subscription = Subscription(
                user_id=user.id,
                plan_id="test_plan",
                status="active",
                current_period_start="2024-01-01T00:00:00Z",
                current_period_end="2024-02-01T00:00:00Z"
            )
            async_session.add(subscription)
            
            # 트랜잭션 커밋 (with 문에서 자동)
        
        # 데이터 확인
        result = await async_session.execute(
            select(User).where(User.email == "transaction@test.com")
        )
        user = result.scalar_one_or_none()
        assert user is not None
        
        result = await async_session.execute(
            select(Subscription).where(Subscription.user_id == user.id)
        )
        subscription = result.scalar_one_or_none()
        assert subscription is not None

class TestErrorHandling:
    """에러 처리 통합 테스트"""
    
    async def test_404_error_handling(self, test_client: AsyncClient):
        """404 에러 처리 테스트"""
        response = await test_client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    async def test_422_error_handling(self, test_client: AsyncClient):
        """422 에러 처리 테스트 (유효성 검사 실패)"""
        invalid_data = {
            "email": "invalid-email",  # 잘못된 이메일 형식
            "password": "123"  # 너무 짧은 비밀번호
        }
        
        response = await test_client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422
    
    async def test_500_error_handling(self, test_client: AsyncClient):
        """500 에러 처리 테스트"""
        # 잘못된 데이터로 500 에러 유발
        with patch("app.services.subscription_service.SubscriptionService.get_available_plans") as mock_plans:
            mock_plans.side_effect = Exception("Database connection failed")
            
            response = await test_client.get("/api/v1/subscriptions/plans")
            assert response.status_code == 500

class TestPerformanceIntegration:
    """성능 통합 테스트"""
    
    async def test_concurrent_requests(self, test_client: AsyncClient):
        """동시 요청 테스트"""
        # 동시에 여러 요청 보내기
        tasks = []
        for i in range(10):
            task = test_client.get("/api/v1/subscriptions/plans")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        # 모든 요청이 성공해야 함
        for response in responses:
            assert response.status_code == 200
    
    async def test_cache_performance(self):
        """캐시 성능 테스트"""
        import time
        
        # 캐시 없이 실행
        start_time = time.time()
        for _ in range(100):
            await cache_service.get("nonexistent_key")
        no_cache_time = time.time() - start_time
        
        # 캐시 설정
        await cache_service.set("performance_test", {"data": "test"}, ttl=60)
        
        # 캐시 있이 실행
        start_time = time.time()
        for _ in range(100):
            await cache_service.get("performance_test")
        cache_time = time.time() - start_time
        
        # 캐시가 더 빨라야 함
        assert cache_time < no_cache_time

# 통합 테스트 실행을 위한 헬퍼 함수
async def run_integration_tests():
    """통합 테스트 실행"""
    print("Running integration tests...")
    
    # 테스트 실행
    pytest.main(["-v", "tests/test_integration.py"])
    
    print("Integration tests completed!")

if __name__ == "__main__":
    asyncio.run(run_integration_tests())
