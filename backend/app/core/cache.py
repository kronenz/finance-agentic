# Redis 캐싱 시스템
import json
import asyncio
from typing import Any, Optional, Union
import redis.asyncio as redis
from functools import wraps
import structlog

logger = structlog.get_logger()

class CacheManager:
    """Redis 캐시 관리자"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.default_ttl = 3600  # 1시간 기본 TTL
    
    async def initialize(self):
        """Redis 연결 초기화"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis cache connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def close(self):
        """Redis 연결 종료"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis cache connection closed")
    
    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """캐시에 데이터 저장"""
        if not self.redis_client:
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            ttl = ttl or self.default_ttl
            await self.redis_client.setex(key, ttl, serialized_value)
            logger.debug(f"Cache set for key {key} with TTL {ttl}")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """캐시에서 데이터 삭제"""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            logger.debug(f"Cache delete for key {key}: {result}")
            return bool(result)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """패턴에 맞는 캐시 키들 삭제"""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                result = await self.redis_client.delete(*keys)
                logger.debug(f"Cache delete pattern {pattern}: {result} keys deleted")
                return result
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """캐시 키 존재 여부 확인"""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """캐시 키의 TTL 조회"""
        if not self.redis_client:
            return -1
        
        try:
            ttl = await self.redis_client.ttl(key)
            return ttl
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return -1

# 전역 캐시 매니저 인스턴스
cache_manager = CacheManager()

def cache_key(*args, **kwargs) -> str:
    """캐시 키 생성"""
    key_parts = []
    
    # 위치 인수 처리
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        elif hasattr(arg, 'id'):
            key_parts.append(f"{arg.__class__.__name__}:{arg.id}")
        else:
            key_parts.append(str(arg))
    
    # 키워드 인수 처리
    for key, value in sorted(kwargs.items()):
        if isinstance(value, (str, int, float, bool)):
            key_parts.append(f"{key}:{value}")
        elif hasattr(value, 'id'):
            key_parts.append(f"{key}:{value.__class__.__name__}:{value.id}")
        else:
            key_parts.append(f"{key}:{str(value)}")
    
    return ":".join(key_parts)

def cached(ttl: int = 3600, key_prefix: str = ""):
    """캐싱 데코레이터"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key_str = f"{key_prefix}:{cache_key(*args, **kwargs)}"
            
            # 캐시에서 조회
            cached_result = await cache_manager.get(cache_key_str)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key_str}")
                return cached_result
            
            # 캐시 미스 - 함수 실행
            logger.debug(f"Cache miss for key: {cache_key_str}")
            result = await func(*args, **kwargs)
            
            # 결과 캐싱
            await cache_manager.set(cache_key_str, result, ttl)
            
            return result
        
        return wrapper
    return decorator

def cache_invalidate(pattern: str):
    """캐시 무효화 데코레이터"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # 캐시 무효화
            await cache_manager.delete_pattern(pattern)
            logger.debug(f"Cache invalidated for pattern: {pattern}")
            
            return result
        
        return wrapper
    return decorator

# 캐시 키 상수
class CacheKeys:
    """캐시 키 상수"""
    
    # 사용자 관련
    USER_PROFILE = "user:profile"
    USER_SUBSCRIPTION = "user:subscription"
    
    # 구독 관련
    SUBSCRIPTION_PLANS = "subscription:plans"
    SUBSCRIPTION_ACTIVE = "subscription:active"
    
    # AI 관련
    AI_SYSTEM_STATUS = "ai:system:status"
    AI_PREDICTIONS = "ai:predictions"
    
    # 거래 관련
    TRADING_PORTFOLIO = "trading:portfolio"
    TRADING_ORDERS = "trading:orders"
    
    # 모니터링 관련
    MONITORING_METRICS = "monitoring:metrics"
    MONITORING_HEALTH = "monitoring:health"
    
    # 데이터 관련
    MARKET_DATA = "market:data"
    TECHNICAL_INDICATORS = "technical:indicators"

# 캐시 TTL 상수 (초)
class CacheTTL:
    """캐시 TTL 상수"""
    
    # 사용자 관련 (10분)
    USER_PROFILE = 600
    USER_SUBSCRIPTION = 600
    
    # 구독 관련 (1시간)
    SUBSCRIPTION_PLANS = 3600
    SUBSCRIPTION_ACTIVE = 600
    
    # AI 관련 (5분)
    AI_SYSTEM_STATUS = 300
    AI_PREDICTIONS = 300
    
    # 거래 관련 (1분)
    TRADING_PORTFOLIO = 60
    TRADING_ORDERS = 60
    
    # 모니터링 관련 (30초)
    MONITORING_METRICS = 30
    MONITORING_HEALTH = 30
    
    # 데이터 관련 (1분)
    MARKET_DATA = 60
    TECHNICAL_INDICATORS = 300
