# 구독 API 테스트
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock

from app.main import app
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionPlan
from app.services.subscription_service import SubscriptionService

@pytest.fixture
async def test_user(async_session: AsyncSession):
    """테스트용 사용자 생성"""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user

@pytest.fixture
async def test_subscription_plan(async_session: AsyncSession):
    """테스트용 구독 플랜 생성"""
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
    return plan

@pytest.fixture
async def test_subscription(async_session: AsyncSession, test_user: User, test_subscription_plan: SubscriptionPlan):
    """테스트용 구독 생성"""
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_subscription_plan.id,
        status="active",
        current_period_start="2024-01-01T00:00:00Z",
        current_period_end="2024-02-01T00:00:00Z",
        stripe_subscription_id="sub_test123",
        stripe_customer_id="cus_test123"
    )
    async_session.add(subscription)
    await async_session.commit()
    await async_session.refresh(subscription)
    return subscription

class TestSubscriptionPlans:
    """구독 플랜 테스트"""
    
    async def test_get_subscription_plans(self, client: AsyncClient):
        """구독 플랜 목록 조회 테스트"""
        response = await client.get("/api/v1/subscriptions/plans")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # 기본 플랜 확인
        plan_names = [plan["name"] for plan in data]
        assert "Basic Plan" in plan_names
        assert "Premium Plan" in plan_names
        assert "Pro Plan" in plan_names

class TestUserSubscriptions:
    """사용자 구독 테스트"""
    
    async def test_get_user_subscriptions_unauthorized(self, client: AsyncClient):
        """인증되지 않은 사용자의 구독 조회 테스트"""
        response = await client.get("/api/v1/subscriptions/")
        
        assert response.status_code == 401
    
    async def test_get_user_subscriptions_success(
        self, 
        client: AsyncClient, 
        test_user: User,
        test_subscription: Subscription
    ):
        """사용자 구독 조회 성공 테스트"""
        # 인증 토큰 생성 (실제로는 JWT 토큰을 생성해야 함)
        with patch("app.services.auth_service.get_current_user") as mock_auth:
            mock_auth.return_value = test_user
            
            response = await client.get("/api/v1/subscriptions/")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    async def test_get_active_subscription_unauthorized(self, client: AsyncClient):
        """인증되지 않은 사용자의 활성 구독 조회 테스트"""
        response = await client.get("/api/v1/subscriptions/active")
        
        assert response.status_code == 401
    
    async def test_get_active_subscription_success(
        self, 
        client: AsyncClient, 
        test_user: User,
        test_subscription: Subscription
    ):
        """활성 구독 조회 성공 테스트"""
        with patch("app.services.auth_service.get_current_user") as mock_auth:
            mock_auth.return_value = test_user
            
            response = await client.get("/api/v1/subscriptions/active")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "active"

