"""
부하 테스트 및 스트레스 테스트
"""

import pytest
import asyncio
import aiohttp
import time
import statistics
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor
import requests

class LoadTester:
    """부하 테스트 클래스"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []
    
    async def single_request(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET", 
                           data: Dict = None) -> Dict[str, Any]:
        """단일 요청 실행"""
        start_time = time.time()
        
        try:
            if method == "GET":
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    content = await response.text()
                    status_code = response.status
            elif method == "POST":
                async with session.post(f"{self.base_url}{endpoint}", json=data) as response:
                    content = await response.text()
                    status_code = response.status
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "duration": duration,
                "success": 200 <= status_code < 300,
                "timestamp": start_time
            }
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "duration": duration,
                "success": False,
                "error": str(e),
                "timestamp": start_time
            }
    
    async def load_test(self, endpoint: str, method: str = "GET", data: Dict = None,
                       concurrent_users: int = 10, duration_seconds: int = 60) -> Dict[str, Any]:
        """부하 테스트 실행"""
        print(f"Starting load test: {endpoint} with {concurrent_users} concurrent users for {duration_seconds}s")
        
        start_time = time.time()
        results = []
        
        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < duration_seconds:
                tasks = []
                for _ in range(concurrent_users):
                    task = self.single_request(session, endpoint, method, data)
                    tasks.append(task)
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                results.extend([r for r in batch_results if isinstance(r, dict)])
                
                # 1초 대기
                await asyncio.sleep(1)
        
        return self._analyze_results(results)
    
    def _analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """결과 분석"""
        if not results:
            return {"error": "No results to analyze"}
        
        durations = [r["duration"] for r in results]
        success_count = sum(1 for r in results if r["success"])
        total_requests = len(results)
        
        return {
            "total_requests": total_requests,
            "successful_requests": success_count,
            "failed_requests": total_requests - success_count,
            "success_rate": success_count / total_requests * 100,
            "avg_response_time": statistics.mean(durations),
            "min_response_time": min(durations),
            "max_response_time": max(durations),
            "median_response_time": statistics.median(durations),
            "p95_response_time": self._percentile(durations, 95),
            "p99_response_time": self._percentile(durations, 99),
            "requests_per_second": total_requests / (max(r["timestamp"] for r in results) - min(r["timestamp"] for r in results)) if results else 0
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """백분위수 계산"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

