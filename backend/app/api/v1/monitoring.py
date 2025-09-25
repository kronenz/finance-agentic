# 모니터링 관련 API 엔드포인트
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog

from ...core.auth import get_current_user
from ...schemas.monitoring import (
    MetricsRequest,
    MetricsResponse,
    AlertRequest,
    AlertResponse,
    SystemMetrics,
    AgentMetrics,
    DatabaseMetrics,
    RedisMetrics,
    AlertRule,
    AlertStatus
)

logger = structlog.get_logger()
router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    request: MetricsRequest,
    current_user: dict = Depends(get_current_user)
):
    """시스템 메트릭 조회"""
    try:
        # 실제로는 Prometheus에서 메트릭 조회
        # 여기서는 예시 데이터 반환
        
        system_metrics = SystemMetrics(
            cpu_usage=45.2,
            memory_usage=67.8,
            disk_usage=23.4,
            network_in=1024.5,
            network_out=2048.3,
            timestamp=datetime.utcnow().isoformat()
        )
        
        agent_metrics = AgentMetrics(
            data_collection_agent={
                "status": "running",
                "messages_processed": 1500,
                "error_count": 2,
                "last_activity": datetime.utcnow().isoformat()
            },
            data_analysis_agent={
                "status": "running",
                "analyses_completed": 1200,
                "error_count": 1,
                "last_activity": datetime.utcnow().isoformat()
            },
            prediction_agent={
                "status": "running",
                "predictions_made": 800,
                "error_count": 0,
                "last_activity": datetime.utcnow().isoformat()
            }
        )
        
        database_metrics = DatabaseMetrics(
            connection_count=25,
            query_count=5000,
            slow_queries=3,
            lock_wait_time=0.5,
            timestamp=datetime.utcnow().isoformat()
        )
        
        redis_metrics = RedisMetrics(
            memory_usage=128.5,
            connected_clients=15,
            keys_count=10000,
            hit_rate=0.95,
            timestamp=datetime.utcnow().isoformat()
        )
        
        return MetricsResponse(
            system=system_metrics,
            agents=agent_metrics,
            database=database_metrics,
            redis=redis_metrics,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    status: Optional[str] = Query(None, description="알림 상태"),
    severity: Optional[str] = Query(None, description="심각도"),
    limit: int = Query(100, ge=1, le=1000, description="조회 개수"),
    current_user: dict = Depends(get_current_user)
):
    """알림 목록 조회"""
    try:
        # 실제로는 데이터베이스에서 알림 조회
        # 여기서는 예시 데이터 반환
        
        alerts = [
            AlertResponse(
                alert_id="alert_001",
                title="High CPU Usage",
                description="CPU 사용률이 80%를 초과했습니다",
                severity="WARNING",
                status="ACTIVE",
                source="system_monitor",
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            ),
            AlertResponse(
                alert_id="alert_002",
                title="Database Connection Error",
                description="데이터베이스 연결에 실패했습니다",
                severity="CRITICAL",
                status="RESOLVED",
                source="database_monitor",
                created_at=(datetime.utcnow() - timedelta(hours=2)).isoformat(),
                updated_at=(datetime.utcnow() - timedelta(hours=1)).isoformat()
            )
        ]
        
        # 필터링 적용
        if status:
            alerts = [alert for alert in alerts if alert.status == status]
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
            
        return alerts[:limit]
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts", response_model=AlertResponse)
async def create_alert(
    request: AlertRequest,
    current_user: dict = Depends(get_current_user)
):
    """알림 생성"""
    try:
        # 실제로는 알림 생성 및 저장
        # 여기서는 시뮬레이션
        
        alert_id = f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        alert = AlertResponse(
            alert_id=alert_id,
            title=request.title,
            description=request.description,
            severity=request.severity,
            status="ACTIVE",
            source=request.source,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        
        return alert
        
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """알림 해결"""
    try:
        # 실제로는 데이터베이스에서 알림 상태 업데이트
        # 여기서는 시뮬레이션
        
        return {
            "message": f"Alert {alert_id} resolved successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rules", response_model=List[AlertRule])
async def get_alert_rules(
    current_user: dict = Depends(get_current_user)
):
    """알림 규칙 조회"""
    try:
        # 실제로는 데이터베이스에서 알림 규칙 조회
        # 여기서는 예시 데이터 반환
        
        rules = [
            AlertRule(
                rule_id="rule_001",
                name="High CPU Usage",
                description="CPU 사용률이 80%를 초과할 때 알림",
                condition="cpu_usage > 80",
                severity="WARNING",
                is_enabled=True,
                created_at=datetime.utcnow().isoformat()
            ),
            AlertRule(
                rule_id="rule_002",
                name="Database Connection Error",
                description="데이터베이스 연결 실패 시 알림",
                condition="db_connection_failed > 0",
                severity="CRITICAL",
                is_enabled=True,
                created_at=datetime.utcnow().isoformat()
            ),
            AlertRule(
                rule_id="rule_003",
                name="Memory Usage High",
                description="메모리 사용률이 90%를 초과할 때 알림",
                condition="memory_usage > 90",
                severity="CRITICAL",
                is_enabled=True,
                created_at=datetime.utcnow().isoformat()
            )
        ]
        
        return rules
        
    except Exception as e:
        logger.error(f"Error getting alert rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rules", response_model=AlertRule)
async def create_alert_rule(
    request: AlertRule,
    current_user: dict = Depends(get_current_user)
):
    """알림 규칙 생성"""
    try:
        # 실제로는 알림 규칙 생성 및 저장
        # 여기서는 시뮬레이션
        
        rule_id = f"rule_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        rule = AlertRule(
            rule_id=rule_id,
            name=request.name,
            description=request.description,
            condition=request.condition,
            severity=request.severity,
            is_enabled=request.is_enabled,
            created_at=datetime.utcnow().isoformat()
        )
        
        return rule
        
    except Exception as e:
        logger.error(f"Error creating alert rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_health_status(
    current_user: dict = Depends(get_current_user)
):
    """시스템 헬스 상태 조회"""
    try:
        # 실제로는 각 컴포넌트의 상태 확인
        # 여기서는 예시 데이터 반환
        
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "api_server": {
                    "status": "healthy",
                    "response_time": 45.2,
                    "uptime": "99.9%"
                },
                "database": {
                    "status": "healthy",
                    "connection_count": 25,
                    "query_time": 12.5
                },
                "redis": {
                    "status": "healthy",
                    "memory_usage": "128.5MB",
                    "hit_rate": "95%"
                },
                "ai_agents": {
                    "status": "healthy",
                    "active_agents": 3,
                    "total_agents": 3
                }
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_logs(
    level: Optional[str] = Query(None, description="로그 레벨"),
    source: Optional[str] = Query(None, description="로그 소스"),
    start_time: Optional[str] = Query(None, description="시작 시간"),
    end_time: Optional[str] = Query(None, description="종료 시간"),
    limit: int = Query(100, ge=1, le=1000, description="조회 개수"),
    current_user: dict = Depends(get_current_user)
):
    """로그 조회"""
    try:
        # 실제로는 로그 시스템에서 로그 조회
        # 여기서는 예시 데이터 반환
        
        logs = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "source": "api_server",
                "message": "API request processed successfully",
                "details": {
                    "endpoint": "/api/v1/ai/status",
                    "method": "GET",
                    "status_code": 200,
                    "response_time": 45.2
                }
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "level": "WARNING",
                "source": "data_collection",
                "message": "High memory usage detected",
                "details": {
                    "memory_usage": "85%",
                    "threshold": "80%"
                }
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
                "level": "ERROR",
                "source": "database",
                "message": "Database connection timeout",
                "details": {
                    "timeout": "30s",
                    "retry_count": 3
                }
            }
        ]
        
        # 필터링 적용
        if level:
            logs = [log for log in logs if log["level"] == level]
        if source:
            logs = [log for log in logs if log["source"] == source]
            
        return logs[:limit]
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
