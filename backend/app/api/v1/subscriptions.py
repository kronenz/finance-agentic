# 구독 관리 API 엔드포인트
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionPlanResponse,
    SubscriptionStatus
)
from app.services.subscription_service import SubscriptionService
from app.api.v1.auth import get_current_user
from app.core.cache import cached, cache_invalidate, CacheKeys, CacheTTL

# 로거 설정
logger = structlog.get_logger()

router = APIRouter()

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans():
    """구독 플랜 목록 조회"""
    try:
        plans = await SubscriptionService.get_available_plans()
        logger.info("Subscription plans retrieved successfully", count=len(plans))
        return plans
    except Exception as e:
        logger.error("Failed to retrieve subscription plans", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription plans"
        )

@router.get("/", response_model=List[SubscriptionResponse])
async def get_user_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자의 구독 목록 조회"""
    try:
        subscriptions = await SubscriptionService.get_user_subscriptions(
            db, current_user.id
        )
        logger.info(
            "User subscriptions retrieved",
            user_id=current_user.id,
            count=len(subscriptions)
        )
        return subscriptions
    except Exception as e:
        logger.error(
            "Failed to retrieve user subscriptions",
            user_id=current_user.id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscriptions"
        )

@router.get("/active", response_model=Optional[SubscriptionResponse])
async def get_active_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자의 활성 구독 조회"""
    try:
        subscription = await SubscriptionService.get_active_subscription(
            db, current_user.id
        )
        if subscription:
            logger.info(
                "Active subscription retrieved",
                user_id=current_user.id,
                subscription_id=subscription.id
            )
        else:
            logger.info(
                "No active subscription found",
                user_id=current_user.id
            )
        return subscription
    except Exception as e:
        logger.error(
            "Failed to retrieve active subscription",
            user_id=current_user.id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active subscription"
        )

@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """새 구독 생성"""
    try:
        # 기존 활성 구독 확인
        existing_subscription = await SubscriptionService.get_active_subscription(
            db, current_user.id
        )
        if existing_subscription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active subscription"
            )
        
        # 구독 생성
        subscription = await SubscriptionService.create_subscription(
            db, current_user.id, subscription_data
        )
        
        logger.info(
            "Subscription created successfully",
            user_id=current_user.id,
            subscription_id=subscription.id,
            plan_id=subscription.plan_id
        )
        
        return subscription
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to create subscription",
            user_id=current_user.id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )

@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: str,
    subscription_data: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """구독 정보 업데이트"""
    try:
        # 구독 소유권 확인
        subscription = await SubscriptionService.get_subscription_by_id(
            db, subscription_id
        )
        if not subscription or subscription.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # 구독 업데이트
        updated_subscription = await SubscriptionService.update_subscription(
            db, subscription_id, subscription_data
        )
        
        logger.info(
            "Subscription updated successfully",
            user_id=current_user.id,
            subscription_id=subscription_id
        )
        
        return updated_subscription
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update subscription",
            user_id=current_user.id,
            subscription_id=subscription_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription"
        )

@router.post("/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """구독 취소"""
    try:
        # 구독 소유권 확인
        subscription = await SubscriptionService.get_subscription_by_id(
            db, subscription_id
        )
        if not subscription or subscription.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # 구독 취소
        await SubscriptionService.cancel_subscription(db, subscription_id)
        
        logger.info(
            "Subscription cancelled successfully",
            user_id=current_user.id,
            subscription_id=subscription_id
        )
        
        return {"message": "Subscription cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to cancel subscription",
            user_id=current_user.id,
            subscription_id=subscription_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )

@router.post("/{subscription_id}/reactivate")
async def reactivate_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """구독 재활성화"""
    try:
        # 구독 소유권 확인
        subscription = await SubscriptionService.get_subscription_by_id(
            db, subscription_id
        )
        if not subscription or subscription.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # 구독 재활성화
        await SubscriptionService.reactivate_subscription(db, subscription_id)
        
        logger.info(
            "Subscription reactivated successfully",
            user_id=current_user.id,
            subscription_id=subscription_id
        )
        
        return {"message": "Subscription reactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to reactivate subscription",
            user_id=current_user.id,
            subscription_id=subscription_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reactivate subscription"
        )

@router.get("/{subscription_id}/history")
async def get_subscription_history(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """구독 이력 조회"""
    try:
        # 구독 소유권 확인
        subscription = await SubscriptionService.get_subscription_by_id(
            db, subscription_id
        )
        if not subscription or subscription.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # 구독 이력 조회
        history = await SubscriptionService.get_subscription_history(
            db, subscription_id
        )
        
        logger.info(
            "Subscription history retrieved",
            user_id=current_user.id,
            subscription_id=subscription_id,
            count=len(history)
        )
        
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to retrieve subscription history",
            user_id=current_user.id,
            subscription_id=subscription_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription history"
        )
