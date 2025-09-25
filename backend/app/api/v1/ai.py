# AI 관련 API 엔드포인트
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog

from ...services.agent_coordination_service import AgentCoordinationService
from ...services.data_collection_service import DataCollectionService
from ...services.data_analysis_service import DataAnalysisService
from ...ml.models.lstm_model import LSTMModel
from ...ml.models.xgboost_model import XGBoostModel
from ...core.auth import get_current_user
from ...core.cache import cached, cache_invalidate, CacheKeys, CacheTTL
from ...schemas.ai import (
    AISystemStatus,
    DataCollectionRequest,
    DataCollectionResponse,
    ModelPredictionRequest,
    ModelPredictionResponse,
    TradingSignalRequest,
    TradingSignalResponse,
    AgentStatus,
    SystemHealth
)

logger = structlog.get_logger()
router = APIRouter(prefix="/ai", tags=["AI"])
security = HTTPBearer()

# 전역 서비스 인스턴스
agent_coordinator = None
data_collection_service = None
data_analysis_service = None
lstm_model = None
xgboost_model = None

async def get_agent_coordinator() -> AgentCoordinationService:
    """에이전트 조율 서비스 인스턴스 반환"""
    global agent_coordinator
    if agent_coordinator is None:
        agent_coordinator = AgentCoordinationService()
        await agent_coordinator.initialize()
    return agent_coordinator

async def get_data_collection_service() -> DataCollectionService:
    """데이터 수집 서비스 인스턴스 반환"""
    global data_collection_service
    if data_collection_service is None:
        data_collection_service = DataCollectionService()
        await data_collection_service.initialize()
    return data_collection_service

async def get_data_analysis_service() -> DataAnalysisService:
    """데이터 분석 서비스 인스턴스 반환"""
    global data_analysis_service
    if data_analysis_service is None:
        data_analysis_service = DataAnalysisService()
        await data_analysis_service.initialize()
    return data_analysis_service

@router.get("/status", response_model=AISystemStatus)
@cached(ttl=CacheTTL.AI_SYSTEM_STATUS, key_prefix=CacheKeys.AI_SYSTEM_STATUS)
async def get_ai_system_status(
    current_user: dict = Depends(get_current_user),
    coordinator: AgentCoordinationService = Depends(get_agent_coordinator)
):
    """AI 시스템 상태 조회"""
    try:
        status = await coordinator.get_system_status()
        
        return AISystemStatus(
            timestamp=status["timestamp"],
            is_running=status["is_running"],
            agents={
                agent_id: AgentStatus(
                    is_running=agent_info["is_running"],
                    agent_name=agent_info["agent_name"]
                )
                for agent_id, agent_info in status["agents"].items()
            },
            redis_status=status["redis_status"],
            message_queues=status["message_queues"]
        )
        
    except Exception as e:
        logger.error(f"Error getting AI system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data/collect", response_model=DataCollectionResponse)
async def start_data_collection(
    request: DataCollectionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    coordinator: AgentCoordinationService = Depends(get_agent_coordinator)
):
    """데이터 수집 시작"""
    try:
        # 데이터 수집 시작
        await coordinator.start_data_collection(
            symbols=request.symbols,
            exchanges=request.exchanges
        )
        
        # 백그라운드에서 데이터 수집 서비스 시작
        background_tasks.add_task(
            _start_data_collection_background,
            request.symbols,
            request.exchanges
        )
        
        return DataCollectionResponse(
            status="started",
            message=f"Data collection started for {len(request.symbols)} symbols",
            symbols=request.symbols,
            exchanges=request.exchanges,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error starting data collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data/stop")
async def stop_data_collection(
    current_user: dict = Depends(get_current_user),
    coordinator: AgentCoordinationService = Depends(get_agent_coordinator)
):
    """데이터 수집 중지"""
    try:
        await coordinator.stop_data_collection()
        
        return {
            "status": "stopped",
            "message": "Data collection stopped",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping data collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/predict", response_model=ModelPredictionResponse)
async def predict_with_models(
    request: ModelPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """모델을 사용한 예측 수행"""
    try:
        # LSTM 모델 로드 (실제로는 캐시된 모델 사용)
        global lstm_model, xgboost_model
        
        if lstm_model is None:
            lstm_model = LSTMModel()
            # 실제로는 저장된 모델 로드
            # lstm_model.load_model("models/lstm_model.h5")
            
        if xgboost_model is None:
            xgboost_model = XGBoostModel()
            # 실제로는 저장된 모델 로드
            # xgboost_model.load_model("models/xgboost_model.pkl")
        
        # 예측 수행 (실제로는 전처리된 데이터 사용)
        predictions = {
            "lstm_prediction": {
                "predicted_price": 50000.0,
                "confidence": 0.85,
                "timestamp": datetime.utcnow().isoformat()
            },
            "xgboost_prediction": {
                "signal": "BUY",
                "confidence": 0.75,
                "probability": {
                    "BUY": 0.75,
                    "HOLD": 0.20,
                    "SELL": 0.05
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return ModelPredictionResponse(
            symbol=request.symbol,
            predictions=predictions,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error making predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/signals/generate", response_model=TradingSignalResponse)
async def generate_trading_signals(
    request: TradingSignalRequest,
    current_user: dict = Depends(get_current_user)
):
    """거래 신호 생성"""
    try:
        # 실제로는 AI 에이전트를 통해 신호 생성
        # 여기서는 예시 신호 생성
        
        signals = []
        for symbol in request.symbols:
            signal = {
                "symbol": symbol,
                "signal": "BUY",
                "confidence": 0.80,
                "price": 50000.0,
                "timestamp": datetime.utcnow().isoformat(),
                "reasoning": "RSI oversold, MACD bullish crossover"
            }
            signals.append(signal)
        
        return TradingSignalResponse(
            signals=signals,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error generating trading signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=SystemHealth)
async def get_system_health():
    """시스템 헬스 체크"""
    try:
        # Redis 연결 확인
        redis_status = "healthy"
        try:
            # 실제로는 Redis ping
            pass
        except:
            redis_status = "unhealthy"
        
        # 데이터베이스 연결 확인
        db_status = "healthy"
        try:
            # 실제로는 DB 연결 확인
            pass
        except:
            db_status = "unhealthy"
        
        # AI 에이전트 상태 확인
        agent_status = "healthy"
        try:
            coordinator = await get_agent_coordinator()
            status = await coordinator.get_system_status()
            if not status["is_running"]:
                agent_status = "unhealthy"
        except:
            agent_status = "unhealthy"
        
        overall_status = "healthy" if all([
            redis_status == "healthy",
            db_status == "healthy",
            agent_status == "healthy"
        ]) else "unhealthy"
        
        return SystemHealth(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            components={
                "redis": redis_status,
                "database": db_status,
                "ai_agents": agent_status
            }
        )
        
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _start_data_collection_background(symbols: List[str], exchanges: List[str]):
    """백그라운드 데이터 수집 작업"""
    try:
        data_service = await get_data_collection_service()
        await data_service.start_collection(symbols, exchanges)
    except Exception as e:
        logger.error(f"Error in background data collection: {e}")

@router.on_event("shutdown")
async def shutdown_ai_services():
    """AI 서비스 종료"""
    try:
        global agent_coordinator, data_collection_service, data_analysis_service
        
        if agent_coordinator:
            await agent_coordinator.cleanup()
            
        if data_collection_service:
            await data_collection_service.cleanup()
            
        if data_analysis_service:
            await data_analysis_service.cleanup()
            
        logger.info("AI services shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during AI services shutdown: {e}")