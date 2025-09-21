# 구독 관리 서비스
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import structlog

from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionHistory
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionPlanResponse,
    SubscriptionHistoryResponse,
    SubscriptionStatus
)
from app.services.payment_service import PaymentService

# 로거 설정
logger = structlog.get_logger()

class SubscriptionService:
    """구독 관리 서비스 클래스"""
    
    @staticmethod
    async def get_available_plans() -> List[SubscriptionPlanResponse]:
        """사용 가능한 구독 플랜 목록 조회"""
        try:
            # 실제 구현에서는 데이터베이스에서 조회
            # 여기서는 하드코딩된 플랜 반환
            plans = [
                SubscriptionPlanResponse(
                    id="basic",
                    name="Basic Plan",
                    description="기본 거래 기능과 제한된 API 접근",
                    price=29.99,
                    currency="USD",
                    billing_cycle="monthly",
                    features=[
                        "일일 최대 10회 거래",
                        "기본 기술 지표",
                        "이메일 지원",
                        "포트폴리오 가치 최대 $10,000"
                    ],
                    max_trades_per_day=10,
                    max_portfolio_value=10000.0,
                    is_active=True
                ),
                SubscriptionPlanResponse(
                    id="premium",
                    name="Premium Plan",
                    description="고급 거래 기능과 AI 추천",
                    price=79.99,
                    currency="USD",
                    billing_cycle="monthly",
                    features=[
                        "일일 최대 50회 거래",
                        "AI 기반 전략 추천",
                        "고급 기술 지표",
                        "실시간 알림",
                        "우선 지원",
                        "포트폴리오 가치 최대 $100,000"
                    ],
                    max_trades_per_day=50,
                    max_portfolio_value=100000.0,
                    is_active=True
                ),
                SubscriptionPlanResponse(
                    id="pro",
                    name="Pro Plan",
                    description="전체 기능과 무제한 거래",
                    price=199.99,
                    currency="USD",
                    billing_cycle="monthly",
                    features=[
                        "무제한 거래",
                        "AI 기반 전략 추천",
                        "모든 기술 지표",
                        "실시간 알림",
                        "전용 지원",
                        "무제한 포트폴리오",
                        "API 접근",
                        "백테스팅 도구"
                    ],
                    max_trades_per_day=-1,  # 무제한
                    max_portfolio_value=-1.0,  # 무제한
                    is_active=True
                )
            ]
            
            logger.info("Available subscription plans retrieved", count=len(plans))
            return plans
            
        except Exception as e:
            logger.error("Failed to retrieve subscription plans", error=str(e))
            raise
    
    @staticmethod
    async def get_user_subscriptions(
        db: AsyncSession, 
        user_id: str
    ) -> List[SubscriptionResponse]:
        """사용자의 구독 목록 조회"""
        try:
            result = await db.execute(
                select(Subscription)
                .where(Subscription.user_id == user_id)
                .order_by(Subscription.created_at.desc())
            )
            subscriptions = result.scalars().all()
            
            subscription_responses = []
            for sub in subscriptions:
                # 플랜 정보 조회
                plan = await SubscriptionService.get_plan_by_id(sub.plan_id)
                
                subscription_responses.append(SubscriptionResponse(
                    id=sub.id,
                    user_id=sub.user_id,
                    plan_id=sub.plan_id,
                    plan_name=plan.name if plan else "Unknown Plan",
                    status=SubscriptionStatus(sub.status),
                    start_date=sub.start_date,
                    end_date=sub.end_date,
                    billing_cycle=sub.billing_cycle,
                    price=sub.price,
                    currency=sub.currency,
                    is_active=sub.is_active,
                    created_at=sub.created_at,
                    updated_at=sub.updated_at
                ))
            
            logger.info(
                "User subscriptions retrieved",
                user_id=user_id,
                count=len(subscription_responses)
            )
            return subscription_responses
            
        except Exception as e:
            logger.error(
                "Failed to retrieve user subscriptions",
                user_id=user_id,
                error=str(e)
            )
            raise
    
    @staticmethod
    async def get_active_subscription(
        db: AsyncSession, 
        user_id: str
    ) -> Optional[SubscriptionResponse]:
        """사용자의 활성 구독 조회"""
        try:
            result = await db.execute(
                select(Subscription)
                .where(
                    and_(
                        Subscription.user_id == user_id,
                        Subscription.is_active == True,
                        or_(
                            Subscription.end_date.is_(None),
                            Subscription.end_date > datetime.utcnow()
                        )
                    )
                )
                .order_by(Subscription.created_at.desc())
            )
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                return None
            
            # 플랜 정보 조회
            plan = await SubscriptionService.get_plan_by_id(subscription.plan_id)
            
            subscription_response = SubscriptionResponse(
                id=subscription.id,
                user_id=subscription.user_id,
                plan_id=subscription.plan_id,
                plan_name=plan.name if plan else "Unknown Plan",
                status=SubscriptionStatus(subscription.status),
                start_date=subscription.start_date,
                end_date=subscription.end_date,
                billing_cycle=subscription.billing_cycle,
                price=subscription.price,
                currency=subscription.currency,
                is_active=subscription.is_active,
                created_at=subscription.created_at,
                updated_at=subscription.updated_at
            )
            
            logger.info(
                "Active subscription retrieved",
                user_id=user_id,
                subscription_id=subscription.id
            )
            return subscription_response
            
        except Exception as e:
            logger.error(
                "Failed to retrieve active subscription",
                user_id=user_id,
                error=str(e)
            )
            raise
    
    @staticmethod
    async def create_subscription(
        db: AsyncSession,
        user_id: str,
        subscription_data: SubscriptionCreate
    ) -> SubscriptionResponse:
        """새 구독 생성"""
        try:
            # 플랜 정보 조회
            plan = await SubscriptionService.get_plan_by_id(subscription_data.plan_id)
            if not plan:
                raise ValueError(f"Plan {subscription_data.plan_id} not found")
            
            # 결제 처리
            payment_result = await PaymentService.process_subscription_payment(
                user_id, subscription_data.payment_method_id, plan.price
            )
            
            if not payment_result.success:
                raise ValueError(f"Payment failed: {payment_result.error}")
            
            # 구독 기간 계산
            start_date = datetime.utcnow()
            if subscription_data.billing_cycle == "monthly":
                end_date = start_date + timedelta(days=30)
            else:  # yearly
                end_date = start_date + timedelta(days=365)
            
            # 구독 생성
            subscription = Subscription(
                user_id=user_id,
                plan_id=subscription_data.plan_id,
                status=SubscriptionStatus.ACTIVE,
                start_date=start_date,
                end_date=end_date,
                billing_cycle=subscription_data.billing_cycle,
                price=plan.price,
                currency=plan.currency,
                is_active=True,
                stripe_subscription_id=payment_result.subscription_id
            )
            
            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)
            
            # 구독 이력 기록
            await SubscriptionService._create_subscription_history(
                db, subscription.id, "created", None, SubscriptionStatus.ACTIVE,
                f"Subscription created for plan {plan.name}"
            )
            
            logger.info(
                "Subscription created successfully",
                user_id=user_id,
                subscription_id=subscription.id,
                plan_id=subscription_data.plan_id
            )
            
            return SubscriptionResponse(
                id=subscription.id,
                user_id=subscription.user_id,
                plan_id=subscription.plan_id,
                plan_name=plan.name,
                status=SubscriptionStatus(subscription.status),
                start_date=subscription.start_date,
                end_date=subscription.end_date,
                billing_cycle=subscription.billing_cycle,
                price=subscription.price,
                currency=subscription.currency,
                is_active=subscription.is_active,
                created_at=subscription.created_at,
                updated_at=subscription.updated_at
            )
            
        except Exception as e:
            await db.rollback()
            logger.error(
                "Failed to create subscription",
                user_id=user_id,
                error=str(e)
            )
            raise
    
    @staticmethod
    async def update_subscription(
        db: AsyncSession,
        subscription_id: str,
        subscription_data: SubscriptionUpdate
    ) -> SubscriptionResponse:
        """구독 정보 업데이트"""
        try:
            result = await db.execute(
                select(Subscription).where(Subscription.id == subscription_id)
            )
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                raise ValueError(f"Subscription {subscription_id} not found")
            
            old_status = subscription.status
            
            # 업데이트할 필드들
            update_data = subscription_data.dict(exclude_unset=True)
            
            # 플랜 변경 시 결제 처리
            if "plan_id" in update_data:
                plan = await SubscriptionService.get_plan_by_id(update_data["plan_id"])
                if not plan:
                    raise ValueError(f"Plan {update_data['plan_id']} not found")
                
                # 결제 처리 (업그레이드/다운그레이드)
                payment_result = await PaymentService.process_plan_change(
                    subscription.user_id, subscription_id, plan.price
                )
                
                if not payment_result.success:
                    raise ValueError(f"Payment failed: {payment_result.error}")
                
                update_data["price"] = plan.price
                update_data["currency"] = plan.currency
            
            # 구독 업데이트
            for field, value in update_data.items():
                setattr(subscription, field, value)
            
            subscription.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(subscription)
            
            # 구독 이력 기록
            await SubscriptionService._create_subscription_history(
                db, subscription_id, "updated", old_status, subscription.status,
                f"Subscription updated: {', '.join(update_data.keys())}"
            )
            
            # 플랜 정보 조회
            plan = await SubscriptionService.get_plan_by_id(subscription.plan_id)
            
            logger.info(
                "Subscription updated successfully",
                subscription_id=subscription_id,
                updated_fields=list(update_data.keys())
            )
            
            return SubscriptionResponse(
                id=subscription.id,
                user_id=subscription.user_id,
                plan_id=subscription.plan_id,
                plan_name=plan.name if plan else "Unknown Plan",
                status=SubscriptionStatus(subscription.status),
                start_date=subscription.start_date,
                end_date=subscription.end_date,
                billing_cycle=subscription.billing_cycle,
                price=subscription.price,
                currency=subscription.currency,
                is_active=subscription.is_active,
                created_at=subscription.created_at,
                updated_at=subscription.updated_at
            )
            
        except Exception as e:
            await db.rollback()
            logger.error(
                "Failed to update subscription",
                subscription_id=subscription_id,
                error=str(e)
            )
            raise
    
    @staticmethod
    async def cancel_subscription(
        db: AsyncSession,
        subscription_id: str
    ) -> None:
        """구독 취소"""
        try:
            result = await db.execute(
                select(Subscription).where(Subscription.id == subscription_id)
            )
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                raise ValueError(f"Subscription {subscription_id} not found")
            
            old_status = subscription.status
            
            # 구독 취소
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.is_active = False
            subscription.updated_at = datetime.utcnow()
            
            # Stripe 구독 취소
            if subscription.stripe_subscription_id:
                await PaymentService.cancel_subscription(subscription.stripe_subscription_id)
            
            await db.commit()
            
            # 구독 이력 기록
            await SubscriptionService._create_subscription_history(
                db, subscription_id, "cancelled", old_status, SubscriptionStatus.CANCELLED,
                "Subscription cancelled by user"
            )
            
            logger.info(
                "Subscription cancelled successfully",
                subscription_id=subscription_id
            )
            
        except Exception as e:
            await db.rollback()
            logger.error(
                "Failed to cancel subscription",
                subscription_id=subscription_id,
                error=str(e)
            )
            raise
    
    @staticmethod
    async def reactivate_subscription(
        db: AsyncSession,
        subscription_id: str
    ) -> None:
        """구독 재활성화"""
        try:
            result = await db.execute(
                select(Subscription).where(Subscription.id == subscription_id)
            )
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                raise ValueError(f"Subscription {subscription_id} not found")
            
            old_status = subscription.status
            
            # 구독 재활성화
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.is_active = True
            subscription.updated_at = datetime.utcnow()
            
            # 결제 처리
            payment_result = await PaymentService.process_subscription_payment(
                subscription.user_id, subscription.payment_method_id, subscription.price
            )
            
            if not payment_result.success:
                raise ValueError(f"Payment failed: {payment_result.error}")
            
            await db.commit()
            
            # 구독 이력 기록
            await SubscriptionService._create_subscription_history(
                db, subscription_id, "reactivated", old_status, SubscriptionStatus.ACTIVE,
                "Subscription reactivated by user"
            )
            
            logger.info(
                "Subscription reactivated successfully",
                subscription_id=subscription_id
            )
            
        except Exception as e:
            await db.rollback()
            logger.error(
                "Failed to reactivate subscription",
                subscription_id=subscription_id,
                error=str(e)
            )
            raise
    
    @staticmethod
    async def get_subscription_by_id(
        db: AsyncSession,
        subscription_id: str
    ) -> Optional[Subscription]:
        """ID로 구독 조회"""
        try:
            result = await db.execute(
                select(Subscription).where(Subscription.id == subscription_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                "Failed to retrieve subscription by ID",
                subscription_id=subscription_id,
                error=str(e)
            )
            raise
    
    @staticmethod
    async def get_subscription_history(
        db: AsyncSession,
        subscription_id: str
    ) -> List[SubscriptionHistoryResponse]:
        """구독 이력 조회"""
        try:
            result = await db.execute(
                select(SubscriptionHistory)
                .where(SubscriptionHistory.subscription_id == subscription_id)
                .order_by(SubscriptionHistory.created_at.desc())
            )
            histories = result.scalars().all()
            
            history_responses = []
            for history in histories:
                history_responses.append(SubscriptionHistoryResponse(
                    id=history.id,
                    subscription_id=history.subscription_id,
                    action=history.action,
                    old_status=SubscriptionStatus(history.old_status) if history.old_status else None,
                    new_status=SubscriptionStatus(history.new_status),
                    description=history.description,
                    created_at=history.created_at
                ))
            
            logger.info(
                "Subscription history retrieved",
                subscription_id=subscription_id,
                count=len(history_responses)
            )
            return history_responses
            
        except Exception as e:
            logger.error(
                "Failed to retrieve subscription history",
                subscription_id=subscription_id,
                error=str(e)
            )
            raise
    
    @staticmethod
    async def get_plan_by_id(plan_id: str) -> Optional[SubscriptionPlanResponse]:
        """플랜 ID로 플랜 정보 조회"""
        try:
            plans = await SubscriptionService.get_available_plans()
            for plan in plans:
                if plan.id == plan_id:
                    return plan
            return None
        except Exception as e:
            logger.error(
                "Failed to retrieve plan by ID",
                plan_id=plan_id,
                error=str(e)
            )
            raise
    
    @staticmethod
    async def _create_subscription_history(
        db: AsyncSession,
        subscription_id: str,
        action: str,
        old_status: Optional[SubscriptionStatus],
        new_status: SubscriptionStatus,
        description: str
    ) -> None:
        """구독 이력 생성"""
        try:
            history = SubscriptionHistory(
                subscription_id=subscription_id,
                action=action,
                old_status=old_status.value if old_status else None,
                new_status=new_status.value,
                description=description
            )
            
            db.add(history)
            await db.commit()
            
        except Exception as e:
            logger.error(
                "Failed to create subscription history",
                subscription_id=subscription_id,
                error=str(e)
            )
            raise
