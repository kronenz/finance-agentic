"""
데이터베이스 모델 테스트
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserSocialLogin, UserProfile
from app.models.subscription import SubscriptionPlan, Subscription, Payment
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate

class TestUserModel:
    """사용자 모델 테스트 클래스"""
    
    async def test_create_user(self, db_session: AsyncSession):
        """사용자 생성 테스트"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.email_verified is False
    
    async def test_user_relationships(self, db_session: AsyncSession):
        """사용자 관계 테스트"""
        # 사용자 생성
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # 소셜 로그인 생성
        social_login = UserSocialLogin(
            user_id=user.id,
            provider="google",
            provider_id="google_123"
        )
        db_session.add(social_login)
        await db_session.commit()
        
        # 프로필 생성
        profile = UserProfile(
            user_id=user.id,
            risk_tolerance="medium",
            trading_experience="intermediate"
        )
        db_session.add(profile)
        await db_session.commit()
        
        # 관계 확인
        assert len(user.social_logins) == 1
        assert user.social_logins[0].provider == "google"
        assert user.profile.risk_tolerance == "medium"
    
    async def test_user_unique_email(self, db_session: AsyncSession):
        """사용자 이메일 유니크 제약 테스트"""
        # 첫 번째 사용자 생성
        user1 = User(
            email="test@example.com",
            password_hash="hashed_password1",
            first_name="Test1",
            last_name="User1"
        )
        db_session.add(user1)
        await db_session.commit()
        
        # 같은 이메일로 두 번째 사용자 생성 시도
        user2 = User(
            email="test@example.com",
            password_hash="hashed_password2",
            first_name="Test2",
            last_name="User2"
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):  # IntegrityError 예상
            await db_session.commit()

class TestSubscriptionModel:
    """구독 모델 테스트 클래스"""
    
    async def test_create_subscription_plan(self, db_session: AsyncSession):
        """구독 플랜 생성 테스트"""
        plan = SubscriptionPlan(
            name="basic",
            display_name="Basic Plan",
            description="기본 플랜",
            price_monthly=29.00,
            price_yearly=290.00,
            features=["basic_strategies", "email_support"]
        )
        
        db_session.add(plan)
        await db_session.commit()
        await db_session.refresh(plan)
        
        assert plan.id is not None
        assert plan.name == "basic"
        assert plan.price_monthly == 29.00
        assert plan.is_active is True
    
    async def test_create_subscription(self, db_session: AsyncSession):
        """구독 생성 테스트"""
        # 사용자 생성
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # 구독 플랜 생성
        plan = SubscriptionPlan(
            name="basic",
            display_name="Basic Plan",
            price_monthly=29.00,
            price_yearly=290.00
        )
        db_session.add(plan)
        await db_session.commit()
        await db_session.refresh(plan)
        
        # 구독 생성
        from datetime import datetime, timedelta
        subscription = Subscription(
            user_id=user.id,
            plan_id=plan.id,
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        
        db_session.add(subscription)
        await db_session.commit()
        await db_session.refresh(subscription)
        
        assert subscription.id is not None
        assert subscription.user_id == user.id
        assert subscription.plan_id == plan.id
        assert subscription.status == "active"
    
    async def test_subscription_relationships(self, db_session: AsyncSession):
        """구독 관계 테스트"""
        # 사용자 생성
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # 구독 플랜 생성
        plan = SubscriptionPlan(
            name="basic",
            display_name="Basic Plan",
            price_monthly=29.00,
            price_yearly=290.00
        )
        db_session.add(plan)
        await db_session.commit()
        await db_session.refresh(plan)
        
        # 구독 생성
        from datetime import datetime, timedelta
        subscription = Subscription(
            user_id=user.id,
            plan_id=plan.id,
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(subscription)
        await db_session.commit()
        await db_session.refresh(subscription)
        
        # 결제 생성
        payment = Payment(
            user_id=user.id,
            subscription_id=subscription.id,
            amount=29.00,
            currency="USD",
            status="completed"
        )
        db_session.add(payment)
        await db_session.commit()
        
        # 관계 확인
        assert len(user.subscriptions) == 1
        assert user.subscriptions[0].plan.name == "basic"
        assert len(subscription.payments) == 1
        assert subscription.payments[0].amount == 29.00

class TestAuthService:
    """인증 서비스 테스트 클래스"""
    
    async def test_create_user(self, db_session: AsyncSession):
        """사용자 생성 서비스 테스트"""
        auth_service = AuthService(db_session)
        
        user_data = UserCreate(
            email="test@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="User"
        )
        
        user = await auth_service.create_user(user_data)
        
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.password_hash is not None
        assert user.password_hash != "TestPassword123!"  # 해싱되었는지 확인
    
    async def test_authenticate_user(self, db_session: AsyncSession):
        """사용자 인증 서비스 테스트"""
        auth_service = AuthService(db_session)
        
        # 사용자 생성
        user_data = UserCreate(
            email="test@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="User"
        )
        await auth_service.create_user(user_data)
        
        # 올바른 자격증명으로 인증
        authenticated_user = await auth_service.authenticate_user(
            "test@example.com", "TestPassword123!"
        )
        assert authenticated_user is not None
        assert authenticated_user.email == "test@example.com"
        
        # 잘못된 비밀번호로 인증
        failed_user = await auth_service.authenticate_user(
            "test@example.com", "WrongPassword"
        )
        assert failed_user is None
        
        # 존재하지 않는 이메일로 인증
        nonexistent_user = await auth_service.authenticate_user(
            "nonexistent@example.com", "TestPassword123!"
        )
        assert nonexistent_user is None