class TestCreateSubscription:
    """구독 생성 테스트"""
    
    async def test_create_subscription_unauthorized(self, client: AsyncClient):
        """인증되지 않은 사용자의 구독 생성 테스트"""
        subscription_data = {
            "plan_id": "basic",
            "payment_method_id": "pm_test123",
            "billing_cycle": "monthly"
        }
        
        response = await client.post("/api/v1/subscriptions/", json=subscription_data)
        
        assert response.status_code == 401
    
    async def test_create_subscription_success(
        self, 
        client: AsyncClient, 
        test_user: User
    ):
        """구독 생성 성공 테스트"""
        subscription_data = {
            "plan_id": "basic",
            "payment_method_id": "pm_test123",
            "billing_cycle": "monthly"
        }
        
        with patch("app.services.auth_service.get_current_user") as mock_auth, \
             patch("app.services.subscription_service.SubscriptionService.create_subscription") as mock_create:
            
            mock_auth.return_value = test_user
            mock_create.return_value = {
                "id": "sub_test123",
                "user_id": str(test_user.id),
                "plan_id": "basic",
                "status": "active",
                "price": 29.99,
                "currency": "USD"
            }
            
            response = await client.post("/api/v1/subscriptions/", json=subscription_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["plan_id"] == "basic"
            assert data["status"] == "active"
    
    async def test_create_subscription_invalid_plan(
        self, 
        client: AsyncClient, 
        test_user: User
    ):
        """잘못된 플랜으로 구독 생성 테스트"""
        subscription_data = {
            "plan_id": "invalid_plan",
            "payment_method_id": "pm_test123",
            "billing_cycle": "monthly"
        }
        
        with patch("app.services.auth_service.get_current_user") as mock_auth:
            mock_auth.return_value = test_user
            
            response = await client.post("/api/v1/subscriptions/", json=subscription_data)
            
            assert response.status_code == 500  # 플랜을 찾을 수 없음
    
    async def test_create_subscription_invalid_billing_cycle(
        self, 
        client: AsyncClient, 
        test_user: User
    ):
        """잘못된 결제 주기로 구독 생성 테스트"""
        subscription_data = {
            "plan_id": "basic",
            "payment_method_id": "pm_test123",
            "billing_cycle": "invalid_cycle"
        }
        
        with patch("app.services.auth_service.get_current_user") as mock_auth:
            mock_auth.return_value = test_user
            
            response = await client.post("/api/v1/subscriptions/", json=subscription_data)
            
            assert response.status_code == 422  # 유효성 검사 실패

class TestUpdateSubscription:
    """구독 업데이트 테스트"""
    
    async def test_update_subscription_unauthorized(self, client: AsyncClient):
        """인증되지 않은 사용자의 구독 업데이트 테스트"""
        subscription_data = {
            "billing_cycle": "yearly"
        }
        
        response = await client.put("/api/v1/subscriptions/test_id", json=subscription_data)
        
        assert response.status_code == 401
    
    async def test_update_subscription_not_found(
        self, 
        client: AsyncClient, 
        test_user: User
    ):
        """존재하지 않는 구독 업데이트 테스트"""
        subscription_data = {
            "billing_cycle": "yearly"
        }
        
        with patch("app.services.auth_service.get_current_user") as mock_auth:
            mock_auth.return_value = test_user
            
            response = await client.put("/api/v1/subscriptions/nonexistent_id", json=subscription_data)
            
            assert response.status_code == 404

class TestCancelSubscription:
    """구독 취소 테스트"""
    
    async def test_cancel_subscription_unauthorized(self, client: AsyncClient):
        """인증되지 않은 사용자의 구독 취소 테스트"""
        response = await client.post("/api/v1/subscriptions/test_id/cancel")
        
        assert response.status_code == 401
    
    async def test_cancel_subscription_not_found(
        self, 
        client: AsyncClient, 
        test_user: User
    ):
        """존재하지 않는 구독 취소 테스트"""
        with patch("app.services.auth_service.get_current_user") as mock_auth:
            mock_auth.return_value = test_user
            
            response = await client.post("/api/v1/subscriptions/nonexistent_id/cancel")
            
            assert response.status_code == 404

class TestReactivateSubscription:
    """구독 재활성화 테스트"""
    
    async def test_reactivate_subscription_unauthorized(self, client: AsyncClient):
        """인증되지 않은 사용자의 구독 재활성화 테스트"""
        response = await client.post("/api/v1/subscriptions/test_id/reactivate")
        
        assert response.status_code == 401
    
    async def test_reactivate_subscription_not_found(
        self, 
        client: AsyncClient, 
        test_user: User
    ):
        """존재하지 않는 구독 재활성화 테스트"""
        with patch("app.services.auth_service.get_current_user") as mock_auth:
            mock_auth.return_value = test_user
            
            response = await client.post("/api/v1/subscriptions/nonexistent_id/reactivate")
            
            assert response.status_code == 404

class TestSubscriptionHistory:
    """구독 이력 테스트"""
    
    async def test_get_subscription_history_unauthorized(self, client: AsyncClient):
        """인증되지 않은 사용자의 구독 이력 조회 테스트"""
        response = await client.get("/api/v1/subscriptions/test_id/history")
        
        assert response.status_code == 401
    
    async def test_get_subscription_history_not_found(
        self, 
        client: AsyncClient, 
        test_user: User
    ):
        """존재하지 않는 구독의 이력 조회 테스트"""
        with patch("app.services.auth_service.get_current_user") as mock_auth:
            mock_auth.return_value = test_user
            
            response = await client.get("/api/v1/subscriptions/nonexistent_id/history")
            
            assert response.status_code == 404

class TestSubscriptionService:
    """구독 서비스 테스트"""
    
    async def test_get_available_plans(self):
        """사용 가능한 플랜 조회 테스트"""
        plans = await SubscriptionService.get_available_plans()
        
        assert isinstance(plans, list)
        assert len(plans) == 3  # Basic, Premium, Pro
        
        plan_names = [plan.name for plan in plans]
        assert "Basic Plan" in plan_names
        assert "Premium Plan" in plan_names
        assert "Pro Plan" in plan_names
    
    async def test_get_plan_by_id(self):
        """플랜 ID로 플랜 조회 테스트"""
        plan = await SubscriptionService.get_plan_by_id("basic")
        
        assert plan is not None
        assert plan.id == "basic"
        assert plan.name == "Basic Plan"
    
    async def test_get_plan_by_id_not_found(self):
        """존재하지 않는 플랜 ID로 조회 테스트"""
        plan = await SubscriptionService.get_plan_by_id("nonexistent")
        
        assert plan is None
