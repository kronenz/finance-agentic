# 간단한 API 테스트
import asyncio
import aiohttp
import pytest
from datetime import datetime

class TestSimpleAPI:
    """간단한 API 테스트"""
    
    BASE_URL = "http://localhost:8000"
    TEST_USER_EMAIL = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
    TEST_USER_PASSWORD = "TestPassword123!"
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """헬스 체크 테스트"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/health") as response:
                assert response.status == 200
                data = await response.json()
                assert "status" in data
                assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_user_registration(self):
        """사용자 등록 테스트"""
        async with aiohttp.ClientSession() as session:
            register_data = {
                "first_name": "Test",
                "last_name": "User",
                "email": self.TEST_USER_EMAIL,
                "password": self.TEST_USER_PASSWORD,
                "agreeToTerms": True
            }
            
            async with session.post(
                f"{self.BASE_URL}/api/v1/auth/register",
                json=register_data
            ) as response:
                assert response.status in [201, 409]  # 409는 이미 존재하는 사용자
                data = await response.json()
                assert "message" in data
    
    @pytest.mark.asyncio
    async def test_user_login(self):
        """사용자 로그인 테스트"""
        async with aiohttp.ClientSession() as session:
            login_data = {
                "email": self.TEST_USER_EMAIL,
                "password": self.TEST_USER_PASSWORD
            }
            
            async with session.post(
                f"{self.BASE_URL}/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert "access_token" in data
                assert "token_type" in data
                return data["access_token"]
    
    @pytest.mark.asyncio
    async def test_ai_status_with_auth(self):
        """인증이 필요한 AI 상태 조회 테스트"""
        # 먼저 로그인하여 토큰 획득
        async with aiohttp.ClientSession() as session:
            login_data = {
                "email": self.TEST_USER_EMAIL,
                "password": self.TEST_USER_PASSWORD
            }
            
            async with session.post(
                f"{self.BASE_URL}/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data["access_token"]
                    
                    # 토큰을 사용하여 AI 상태 조회
                    headers = {"Authorization": f"Bearer {token}"}
                    async with session.get(
                        f"{self.BASE_URL}/api/v1/ai/status",
                        headers=headers
                    ) as ai_response:
                        assert ai_response.status == 200
                        ai_data = await ai_response.json()
                        assert "timestamp" in ai_data
                        assert "is_running" in ai_data
                else:
                    pytest.skip("Login failed, skipping authenticated test")
    
    @pytest.mark.asyncio
    async def test_trading_portfolio_with_auth(self):
        """인증이 필요한 거래 포트폴리오 조회 테스트"""
        # 먼저 로그인하여 토큰 획득
        async with aiohttp.ClientSession() as session:
            login_data = {
                "email": self.TEST_USER_EMAIL,
                "password": self.TEST_USER_PASSWORD
            }
            
            async with session.post(
                f"{self.BASE_URL}/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data["access_token"]
                    
                    # 토큰을 사용하여 포트폴리오 조회
                    headers = {"Authorization": f"Bearer {token}"}
                    async with session.get(
                        f"{self.BASE_URL}/api/v1/trading/portfolio",
                        headers=headers
                    ) as portfolio_response:
                        assert portfolio_response.status == 200
                        portfolio_data = await portfolio_response.json()
                        assert "total_value" in portfolio_data
                        assert "assets" in portfolio_data
                else:
                    pytest.skip("Login failed, skipping authenticated test")
    
    @pytest.mark.asyncio
    async def test_subscription_plans_with_auth(self):
        """인증이 필요한 구독 플랜 조회 테스트"""
        # 먼저 로그인하여 토큰 획득
        async with aiohttp.ClientSession() as session:
            login_data = {
                "email": self.TEST_USER_EMAIL,
                "password": self.TEST_USER_PASSWORD
            }
            
            async with session.post(
                f"{self.BASE_URL}/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data["access_token"]
                    
                    # 토큰을 사용하여 구독 플랜 조회
                    headers = {"Authorization": f"Bearer {token}"}
                    async with session.get(
                        f"{self.BASE_URL}/api/v1/subscriptions/plans",
                        headers=headers
                    ) as plans_response:
                        assert plans_response.status == 200
                        plans_data = await plans_response.json()
                        assert isinstance(plans_data, list)
                        if plans_data:
                            assert "id" in plans_data[0]
                            assert "name" in plans_data[0]
                            assert "price" in plans_data[0]
                else:
                    pytest.skip("Login failed, skipping authenticated test")
    
    @pytest.mark.asyncio
    async def test_monitoring_metrics_with_auth(self):
        """인증이 필요한 모니터링 메트릭 조회 테스트"""
        # 먼저 로그인하여 토큰 획득
        async with aiohttp.ClientSession() as session:
            login_data = {
                "email": self.TEST_USER_EMAIL,
                "password": self.TEST_USER_PASSWORD
            }
            
            async with session.post(
                f"{self.BASE_URL}/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data["access_token"]
                    
                    # 토큰을 사용하여 모니터링 메트릭 조회
                    headers = {"Authorization": f"Bearer {token}"}
                    async with session.get(
                        f"{self.BASE_URL}/api/v1/monitoring/metrics",
                        headers=headers
                    ) as metrics_response:
                        assert metrics_response.status == 200
                        metrics_data = await metrics_response.json()
                        assert "system" in metrics_data
                        assert "agents" in metrics_data
                        assert "database" in metrics_data
                        assert "redis" in metrics_data
                else:
                    pytest.skip("Login failed, skipping authenticated test")
    
    @pytest.mark.asyncio
    async def test_complete_user_journey(self):
        """완전한 사용자 여정 테스트"""
        async with aiohttp.ClientSession() as session:
            # 1. 사용자 등록
            register_data = {
                "first_name": "Test",
                "last_name": "User",
                "email": self.TEST_USER_EMAIL,
                "password": self.TEST_USER_PASSWORD,
                "agreeToTerms": True
            }
            
            async with session.post(
                f"{self.BASE_URL}/api/v1/auth/register",
                json=register_data
            ) as response:
                assert response.status in [201, 409]
            
            # 2. 로그인
            login_data = {
                "email": self.TEST_USER_EMAIL,
                "password": self.TEST_USER_PASSWORD
            }
            
            async with session.post(
                f"{self.BASE_URL}/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                assert response.status == 200
                data = await response.json()
                token = data["access_token"]
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # 3. AI 상태 확인
            async with session.get(
                f"{self.BASE_URL}/api/v1/ai/status",
                headers=headers
            ) as response:
                assert response.status == 200
            
            # 4. 포트폴리오 확인
            async with session.get(
                f"{self.BASE_URL}/api/v1/trading/portfolio",
                headers=headers
            ) as response:
                assert response.status == 200
            
            # 5. 구독 플랜 확인
            async with session.get(
                f"{self.BASE_URL}/api/v1/subscriptions/plans",
                headers=headers
            ) as response:
                assert response.status == 200
            
            # 6. 모니터링 메트릭 확인
            async with session.get(
                f"{self.BASE_URL}/api/v1/monitoring/metrics",
                headers=headers
            ) as response:
                assert response.status == 200
            
            print("✅ Complete user journey test passed!")
