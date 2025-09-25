# E2E 테스트: 사용자 가입 및 거래 시나리오
import pytest
import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any

class TestUserRegistrationAndTrading:
    """사용자 가입 및 거래 E2E 테스트"""
    
    BASE_URL = "http://localhost:8000"
    TEST_USER_EMAIL = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
    TEST_USER_PASSWORD = "TestPassword123!"
    TEST_USER_FIRST_NAME = "Test"
    TEST_USER_LAST_NAME = "User"
    
    @pytest.fixture
    def http_session(self):
        """HTTP 세션 생성"""
        return aiohttp.ClientSession()
    
    @pytest.fixture
    async def auth_token(self, http_session):
        """인증 토큰 획득"""
        # 1. 사용자 등록
        register_data = {
            "first_name": self.TEST_USER_FIRST_NAME,
            "last_name": self.TEST_USER_LAST_NAME,
            "email": self.TEST_USER_EMAIL,
            "password": self.TEST_USER_PASSWORD,
            "agreeToTerms": True
        }
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/auth/register",
            json=register_data
        ) as response:
            assert response.status == 201
            register_result = await response.json()
            assert "message" in register_result
        
        # 2. 로그인
        login_data = {
            "email": self.TEST_USER_EMAIL,
            "password": self.TEST_USER_PASSWORD
        }
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/auth/login",
            data=login_data
        ) as response:
            assert response.status == 200
            login_result = await response.json()
            assert "access_token" in login_result
            return login_result["access_token"]
    
    @pytest.mark.asyncio
    async def test_user_registration_and_login(self, http_session):
        """사용자 등록 및 로그인 테스트"""
        # 1. 사용자 등록
        register_data = {
            "first_name": self.TEST_USER_FIRST_NAME,
            "last_name": self.TEST_USER_LAST_NAME,
            "email": self.TEST_USER_EMAIL,
            "password": self.TEST_USER_PASSWORD,
            "agreeToTerms": True
        }
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/auth/register",
            json=register_data
        ) as response:
            assert response.status == 201
            result = await response.json()
            assert "message" in result
            assert "User registered successfully" in result["message"]
        
        # 2. 로그인
        login_data = {
            "email": self.TEST_USER_EMAIL,
            "password": self.TEST_USER_PASSWORD
        }
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/auth/login",
            data=login_data
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert "access_token" in result
            assert "token_type" in result
            assert result["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_ai_system_status_check(self, http_session, auth_token):
        """AI 시스템 상태 확인 테스트"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with http_session.get(
            f"{self.BASE_URL}/api/v1/ai/status",
            headers=headers
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert "timestamp" in result
            assert "is_running" in result
            assert "agents" in result
            assert "redis_status" in result
    
    @pytest.mark.asyncio
    async def test_data_collection_start(self, http_session, auth_token):
        """데이터 수집 시작 테스트"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        data = {
            "symbols": ["BTC/USDT", "ETH/USDT"],
            "exchanges": ["binance", "coinbase"]
        }
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/ai/data/collect",
            headers=headers,
            json=data
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert "status" in result
            assert "message" in result
            assert result["status"] == "started"
    
    @pytest.mark.asyncio
    async def test_trading_signal_generation(self, http_session, auth_token):
        """거래 신호 생성 테스트"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        data = {
            "symbols": ["BTC/USDT", "ETH/USDT"],
            "timeframe": "1h"
        }
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/ai/signals/generate",
            headers=headers,
            json=data
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert "signals" in result
            assert "timestamp" in result
            assert len(result["signals"]) == 2
            
            for signal in result["signals"]:
                assert "symbol" in signal
                assert "signal" in signal
                assert "confidence" in signal
                assert "price" in signal
                assert "timestamp" in signal
                assert "reasoning" in signal
                assert signal["signal"] in ["BUY", "SELL", "HOLD"]
                assert 0 <= signal["confidence"] <= 1
    
    @pytest.mark.asyncio
    async def test_order_creation_and_management(self, http_session, auth_token):
        """주문 생성 및 관리 테스트"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # 1. 주문 생성
        order_data = {
            "symbol": "BTC/USDT",
            "side": "BUY",
            "type": "LIMIT",
            "quantity": 0.1,
            "price": 50000.0
        }
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/trading/orders",
            headers=headers,
            json=order_data
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert "order" in result
            assert "message" in result
            assert "timestamp" in result
            
            order = result["order"]
            assert "order_id" in order
            assert "symbol" in order
            assert "side" in order
            assert "type" in order
            assert "quantity" in order
            assert "price" in order
            assert "status" in order
            
            order_id = order["order_id"]
        
        # 2. 주문 조회
        async with http_session.get(
            f"{self.BASE_URL}/api/v1/trading/orders/{order_id}",
            headers=headers
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert "order" in result
            assert result["order"]["order_id"] == order_id
        
        # 3. 주문 목록 조회
        async with http_session.get(
            f"{self.BASE_URL}/api/v1/trading/orders",
            headers=headers
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert isinstance(result, list)
            assert len(result) >= 1
        
        # 4. 주문 취소
        async with http_session.delete(
            f"{self.BASE_URL}/api/v1/trading/orders/{order_id}",
            headers=headers
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert "message" in result
            assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_portfolio_management(self, http_session, auth_token):
        """포트폴리오 관리 테스트"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with http_session.get(
            f"{self.BASE_URL}/api/v1/trading/portfolio",
            headers=headers
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert "total_value" in result
            assert "total_pnl" in result
            assert "total_pnl_percentage" in result
            assert "assets" in result
            assert "timestamp" in result
            assert isinstance(result["assets"], list)
    
    @pytest.mark.asyncio
    async def test_subscription_management(self, http_session, auth_token):
        """구독 관리 테스트"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # 1. 구독 플랜 조회
        async with http_session.get(
            f"{self.BASE_URL}/api/v1/subscriptions/plans",
            headers=headers
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert isinstance(result, list)
            assert len(result) >= 1
            
            for plan in result:
                assert "id" in plan
                assert "name" in plan
                assert "price" in plan
                assert "billing_cycle" in plan
                assert "features" in plan
        
        # 2. 구독 생성
        subscription_data = {
            "plan_id": "premium",
            "billing_cycle": "monthly"
        }
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/subscriptions",
            headers=headers,
            json=subscription_data
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert "subscription" in result
            assert "message" in result
            assert "timestamp" in result
        
        # 3. 활성 구독 조회
        async with http_session.get(
            f"{self.BASE_URL}/api/v1/subscriptions/active",
            headers=headers
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert "subscription" in result
            assert "plan" in result
            assert "status" in result
            assert "created_at" in result
    
    @pytest.mark.asyncio
    async def test_monitoring_system(self, http_session, auth_token):
        """모니터링 시스템 테스트"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # 1. 시스템 메트릭 조회
        async with http_session.get(
            f"{self.BASE_URL}/api/v1/monitoring/metrics",
            headers=headers
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert "system" in result
            assert "agents" in result
            assert "database" in result
            assert "redis" in result
            assert "timestamp" in result
        
        # 2. 시스템 헬스 체크
        async with http_session.get(
            f"{self.BASE_URL}/api/v1/monitoring/health",
            headers=headers
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert "overall_status" in result
            assert "timestamp" in result
            assert "components" in result
        
        # 3. 알림 목록 조회
        async with http_session.get(
            f"{self.BASE_URL}/api/v1/monitoring/alerts",
            headers=headers
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_logout(self, http_session, auth_token):
        """로그아웃 테스트"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/auth/logout",
            headers=headers
        ) as response:
            assert response.status == 200
            result = await response.json()
            assert "message" in result
            assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_complete_user_journey(self, http_session):
        """완전한 사용자 여정 테스트"""
        # 1. 사용자 등록
        register_data = {
            "first_name": self.TEST_USER_FIRST_NAME,
            "last_name": self.TEST_USER_LAST_NAME,
            "email": self.TEST_USER_EMAIL,
            "password": self.TEST_USER_PASSWORD,
            "agreeToTerms": True
        }
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/auth/register",
            json=register_data
        ) as response:
            assert response.status == 201
        
        # 2. 로그인
        login_data = {
            "email": self.TEST_USER_EMAIL,
            "password": self.TEST_USER_PASSWORD
        }
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/auth/login",
            data=login_data
        ) as response:
            assert response.status == 200
            login_result = await response.json()
            auth_token = login_result["access_token"]
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # 3. AI 시스템 상태 확인
        async with http_session.get(
            f"{self.BASE_URL}/api/v1/ai/status",
            headers=headers
        ) as response:
            assert response.status == 200
        
        # 4. 데이터 수집 시작
        data = {
            "symbols": ["BTC/USDT"],
            "exchanges": ["binance"]
        }
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/ai/data/collect",
            headers=headers,
            json=data
        ) as response:
            assert response.status == 200
        
        # 5. 거래 신호 생성
        signal_data = {
            "symbols": ["BTC/USDT"],
            "timeframe": "1h"
        }
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/ai/signals/generate",
            headers=headers,
            json=signal_data
        ) as response:
            assert response.status == 200
        
        # 6. 주문 생성
        order_data = {
            "symbol": "BTC/USDT",
            "side": "BUY",
            "type": "LIMIT",
            "quantity": 0.1,
            "price": 50000.0
        }
        
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/trading/orders",
            headers=headers,
            json=order_data
        ) as response:
            assert response.status == 200
        
        # 7. 포트폴리오 확인
        async with http_session.get(
            f"{self.BASE_URL}/api/v1/trading/portfolio",
            headers=headers
        ) as response:
            assert response.status == 200
        
        # 8. 로그아웃
        async with http_session.post(
            f"{self.BASE_URL}/api/v1/auth/logout",
            headers=headers
        ) as response:
            assert response.status == 200
