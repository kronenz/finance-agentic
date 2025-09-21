# 성능 테스트 및 벤치마크
import pytest
import asyncio
import time
import statistics
from httpx import AsyncClient
from concurrent.futures import ThreadPoolExecutor
import psutil
import os
from typing import List, Dict, Any

from app.main import app

class PerformanceTestSuite:
    """성능 테스트 스위트"""
    
    def __init__(self):
        self.results: Dict[str, List[float]] = {}
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
    
    async def measure_response_time(self, client: AsyncClient, endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> float:
        """응답 시간 측정"""
        start_time = time.time()
        
        if method == "GET":
            response = await client.get(endpoint)
        elif method == "POST":
            response = await client.post(endpoint, json=data)
        elif method == "PUT":
            response = await client.put(endpoint, json=data)
        elif method == "DELETE":
            response = await client.delete(endpoint)
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # 밀리초로 변환
        
        # 메모리 및 CPU 사용량 기록
        self.memory_usage.append(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024)  # MB
        self.cpu_usage.append(psutil.cpu_percent())
        
        return response_time
    
    def record_result(self, test_name: str, response_time: float):
        """테스트 결과 기록"""
        if test_name not in self.results:
            self.results[test_name] = []
        self.results[test_name].append(response_time)
    
    def get_statistics(self, test_name: str) -> Dict[str, float]:
        """통계 계산"""
        if test_name not in self.results:
            return {}
        
        times = self.results[test_name]
        return {
            "min": min(times),
            "max": max(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "p95": self.percentile(times, 95),
            "p99": self.percentile(times, 99),
            "std": statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def percentile(self, data: List[float], percentile: int) -> float:
        """백분위수 계산"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

@pytest.fixture
async def performance_suite():
    """성능 테스트 스위트 생성"""
    return PerformanceTestSuite()

@pytest.fixture
async def test_client():
    """테스트 클라이언트 생성"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

class TestAPIPerformance:
    """API 성능 테스트"""
    
    async def test_auth_endpoints_performance(self, test_client: AsyncClient, performance_suite: PerformanceTestSuite):
        """인증 엔드포인트 성능 테스트"""
        # 등록 성능 테스트
        for i in range(10):
            register_data = {
                "email": f"perf_test_{i}@example.com",
                "password": "testpassword123",
                "first_name": "Performance",
                "last_name": "Test"
            }
            
            response_time = await performance_suite.measure_response_time(
                test_client, "/api/v1/auth/register", "POST", register_data
            )
            performance_suite.record_result("auth_register", response_time)
        
        # 로그인 성능 테스트
        for i in range(10):
            login_data = {
                "username": f"perf_test_{i}@example.com",
                "password": "testpassword123"
            }
            
            response_time = await performance_suite.measure_response_time(
                test_client, "/api/v1/auth/login", "POST", login_data
            )
            performance_suite.record_result("auth_login", response_time)
        
        # 통계 출력
        register_stats = performance_suite.get_statistics("auth_register")
        login_stats = performance_suite.get_statistics("auth_login")
        
        print(f"\nAuth Register Performance:")
        print(f"  Mean: {register_stats['mean']:.2f}ms")
        print(f"  P95: {register_stats['p95']:.2f}ms")
        print(f"  P99: {register_stats['p99']:.2f}ms")
        
        print(f"\nAuth Login Performance:")
        print(f"  Mean: {login_stats['mean']:.2f}ms")
        print(f"  P95: {login_stats['p95']:.2f}ms")
        print(f"  P99: {login_stats['p99']:.2f}ms")
        
        # 성능 기준 검증
        assert register_stats['mean'] < 1000, "Auth register should be under 1000ms"
        assert login_stats['mean'] < 500, "Auth login should be under 500ms"
    
    async def test_subscription_endpoints_performance(self, test_client: AsyncClient, performance_suite: PerformanceTestSuite):
        """구독 엔드포인트 성능 테스트"""
        # 구독 플랜 조회 성능 테스트
        for _ in range(20):
            response_time = await performance_suite.measure_response_time(
                test_client, "/api/v1/subscriptions/plans"
            )
            performance_suite.record_result("subscription_plans", response_time)
        
        # 통계 출력
        stats = performance_suite.get_statistics("subscription_plans")
        
        print(f"\nSubscription Plans Performance:")
        print(f"  Mean: {stats['mean']:.2f}ms")
        print(f"  P95: {stats['p95']:.2f}ms")
        print(f"  P99: {stats['p99']:.2f}ms")
        
        # 성능 기준 검증
        assert stats['mean'] < 200, "Subscription plans should be under 200ms"
    
    async def test_ai_endpoints_performance(self, test_client: AsyncClient, performance_suite: PerformanceTestSuite):
        """AI 엔드포인트 성능 테스트"""
        # 시장 분석 성능 테스트
        market_data = {
            "symbol": "BTCUSDT",
            "price_data": [
                {"open": 50000, "high": 51000, "low": 49000, "close": 50500, "volume": 1000000}
                for _ in range(100)
            ],
            "update_model": False
        }
        
        for _ in range(10):
            response_time = await performance_suite.measure_response_time(
                test_client, "/api/v1/ai/market/analyze", "POST", market_data
            )
            performance_suite.record_result("ai_market_analyze", response_time)
        
        # 전략 추천 성능 테스트
        for _ in range(10):
            response_time = await performance_suite.measure_response_time(
                test_client, "/api/v1/ai/strategies/recommend", "POST", {}
            )
            performance_suite.record_result("ai_strategies_recommend", response_time)
        
        # 통계 출력
        market_stats = performance_suite.get_statistics("ai_market_analyze")
        strategy_stats = performance_suite.get_statistics("ai_strategies_recommend")
        
        print(f"\nAI Market Analysis Performance:")
        print(f"  Mean: {market_stats['mean']:.2f}ms")
        print(f"  P95: {market_stats['p95']:.2f}ms")
        print(f"  P99: {market_stats['p99']:.2f}ms")
        
        print(f"\nAI Strategy Recommendation Performance:")
        print(f"  Mean: {strategy_stats['mean']:.2f}ms")
        print(f"  P95: {strategy_stats['p95']:.2f}ms")
        print(f"  P99: {strategy_stats['p99']:.2f}ms")
        
        # 성능 기준 검증
        assert market_stats['mean'] < 2000, "AI market analysis should be under 2000ms"
        assert strategy_stats['mean'] < 1000, "AI strategy recommendation should be under 1000ms"

class TestConcurrencyPerformance:
    """동시성 성능 테스트"""
    
    async def test_concurrent_requests(self, test_client: AsyncClient, performance_suite: PerformanceTestSuite):
        """동시 요청 성능 테스트"""
        async def make_request():
            start_time = time.time()
            response = await test_client.get("/api/v1/subscriptions/plans")
            end_time = time.time()
            return (end_time - start_time) * 1000, response.status_code
        
        # 동시 요청 수: 10, 50, 100
        for concurrent_requests in [10, 50, 100]:
            print(f"\nTesting {concurrent_requests} concurrent requests...")
            
            tasks = [make_request() for _ in range(concurrent_requests)]
            results = await asyncio.gather(*tasks)
            
            response_times = [result[0] for result in results]
            status_codes = [result[1] for result in results]
            
            # 성공률 계산
            success_rate = sum(1 for code in status_codes if code == 200) / len(status_codes) * 100
            
            # 통계 계산
            mean_time = statistics.mean(response_times)
            p95_time = performance_suite.percentile(response_times, 95)
            p99_time = performance_suite.percentile(response_times, 99)
            
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Mean Response Time: {mean_time:.2f}ms")
            print(f"  P95 Response Time: {p95_time:.2f}ms")
            print(f"  P99 Response Time: {p99_time:.2f}ms")
            
            # 성능 기준 검증
            assert success_rate >= 95, f"Success rate should be at least 95% for {concurrent_requests} concurrent requests"
            assert mean_time < 1000, f"Mean response time should be under 1000ms for {concurrent_requests} concurrent requests"
    
    async def test_memory_usage_under_load(self, test_client: AsyncClient, performance_suite: PerformanceTestSuite):
        """부하 상태에서 메모리 사용량 테스트"""
        initial_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        # 1000번의 요청 실행
        tasks = []
        for _ in range(1000):
            task = test_client.get("/api/v1/subscriptions/plans")
            tasks.append(task)
        
        # 요청 실행
        responses = await asyncio.gather(*tasks)
        
        final_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"\nMemory Usage Test:")
        print(f"  Initial Memory: {initial_memory:.2f}MB")
        print(f"  Final Memory: {final_memory:.2f}MB")
        print(f"  Memory Increase: {memory_increase:.2f}MB")
        
        # 메모리 사용량 기준 검증
        assert memory_increase < 100, "Memory increase should be less than 100MB for 1000 requests"
        
        # 응답 상태 확인
        success_count = sum(1 for response in responses if response.status_code == 200)
        success_rate = success_count / len(responses) * 100
        assert success_rate >= 95, "Success rate should be at least 95%"

class TestDatabasePerformance:
    """데이터베이스 성능 테스트"""
    
    async def test_database_query_performance(self, async_session):
        """데이터베이스 쿼리 성능 테스트"""
        from sqlalchemy import select
        from app.models.user import User
        
        # 사용자 생성
        users = []
        for i in range(100):
            user = User(
                email=f"db_perf_test_{i}@example.com",
                hashed_password="hashed_password",
                is_active=True,
                is_verified=True
            )
            users.append(user)
        
        async_session.add_all(users)
        await async_session.commit()
        
        # 쿼리 성능 테스트
        query_times = []
        
        for _ in range(10):
            start_time = time.time()
            
            result = await async_session.execute(select(User).where(User.is_active == True))
            users = result.scalars().all()
            
            end_time = time.time()
            query_time = (end_time - start_time) * 1000
            query_times.append(query_time)
        
        mean_query_time = statistics.mean(query_times)
        p95_query_time = performance_suite.percentile(query_times, 95)
        
        print(f"\nDatabase Query Performance:")
        print(f"  Mean Query Time: {mean_query_time:.2f}ms")
        print(f"  P95 Query Time: {p95_query_time:.2f}ms")
        print(f"  Records Retrieved: {len(users)}")
        
        # 성능 기준 검증
        assert mean_query_time < 100, "Database query should be under 100ms"
        assert p95_query_time < 200, "P95 database query should be under 200ms"

class TestCachePerformance:
    """캐시 성능 테스트"""
    
    async def test_cache_hit_performance(self, performance_suite: PerformanceTestSuite):
        """캐시 히트 성능 테스트"""
        from app.services.cache_service import cache_service
        
        # 캐시 설정
        test_key = "performance_test_cache"
        test_value = {"data": "test", "timestamp": time.time()}
        
        await cache_service.set(test_key, test_value, ttl=60)
        
        # 캐시 히트 성능 테스트
        hit_times = []
        for _ in range(100):
            start_time = time.time()
            await cache_service.get(test_key)
            end_time = time.time()
            hit_times.append((end_time - start_time) * 1000)
        
        mean_hit_time = statistics.mean(hit_times)
        p95_hit_time = performance_suite.percentile(hit_times, 95)
        
        print(f"\nCache Hit Performance:")
        print(f"  Mean Hit Time: {mean_hit_time:.2f}ms")
        print(f"  P95 Hit Time: {p95_hit_time:.2f}ms")
        
        # 성능 기준 검증
        assert mean_hit_time < 10, "Cache hit should be under 10ms"
        assert p95_hit_time < 20, "P95 cache hit should be under 20ms"
    
    async def test_cache_miss_performance(self, performance_suite: PerformanceTestSuite):
        """캐시 미스 성능 테스트"""
        from app.services.cache_service import cache_service
        
        # 캐시 미스 성능 테스트
        miss_times = []
        for i in range(100):
            start_time = time.time()
            await cache_service.get(f"nonexistent_key_{i}")
            end_time = time.time()
            miss_times.append((end_time - start_time) * 1000)
        
        mean_miss_time = statistics.mean(miss_times)
        p95_miss_time = performance_suite.percentile(miss_times, 95)
        
        print(f"\nCache Miss Performance:")
        print(f"  Mean Miss Time: {mean_miss_time:.2f}ms")
        print(f"  P95 Miss Time: {p95_miss_time:.2f}ms")
        
        # 성능 기준 검증
        assert mean_miss_time < 5, "Cache miss should be under 5ms"
        assert p95_miss_time < 10, "P95 cache miss should be under 10ms"

# 성능 테스트 실행을 위한 헬퍼 함수
async def run_performance_tests():
    """성능 테스트 실행"""
    print("Running performance tests...")
    
    # 테스트 실행
    pytest.main(["-v", "tests/test_performance.py", "-s"])
    
    print("Performance tests completed!")

if __name__ == "__main__":
    asyncio.run(run_performance_tests())
