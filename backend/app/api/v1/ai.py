# AI/ML API 엔드포인트
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import pandas as pd
import structlog

from app.core.database import get_db
from app.models.user import User
from app.services.ai_service import ai_service
from app.api.v1.auth import get_current_user
from app.schemas.ai import (
    MarketAnalysisRequest,
    MarketAnalysisResponse,
    StrategyRecommendationRequest,
    StrategyRecommendationResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    UserProfileUpdate,
    UserProfileResponse
)

# 로거 설정
logger = structlog.get_logger()

router = APIRouter()

@router.post("/market/analyze", response_model=MarketAnalysisResponse)
async def analyze_market(
    request: MarketAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """시장 분석 API"""
    try:
        # 가격 데이터를 DataFrame으로 변환
        price_data = pd.DataFrame(request.price_data)
        
        # 시장 분석 수행
        analysis_result = await ai_service.analyze_market(price_data)
        
        # 백그라운드에서 모델 업데이트 (선택적)
        if request.update_model:
            background_tasks.add_task(
                _update_market_model,
                request.price_data,
                request.regime_label
            )
        
        logger.info(
            "Market analysis completed",
            symbol=request.symbol,
            regime=analysis_result['regime_analysis']['regime'],
            confidence=analysis_result['regime_analysis']['confidence']
        )
        
        return MarketAnalysisResponse(
            symbol=request.symbol,
            regime=analysis_result['regime_analysis']['regime'],
            confidence=analysis_result['regime_analysis']['confidence'],
            probabilities=analysis_result['regime_analysis']['probabilities'],
            market_indicators=analysis_result['market_indicators'],
            timestamp=analysis_result['timestamp']
        )
        
    except Exception as e:
        logger.error("Failed to analyze market", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze market"
        )

@router.post("/strategies/recommend", response_model=List[StrategyRecommendationResponse])
async def recommend_strategies(
    request: StrategyRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """전략 추천 API"""
    try:
        # 사용자 프로필 조회 또는 생성
        user_profile = await _get_or_create_user_profile(db, current_user.id)
        
        # 요청된 프로필 업데이트 적용
        if request.profile_updates:
            user_profile.update(request.profile_updates)
            await _update_user_profile(db, current_user.id, user_profile)
        
        # 전략 추천 수행
        recommendations = await ai_service.recommend_strategies(
            current_user.id, user_profile
        )
        
        # 응답 형식 변환
        response = []
        for rec in recommendations:
            response.append(StrategyRecommendationResponse(
                strategy_id=rec['strategy'],
                strategy_name=_get_strategy_name(rec['strategy']),
                score=rec['score'],
                confidence=rec['confidence'],
                description=_get_strategy_description(rec['strategy']),
                risk_level=_get_strategy_risk_level(rec['strategy'])
            ))
        
        logger.info(
            "Strategies recommended for user",
            user_id=str(current_user.id),
            recommendations_count=len(response)
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Failed to recommend strategies",
            user_id=str(current_user.id),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to recommend strategies"
        )

@router.post("/risk/assess", response_model=RiskAssessmentResponse)
async def assess_risk(
    request: RiskAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """리스크 평가 API"""
    try:
        # 포트폴리오 데이터 조회
        portfolio_data = await _get_portfolio_data(db, current_user.id)
        
        # 리스크 평가 수행
        risk_assessment = await ai_service.assess_risk(
            current_user.id, request.market_data, portfolio_data
        )
        
        logger.info(
            "Risk assessed for user",
            user_id=str(current_user.id),
            risk_level=risk_assessment['risk_level'],
            risk_score=risk_assessment['total_risk_score']
        )
        
        return RiskAssessmentResponse(
            total_risk_score=risk_assessment['total_risk_score'],
            risk_level=risk_assessment['risk_level'],
            market_risk=risk_assessment['market_risk'],
            portfolio_risk=risk_assessment['portfolio_risk'],
            recommendations=risk_assessment['recommendations'],
            timestamp=risk_assessment.get('timestamp', '')
        )
        
    except Exception as e:
        logger.error(
            "Failed to assess risk",
            user_id=str(current_user.id),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assess risk"
        )

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자 프로필 조회"""
    try:
        user_profile = await _get_or_create_user_profile(db, current_user.id)
        
        logger.info(
            "User profile retrieved",
            user_id=current_user.id
        )
        
        return UserProfileResponse(
            user_id=str(current_user.id),
            risk_tolerance=user_profile.get('risk_tolerance', 0.5),
            trading_experience=user_profile.get('trading_experience', 0.5),
            investment_horizon=user_profile.get('investment_horizon', 0.5),
            portfolio_size=user_profile.get('portfolio_size', 0.0),
            preferences=user_profile.get('preferences', {}),
            trading_history=user_profile.get('trading_history', [])
        )
        
    except Exception as e:
        logger.error(
            "Failed to get user profile",
            user_id=str(current_user.id),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자 프로필 업데이트"""
    try:
        # 기존 프로필 조회
        user_profile = await _get_or_create_user_profile(db, current_user.id)
        
        # 프로필 업데이트
        update_data = profile_update.dict(exclude_unset=True)
        user_profile.update(update_data)
        
        # 데이터베이스 업데이트
        await _update_user_profile(db, current_user.id, user_profile)
        
        logger.info(
            "User profile updated",
            user_id=str(current_user.id),
            updated_fields=list(update_data.keys())
        )
        
        return UserProfileResponse(
            user_id=str(current_user.id),
            risk_tolerance=user_profile.get('risk_tolerance', 0.5),
            trading_experience=user_profile.get('trading_experience', 0.5),
            investment_horizon=user_profile.get('investment_horizon', 0.5),
            portfolio_size=user_profile.get('portfolio_size', 0.0),
            preferences=user_profile.get('preferences', {}),
            trading_history=user_profile.get('trading_history', [])
        )
        
    except Exception as e:
        logger.error(
            "Failed to update user profile",
            user_id=str(current_user.id),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

@router.get("/models/status")
async def get_models_status():
    """AI 모델 상태 조회"""
    try:
        status = {
            'market_regime_detector': {
                'trained': ai_service.market_regime_detector.is_trained,
                'model_type': 'RandomForestClassifier'
            },
            'strategy_recommender': {
                'trained': ai_service.strategy_recommender.is_trained,
                'model_type': 'RandomForestRegressor'
            },
            'risk_assessor': {
                'trained': ai_service.risk_assessor.is_trained,
                'model_type': 'RandomForestClassifier'
            }
        }
        
        logger.info("AI models status retrieved")
        return status
        
    except Exception as e:
        logger.error("Failed to get models status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get models status"
        )

# 헬퍼 함수들

async def _get_or_create_user_profile(db: AsyncSession, user_id: str) -> Dict[str, Any]:
    """사용자 프로필 조회 또는 생성"""
    try:
        # 기본 프로필 반환 (실제 구현에서는 데이터베이스에서 조회)
        return {
            'user_id': user_id,
            'risk_tolerance': 0.5,
            'trading_experience': 0.5,
            'investment_horizon': 0.5,
            'portfolio_size': 0.0,
        'preferences': {
            'prefers_trend_following': 0.5,
            'prefers_mean_reversion': 0.5,
            'prefers_short_term': 0.5,
            'prefers_long_term': 0.5
        },
        'trading_history': []
    }
    except Exception as e:
        logger.error("Failed to get user profile", user_id=user_id, error=str(e))
        # 기본 프로필 반환
        return {
            'user_id': user_id,
            'risk_tolerance': 0.5,
            'trading_experience': 0.5,
            'investment_horizon': 0.5,
            'portfolio_size': 0.0,
            'preferences': {
                'prefers_trend_following': 0.5,
                'prefers_mean_reversion': 0.5,
                'prefers_short_term': 0.5,
                'prefers_long_term': 0.5
            },
            'trading_history': []
        }

async def _update_user_profile(db: AsyncSession, user_id: str, profile: Dict[str, Any]) -> None:
    """사용자 프로필 업데이트"""
    # 실제 구현에서는 데이터베이스 업데이트
    pass

async def _get_portfolio_data(db: AsyncSession, user_id: str) -> Dict[str, Any]:
    """포트폴리오 데이터 조회"""
    # 실제 구현에서는 데이터베이스에서 조회
    return {
        'concentration': 0.3,
        'leverage': 1.0,
        'position_size': 0.1
    }

async def _update_market_model(price_data: List[Dict[str, Any]], regime_label: Optional[str]) -> None:
    """시장 모델 업데이트 (백그라운드 작업)"""
    try:
        if regime_label:
            # 모델 재훈련 로직
            logger.info("Market model update started")
            # 실제 구현에서는 모델 재훈련
            logger.info("Market model update completed")
    except Exception as e:
        logger.error("Failed to update market model", error=str(e))

def _get_strategy_name(strategy_id: str) -> str:
    """전략 ID를 이름으로 변환"""
    strategy_names = {
        'supertrend_trend_following': 'Supertrend Trend Following',
        'rsi_mean_reversion': 'RSI Mean Reversion',
        'bollinger_bands_squeeze': 'Bollinger Bands Squeeze',
        'macd_crossover': 'MACD Crossover',
        'moving_average_crossover': 'Moving Average Crossover'
    }
    return strategy_names.get(strategy_id, strategy_id)

def _get_strategy_description(strategy_id: str) -> str:
    """전략 설명 반환"""
    descriptions = {
        'supertrend_trend_following': 'Trend-following strategy using Supertrend indicator',
        'rsi_mean_reversion': 'Mean reversion strategy using RSI indicator',
        'bollinger_bands_squeeze': 'Volatility breakout strategy using Bollinger Bands',
        'macd_crossover': 'Trend-following strategy using MACD crossover signals',
        'moving_average_crossover': 'Trend-following strategy using moving average crossovers'
    }
    return descriptions.get(strategy_id, 'Custom trading strategy')

def _get_strategy_risk_level(strategy_id: str) -> str:
    """전략 리스크 레벨 반환"""
    risk_levels = {
        'supertrend_trend_following': 'medium',
        'rsi_mean_reversion': 'low',
        'bollinger_bands_squeeze': 'high',
        'macd_crossover': 'medium',
        'moving_average_crossover': 'low'
    }
    return risk_levels.get(strategy_id, 'medium')
