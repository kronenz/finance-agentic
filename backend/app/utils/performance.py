"""
성능 최적화 유틸리티
"""

import time
import functools
import asyncio
from typing import Any, Callable, Dict, List, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.execution_times: Dict[str, List[float]] = {}
    
    def record_execution_time(self, operation: str, duration: float):
        """실행 시간 기록"""
        if operation not in self.execution_times:
            self.execution_times[operation] = []
        self.execution_times[operation].append(duration)
        
        # 최근 100개만 유지
        if len(self.execution_times[operation]) > 100:
            self.execution_times[operation] = self.execution_times[operation][-100:]
    
    def get_average_time(self, operation: str) -> float:
        """평균 실행 시간 조회"""
        if operation not in self.execution_times:
            return 0.0
        return sum(self.execution_times[operation]) / len(self.execution_times[operation])
    
    def get_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """성능 통계 조회"""
        stats = {}
        for operation, times in self.execution_times.items():
            if times:
                stats[operation] = {
                    'avg': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
        return stats

# 전역 성능 모니터
performance_monitor = PerformanceMonitor()

def measure_time(operation: str = None):
    """실행 시간 측정 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                op_name = operation or f"{func.__module__}.{func.__name__}"
                performance_monitor.record_execution_time(op_name, duration)
                logger.debug(f"{op_name} executed in {duration:.4f}s")
        return wrapper
    return decorator

def measure_async_time(operation: str = None):
    """비동기 함수 실행 시간 측정 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                op_name = operation or f"{func.__module__}.{func.__name__}"
                performance_monitor.record_execution_time(op_name, duration)
                logger.debug(f"{op_name} executed in {duration:.4f}s")
        return wrapper
    return decorator

class AsyncTaskPool:
    """비동기 작업 풀 관리자"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
    
    async def execute(self, coro, *args, **kwargs):
        """세마포어를 사용한 비동기 작업 실행"""
        async with self.semaphore:
            return await coro(*args, **kwargs)
    
    async def execute_batch(self, coros: List[Callable], *args, **kwargs):
        """배치 비동기 작업 실행"""
        tasks = [self.execute(coro, *args, **kwargs) for coro in coros]
        return await asyncio.gather(*tasks, return_exceptions=True)

class ThreadPool:
    """스레드 풀 관리자"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (mp.cpu_count() or 1) + 4)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
    
    def submit(self, func: Callable, *args, **kwargs):
        """스레드 풀에 작업 제출"""
        return self.executor.submit(func, *args, **kwargs)
    
    def map(self, func: Callable, iterable, timeout: Optional[float] = None):
        """스레드 풀을 사용한 맵 연산"""
        return self.executor.map(func, iterable, timeout=timeout)
    
    def shutdown(self, wait: bool = True):
        """스레드 풀 종료"""
        self.executor.shutdown(wait=wait)

class ProcessPool:
    """프로세스 풀 관리자"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or mp.cpu_count()
        self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
    
    def submit(self, func: Callable, *args, **kwargs):
        """프로세스 풀에 작업 제출"""
        return self.executor.submit(func, *args, **kwargs)
    
    def map(self, func: Callable, iterable, timeout: Optional[float] = None):
        """프로세스 풀을 사용한 맵 연산"""
        return self.executor.map(func, iterable, timeout=timeout)
    
    def shutdown(self, wait: bool = True):
        """프로세스 풀 종료"""
        self.executor.shutdown(wait=wait)

class MemoryOptimizer:
    """메모리 최적화 유틸리티"""
    
    @staticmethod
    def clear_memory():
        """메모리 정리"""
        import gc
        gc.collect()
    
    @staticmethod
    def get_memory_usage():
        """메모리 사용량 조회"""
        import psutil
        process = psutil.Process()
        return {
            'rss': process.memory_info().rss,  # 물리 메모리
            'vms': process.memory_info().vms,  # 가상 메모리
            'percent': process.memory_percent()
        }
    
    @staticmethod
    def optimize_dataframe(df):
        """데이터프레임 메모리 최적화"""
        import pandas as pd
        
        # 숫자 타입 최적화
        for col in df.select_dtypes(include=['int64']).columns:
            if df[col].min() >= 0:
                if df[col].max() < 255:
                    df[col] = df[col].astype('uint8')
                elif df[col].max() < 65535:
                    df[col] = df[col].astype('uint16')
                elif df[col].max() < 4294967295:
                    df[col] = df[col].astype('uint32')
            else:
                if df[col].min() > -128 and df[col].max() < 127:
                    df[col] = df[col].astype('int8')
                elif df[col].min() > -32768 and df[col].max() < 32767:
                    df[col] = df[col].astype('int16')
                elif df[col].min() > -2147483648 and df[col].max() < 2147483647:
                    df[col] = df[col].astype('int32')
        
        # 부동소수점 타입 최적화
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        # 카테고리 타입 최적화
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.5:  # 50% 미만의 고유값
                df[col] = df[col].astype('category')
        
        return df

class CacheManager:
    """캐시 관리자"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if time.time() - entry['timestamp'] > self.ttl:
            del self.cache[key]
            return None
        
        return entry['value']
    
    def set(self, key: str, value: Any):
        """캐시에 값 저장"""
        if len(self.cache) >= self.max_size:
            # LRU 방식으로 오래된 항목 제거
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def clear(self):
        """캐시 초기화"""
        self.cache.clear()
    
    def cleanup_expired(self):
        """만료된 캐시 항목 정리"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] > self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]

# 전역 캐시 관리자
cache_manager = CacheManager()

def cached(ttl: int = 3600):
    """캐시 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 캐시에서 조회
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 함수 실행 및 결과 캐시
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result)
            return result
        return wrapper
    return decorator

class BatchProcessor:
    """배치 처리 유틸리티"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
    
    def process_batches(self, items: List[Any], processor: Callable) -> List[Any]:
        """배치 단위로 처리"""
        results = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = processor(batch)
            results.extend(batch_results)
        return results
    
    async def process_batches_async(self, items: List[Any], processor: Callable) -> List[Any]:
        """비동기 배치 처리"""
        results = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = await processor(batch)
            results.extend(batch_results)
        return results

# 전역 배치 프로세서
batch_processor = BatchProcessor()

def optimize_performance():
    """성능 최적화 실행"""
    # 메모리 정리
    MemoryOptimizer.clear_memory()
    
    # 만료된 캐시 정리
    cache_manager.cleanup_expired()
    
    # 성능 통계 로깅
    stats = performance_monitor.get_performance_stats()
    for operation, metrics in stats.items():
        logger.info(f"Performance stats for {operation}: {metrics}")
    
    logger.info("Performance optimization completed")
