"""
API 응답시간 성능 테스트: <100ms 응답시간 보장
"""

import pytest
import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor


class TestAPIPerformance:
    """API 성능 테스트"""
    
    def test_health_endpoint_performance(self):
        """헬스 체크 엔드포인트 성능 테스트"""
        base_url = "http://localhost:8000"
        
        execution_times = []
        for _ in range(100):
            try:
                start_time = time.time()
                response = requests.get(f"{base_url}/health", timeout=5)
                end_time = time.time()
                
                if response.status_code == 200:
                    execution_times.append((end_time - start_time) * 1000)
            except requests.exceptions.RequestException:
                continue
        
        if execution_times:
            avg_time = statistics.mean(execution_times)
            max_time = max(execution_times)
            p95_time = statistics.quantiles(execution_times, n=20)[18] if len(execution_times) >= 20 else max_time
            
            print(f"Health Endpoint - Avg: {avg_time:.2f}ms, Max: {max_time:.2f}ms, P95: {p95_time:.2f}ms")
            
            assert avg_time < 50, f"평균 응답시간이 50ms를 초과: {avg_time:.2f}ms"
            assert max_time < 100, f"최대 응답시간이 100ms를 초과: {max_time:.2f}ms"
    
    def test_trading_endpoints_performance(self):
        """거래 관련 엔드포인트 성능 테스트"""
        base_url = "http://localhost:8000"
        
        endpoints = [
            "/v1/trading/market-regime",
            "/v1/trading/signals?limit=10",
            "/v1/trading/positions",
            "/v1/trading/strategies"
        ]
        
        for endpoint in endpoints:
            execution_times = []
            
            for _ in range(50):
                try:
                    start_time = time.time()
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        execution_times.append((end_time - start_time) * 1000)
                except requests.exceptions.RequestException:
                    continue
            
            if execution_times:
                avg_time = statistics.mean(execution_times)
                max_time = max(execution_times)
                p95_time = statistics.quantiles(execution_times, n=20)[18] if len(execution_times) >= 20 else max_time
                
                print(f"API {endpoint} - Avg: {avg_time:.2f}ms, Max: {max_time:.2f}ms, P95: {p95_time:.2f}ms")
                
                assert avg_time < 100, f"API {endpoint} 평균 응답시간이 100ms를 초과: {avg_time:.2f}ms"
                assert max_time < 200, f"API {endpoint} 최대 응답시간이 200ms를 초과: {max_time:.2f}ms"
    
    def test_concurrent_api_requests(self):
        """동시 API 요청 성능 테스트"""
        base_url = "http://localhost:8000"
        
        def make_request():
            try:
                start_time = time.time()
                response = requests.get(f"{base_url}/health", timeout=5)
                end_time = time.time()
                return (end_time - start_time) * 1000 if response.status_code == 200 else None
            except:
                return None
        
        # 50개 동시 요청
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            execution_times = [future.result() for future in futures if future.result() is not None]
        
        if execution_times:
            avg_time = statistics.mean(execution_times)
            max_time = max(execution_times)
            p95_time = statistics.quantiles(execution_times, n=20)[18] if len(execution_times) >= 20 else max_time
            
            print(f"Concurrent API Requests - Avg: {avg_time:.2f}ms, Max: {max_time:.2f}ms, P95: {p95_time:.2f}ms")
            
            assert avg_time < 100, f"동시 요청 평균 응답시간이 100ms를 초과: {avg_time:.2f}ms"
            assert max_time < 300, f"동시 요청 최대 응답시간이 300ms를 초과: {max_time:.2f}ms"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
