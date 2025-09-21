# 캐싱 서비스
import redis
import json
import pickle
from typing import Any, Optional, Union
from datetime import datetime, timedelta
import structlog

from app.core.config import settings

# 로거 설정
logger = structlog.get_logger()

class CacheService:
    """Redis 기반 캐싱 서비스"""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        self.default_ttl = 3600  # 1시간 기본 TTL
    
    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # JSON 파싱 시도
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # JSON이 아닌 경우 pickle로 시도
                return pickle.loads(value)
                
        except Exception as e:
            logger.error("Failed to get cache value", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """캐시에 값 저장"""
        try:
            ttl = ttl or self.default_ttl
            
            # JSON 직렬화 시도
            try:
                serialized_value = json.dumps(value)
            except (TypeError, ValueError):
                # JSON 직렬화 실패 시 pickle 사용
                serialized_value = pickle.dumps(value)
            
            result = self.redis_client.setex(key, ttl, serialized_value)
            
            if result:
                logger.debug("Cache value set", key=key, ttl=ttl)
            
            return bool(result)
            
        except Exception as e:
            logger.error("Failed to set cache value", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """캐시에서 값 삭제"""
        try:
            result = self.redis_client.delete(key)
            logger.debug("Cache value deleted", key=key)
            return bool(result)
        except Exception as e:
            logger.error("Failed to delete cache value", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """캐시 키 존재 여부 확인"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error("Failed to check cache key existence", key=key, error=str(e))
            return False
    
    async def get_or_set(self, key: str, factory_func, ttl: Optional[int] = None) -> Any:
        """캐시에서 조회하고 없으면 팩토리 함수로 생성하여 저장"""
        try:
            # 캐시에서 조회
            value = await self.get(key)
            if value is not None:
                return value
            
            # 팩토리 함수로 값 생성
            value = await factory_func()
            
            # 캐시에 저장
            await self.set(key, value, ttl)
            
            return value
            
        except Exception as e:
            logger.error("Failed to get or set cache value", key=key, error=str(e))
            # 팩토리 함수로 값 생성 (캐시 실패 시)
            return await factory_func()
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """패턴에 맞는 캐시 키들 삭제"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted_count = self.redis_client.delete(*keys)
                logger.info("Cache keys deleted by pattern", pattern=pattern, count=deleted_count)
                return deleted_count
            return 0
        except Exception as e:
            logger.error("Failed to invalidate cache pattern", pattern=pattern, error=str(e))
            return 0
    
    async def get_ttl(self, key: str) -> int:
        """캐시 키의 TTL 조회"""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error("Failed to get cache TTL", key=key, error=str(e))
            return -1
    
    async def extend_ttl(self, key: str, ttl: int) -> bool:
        """캐시 키의 TTL 연장"""
        try:
            result = self.redis_client.expire(key, ttl)
            logger.debug("Cache TTL extended", key=key, ttl=ttl)
            return bool(result)
        except Exception as e:
            logger.error("Failed to extend cache TTL", key=key, error=str(e))
            return False

# 전역 캐시 서비스 인스턴스
cache_service = CacheService()

# 캐시 데코레이터
def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """함수 결과를 캐시하는 데코레이터"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 캐시에서 조회
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug("Cache hit", function=func.__name__, key=cache_key)
                return cached_result
            
            # 함수 실행
            result = await func(*args, **kwargs)
            
            # 결과 캐시
            await cache_service.set(cache_key, result, ttl)
            logger.debug("Cache miss", function=func.__name__, key=cache_key)
            
            return result
        return wrapper
    return decorator

# 특정 도메인별 캐시 키 생성 함수들
def get_user_cache_key(user_id: str, suffix: str = "") -> str:
    """사용자 관련 캐시 키 생성"""
    return f"user:{user_id}:{suffix}" if suffix else f"user:{user_id}"

def get_market_cache_key(symbol: str, timeframe: str = "1h") -> str:
    """시장 데이터 캐시 키 생성"""
    return f"market:{symbol}:{timeframe}"

def get_strategy_cache_key(user_id: str, strategy_id: str) -> str:
    """전략 관련 캐시 키 생성"""
    return f"strategy:{user_id}:{strategy_id}"

def get_ai_cache_key(model_type: str, input_hash: str) -> str:
    """AI 모델 결과 캐시 키 생성"""
    return f"ai:{model_type}:{input_hash}"

# 캐시 무효화 헬퍼 함수들
async def invalidate_user_cache(user_id: str) -> None:
    """사용자 관련 캐시 무효화"""
    await cache_service.invalidate_pattern(f"user:{user_id}:*")

async def invalidate_market_cache(symbol: str) -> None:
    """시장 데이터 캐시 무효화"""
    await cache_service.invalidate_pattern(f"market:{symbol}:*")

async def invalidate_strategy_cache(user_id: str) -> None:
    """전략 관련 캐시 무효화"""
    await cache_service.invalidate_pattern(f"strategy:{user_id}:*")

async def invalidate_ai_cache(model_type: str) -> None:
    """AI 모델 결과 캐시 무효화"""
    await cache_service.invalidate_pattern(f"ai:{model_type}:*")
