# 모니터링 관련 Pydantic 스키마
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime

# 알림 상태 열거형
AlertStatus = Literal["active", "resolved", "acknowledged", "suppressed"]

class MetricsRequest(BaseModel):
    """메트릭 요청"""
    start_time: Optional[str] = Field(None, description="시작 시간")
    end_time: Optional[str] = Field(None, description="종료 시간")
    interval: Optional[str] = Field("1m", description="간격")
    components: Optional[List[str]] = Field(None, description="컴포넌트 목록")
    
    class Config:
        schema_extra = {
            "example": {
                "start_time": "2024-12-23T00:00:00Z",
                "end_time": "2024-12-23T23:59:59Z",
                "interval": "1m",
                "components": ["system", "agents", "database", "redis"]
            }
        }

class SystemMetrics(BaseModel):
    """시스템 메트릭"""
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU 사용률 (%)")
    memory_usage: float = Field(..., ge=0, le=100, description="메모리 사용률 (%)")
    disk_usage: float = Field(..., ge=0, le=100, description="디스크 사용률 (%)")
    network_in: float = Field(..., ge=0, description="네트워크 입력 (MB/s)")
    network_out: float = Field(..., ge=0, description="네트워크 출력 (MB/s)")
    timestamp: str

class AgentMetrics(BaseModel):
    """에이전트 메트릭"""
    data_collection_agent: Dict[str, Any]
    data_analysis_agent: Dict[str, Any]
    prediction_agent: Dict[str, Any]

class DatabaseMetrics(BaseModel):
    """데이터베이스 메트릭"""
    connection_count: int = Field(..., ge=0, description="연결 수")
    query_count: int = Field(..., ge=0, description="쿼리 수")
    slow_queries: int = Field(..., ge=0, description="느린 쿼리 수")
    lock_wait_time: float = Field(..., ge=0, description="락 대기 시간 (ms)")
    timestamp: str

class RedisMetrics(BaseModel):
    """Redis 메트릭"""
    memory_usage: float = Field(..., ge=0, description="메모리 사용량 (MB)")
    connected_clients: int = Field(..., ge=0, description="연결된 클라이언트 수")
    keys_count: int = Field(..., ge=0, description="키 수")
    hit_rate: float = Field(..., ge=0, le=1, description="히트율")
    timestamp: str

class MetricsResponse(BaseModel):
    """메트릭 응답"""
    system: SystemMetrics
    agents: AgentMetrics
    database: DatabaseMetrics
    redis: RedisMetrics
    timestamp: str

class AlertRequest(BaseModel):
    """알림 요청"""
    title: str = Field(..., description="알림 제목")
    description: str = Field(..., description="알림 설명")
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(..., description="심각도")
    source: str = Field(..., description="알림 소스")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "High CPU Usage",
                "description": "CPU 사용률이 80%를 초과했습니다",
                "severity": "HIGH",
                "source": "system_monitor"
            }
        }

class AlertResponse(BaseModel):
    """알림 응답"""
    alert_id: str
    title: str
    description: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    status: Literal["ACTIVE", "RESOLVED", "SUPPRESSED"]
    source: str
    created_at: str
    updated_at: str

class AlertRule(BaseModel):
    """알림 규칙"""
    rule_id: str
    name: str
    description: str
    condition: str = Field(..., description="알림 조건")
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    is_enabled: bool = Field(True, description="활성화 여부")
    created_at: str
    
    class Config:
        schema_extra = {
            "example": {
                "rule_id": "rule_001",
                "name": "High CPU Usage",
                "description": "CPU 사용률이 80%를 초과할 때 알림",
                "condition": "cpu_usage > 80",
                "severity": "HIGH",
                "is_enabled": True,
                "created_at": "2024-12-23T10:00:00Z"
            }
        }

class LogEntry(BaseModel):
    """로그 엔트리"""
    timestamp: str
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    source: str
    message: str
    details: Optional[Dict[str, Any]] = None

class HealthCheck(BaseModel):
    """헬스 체크"""
    component: str
    status: Literal["healthy", "unhealthy", "degraded"]
    response_time: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: str

class SystemHealth(BaseModel):
    """시스템 헬스"""
    overall_status: Literal["healthy", "unhealthy", "degraded"]
    timestamp: str
    components: Dict[str, HealthCheck]

class PerformanceMetrics(BaseModel):
    """성능 메트릭"""
    response_time: float = Field(..., ge=0, description="응답 시간 (ms)")
    throughput: float = Field(..., ge=0, description="처리량 (req/s)")
    error_rate: float = Field(..., ge=0, le=1, description="에러율")
    availability: float = Field(..., ge=0, le=1, description="가용성")
    timestamp: str

class DashboardConfig(BaseModel):
    """대시보드 설정"""
    dashboard_id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]]
    refresh_interval: int = Field(30, ge=5, le=300, description="새로고침 간격 (초)")
    is_public: bool = Field(False, description="공개 여부")
    created_at: str

class WidgetConfig(BaseModel):
    """위젯 설정"""
    widget_id: str
    type: Literal["chart", "metric", "table", "alert"]
    title: str
    data_source: str
    query: str
    position: Dict[str, int]
    size: Dict[str, int]
    options: Optional[Dict[str, Any]] = None

class NotificationChannel(BaseModel):
    """알림 채널"""
    channel_id: str
    name: str
    type: Literal["email", "slack", "webhook", "sms"]
    config: Dict[str, Any]
    is_enabled: bool = Field(True, description="활성화 여부")
    created_at: str

class NotificationRule(BaseModel):
    """알림 규칙"""
    rule_id: str
    name: str
    condition: str
    channels: List[str]
    cooldown: int = Field(300, ge=0, description="쿨다운 시간 (초)")
    is_enabled: bool = Field(True, description="활성화 여부")
    created_at: str

class MetricsQuery(BaseModel):
    """메트릭 쿼리"""
    query: str = Field(..., description="Prometheus 쿼리")
    start_time: str = Field(..., description="시작 시간")
    end_time: str = Field(..., description="종료 시간")
    step: Optional[str] = Field("1m", description="스텝 간격")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "cpu_usage_percent",
                "start_time": "2024-12-23T00:00:00Z",
                "end_time": "2024-12-23T23:59:59Z",
                "step": "1m"
            }
        }

class MetricsData(BaseModel):
    """메트릭 데이터"""
    metric_name: str
    labels: Dict[str, str]
    values: List[List[float]]  # [[timestamp, value], ...]
    timestamp: str