class StressTester:
    """스트레스 테스트 클래스"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def stress_test(self, endpoint: str, method: str = "GET", data: Dict = None,
                   max_concurrent_users: int = 100, step: int = 10) -> Dict[str, Any]:
        """스트레스 테스트 실행"""
        print(f"Starting stress test: {endpoint} with up to {max_concurrent_users} concurrent users")
        
        results = {}
        
        for concurrent_users in range(step, max_concurrent_users + 1, step):
            print(f"Testing with {concurrent_users} concurrent users...")
            
            start_time = time.time()
            success_count = 0
            total_requests = 0
            response_times = []
            
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = []
                
                for _ in range(concurrent_users * 10):  # 각 사용자당 10개 요청
                    future = executor.submit(self._single_request, endpoint, method, data)
                    futures.append(future)
                
                for future in futures:
                    try:
                        result = future.result(timeout=30)
                        total_requests += 1
                        if result["success"]:
                            success_count += 1
                        response_times.append(result["duration"])
                    except Exception as e:
                        print(f"Request failed: {e}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            results[concurrent_users] = {
                "concurrent_users": concurrent_users,
                "total_requests": total_requests,
                "successful_requests": success_count,
                "failed_requests": total_requests - success_count,
                "success_rate": success_count / total_requests * 100 if total_requests > 0 else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "requests_per_second": total_requests / duration if duration > 0 else 0
            }
            
            # 성공률이 50% 미만이면 중단
            if results[concurrent_users]["success_rate"] < 50:
                print(f"Success rate dropped below 50% at {concurrent_users} concurrent users")
                break
        
        return results
    
    def _single_request(self, endpoint: str, method: str, data: Dict) -> Dict[str, Any]:
        """단일 요청 실행 (동기)"""
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
            elif method == "POST":
                response = requests.post(f"{self.base_url}{endpoint}", json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "duration": duration,
                "success": 200 <= response.status_code < 300
            }
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "duration": duration,
                "success": False,
                "error": str(e)
            }

# 테스트 함수들
@pytest.mark.asyncio
async def test_load_trading_positions():
    """거래 포지션 조회 부하 테스트"""
    tester = LoadTester()
    results = await tester.load_test("/api/v1/trading/positions", concurrent_users=10, duration_seconds=30)
    
    # 성공률이 95% 이상이어야 함
    assert results["success_rate"] >= 95, f"Success rate too low: {results['success_rate']}%"
    
    # 평균 응답 시간이 100ms 이하여야 함
    assert results["avg_response_time"] <= 0.1, f"Average response time too high: {results['avg_response_time']}s"
    
    # P95 응답 시간이 200ms 이하여야 함
    assert results["p95_response_time"] <= 0.2, f"P95 response time too high: {results['p95_response_time']}s"

@pytest.mark.asyncio
async def test_load_market_analysis():
    """시장 분석 부하 테스트"""
    tester = LoadTester()
    results = await tester.load_test("/api/v1/analysis/market-regime", concurrent_users=5, duration_seconds=30)
    
    # 성공률이 90% 이상이어야 함
    assert results["success_rate"] >= 90, f"Success rate too low: {results['success_rate']}%"
    
    # 평균 응답 시간이 200ms 이하여야 함
    assert results["avg_response_time"] <= 0.2, f"Average response time too high: {results['avg_response_time']}s"

@pytest.mark.asyncio
async def test_load_ai_agents():
    """AI 에이전트 상태 조회 부하 테스트"""
    tester = LoadTester()
    results = await tester.load_test("/api/v1/monitoring/agents", concurrent_users=20, duration_seconds=30)
    
    # 성공률이 95% 이상이어야 함
    assert results["success_rate"] >= 95, f"Success rate too low: {results['success_rate']}%"
    
    # 평균 응답 시간이 50ms 이하여야 함
    assert results["avg_response_time"] <= 0.05, f"Average response time too high: {results['avg_response_time']}s"

def test_stress_trading_api():
    """거래 API 스트레스 테스트"""
    tester = StressTester()
    results = tester.stress_test("/api/v1/trading/positions", max_concurrent_users=50, step=5)
    
    # 최대 동시 사용자 수에서도 성공률이 80% 이상이어야 함
    max_users = max(results.keys())
    max_success_rate = results[max_users]["success_rate"]
    assert max_success_rate >= 80, f"Success rate too low at max load: {max_success_rate}%"

def test_stress_market_analysis():
    """시장 분석 스트레스 테스트"""
    tester = StressTester()
    results = tester.stress_test("/api/v1/analysis/market-regime", max_concurrent_users=30, step=5)
    
    # 최대 동시 사용자 수에서도 성공률이 70% 이상이어야 함
    max_users = max(results.keys())
    max_success_rate = results[max_users]["success_rate"]
    assert max_success_rate >= 70, f"Success rate too low at max load: {max_success_rate}%"

def test_stress_ai_agents():
    """AI 에이전트 스트레스 테스트"""
    tester = StressTester()
    results = tester.stress_test("/api/v1/monitoring/agents", max_concurrent_users=100, step=10)
    
    # 최대 동시 사용자 수에서도 성공률이 90% 이상이어야 함
    max_users = max(results.keys())
    max_success_rate = results[max_users]["success_rate"]
    assert max_success_rate >= 90, f"Success rate too low at max load: {max_success_rate}%"

def test_memory_usage_under_load():
    """부하 상태에서 메모리 사용량 테스트"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # 부하 테스트 실행
    tester = LoadTester()
    results = asyncio.run(tester.load_test("/api/v1/trading/positions", concurrent_users=20, duration_seconds=60))
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # 메모리 증가량이 100MB 이하여야 함
    assert memory_increase <= 100 * 1024 * 1024, f"Memory increase too high: {memory_increase / 1024 / 1024:.2f}MB"

def test_cpu_usage_under_load():
    """부하 상태에서 CPU 사용량 테스트"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    # 부하 테스트 실행
    tester = LoadTester()
    results = asyncio.run(tester.load_test("/api/v1/trading/positions", concurrent_users=20, duration_seconds=60))
    
    # CPU 사용률이 80% 이하여야 함
    cpu_percent = process.cpu_percent()
    assert cpu_percent <= 80, f"CPU usage too high: {cpu_percent}%"

if __name__ == "__main__":
    # 부하 테스트 실행
    print("Running load tests...")
    
    # 거래 포지션 조회 부하 테스트
    tester = LoadTester()
    results = asyncio.run(tester.load_test("/api/v1/trading/positions", concurrent_users=10, duration_seconds=30))
    print(f"Trading positions load test: {results}")
    
    # 시장 분석 부하 테스트
    results = asyncio.run(tester.load_test("/api/v1/analysis/market-regime", concurrent_users=5, duration_seconds=30))
    print(f"Market analysis load test: {results}")
    
    # AI 에이전트 상태 조회 부하 테스트
    results = asyncio.run(tester.load_test("/api/v1/monitoring/agents", concurrent_users=20, duration_seconds=30))
    print(f"AI agents load test: {results}")
    
    # 스트레스 테스트 실행
    print("\nRunning stress tests...")
    
    stress_tester = StressTester()
    results = stress_tester.stress_test("/api/v1/trading/positions", max_concurrent_users=50, step=5)
    print(f"Trading API stress test: {results}")
    
    results = stress_tester.stress_test("/api/v1/analysis/market-regime", max_concurrent_users=30, step=5)
    print(f"Market analysis stress test: {results}")
    
    results = stress_tester.stress_test("/api/v1/monitoring/agents", max_concurrent_users=100, step=10)
    print(f"AI agents stress test: {results}")
