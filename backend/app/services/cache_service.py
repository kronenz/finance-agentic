# 캐싱 서비스
import redis
import json
from typing import Any, Optional, Union

class CacheService:
    """캐시 서비스"""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 가져오기"""
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> None:
        """캐시에 데이터 저장"""
        if isinstance(value, (dict, list, tuple, str, int, float, bool)):
            await self.redis.set(key, json.dumps(value), ex=expire)
        else:
            raise TypeError(f"Unsupported type for caching: {type(value)}")

    async def delete(self, key: str) -> None:
        """캐시에서 데이터 삭제"""
        await self.redis.delete(key)

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
