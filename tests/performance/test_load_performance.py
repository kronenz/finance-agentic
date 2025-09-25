# 성능 테스트: 부하 및 스트레스 테스트
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
import json
from datetime import datetime

class PerformanceTestRunner:
    """성능 테스트 실행기"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.start_time = None
        self.end_time = None
    
    async def create_test_user(self, session: aiohttp.ClientSession, user_id: int) -> str:
        """테스트 사용자 생성 및 토큰 획득"""
        email = f"perf_test_user_{user_id}@example.com"
        password = "TestPassword123!"
        
        # 사용자 등록
        register_data = {
            "first_name": f"Test{user_id}",
            "last_name": "User",
            "email": email,
            "password": password,
            "agreeToTerms": True
        }
        
        try:
            async with session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=register_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status not in [201, 409]:  # 409는 이미 존재하는 사용자
                    print(f"User {user_id} registration failed: {response.status}")
                    return None
        except Exception as e:
            print(f"User {user_id} registration error: {e}")
            return None
        
        # 로그인
        login_data = {
            "email": email,
            "password": password
        }
        
        try:
            async with session.post(
                f"{self.base_url}/api/v1/auth/login",
                data=login_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("access_token")
                else:
                    print(f"User {user_id} login failed: {response.status}")
                    return None
        except Exception as e:
            print(f"User {user_id} login error: {e}")
            return None
    
    async def make_api_request(self, session: aiohttp.ClientSession, 
                             method: str, url: str, headers: Dict[str, str] = None,
                             data: Dict[str, Any] = None, json_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """API 요청 실행 및 성능 측정"""
        start_time = time.time()
        
        try:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # ms
                
                # 응답 본문 읽기
                try:
                    response_body = await response.json()
                except:
                    response_body = await response.text()
                
                return {
                    "status_code": response.status,
                    "response_time": response_time,
                    "success": 200 <= response.status < 300,
                    "response_body": response_body,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                "status_code": 0,
                "response_time": response_time,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def load_test_login(self, concurrent_users: int, requests_per_user: int):
        """로그인 부하 테스트"""
        print(f"Starting login load test: {concurrent_users} users, {requests_per_user} requests each")
        
        async def user_workload(user_id: int):
            async with aiohttp.ClientSession() as session:
                results = []
                
                for i in range(requests_per_user):
                    login_data = {
                        "email": f"perf_test_user_{user_id}@example.com",
                        "password": "TestPassword123!"
                    }
                    
                    result = await self.make_api_request(
                        session, "POST", f"{self.base_url}/api/v1/auth/login", data=login_data
                    )
                    results.append(result)
                
                return results
        
        # 동시 사용자 실행
        tasks = [user_workload(i) for i in range(concurrent_users)]
        user_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 집계
        all_results = []
        for user_result in user_results:
            if isinstance(user_result, Exception):
                print(f"User workload failed: {user_result}")
                continue
            all_results.extend(user_result)
        
        return self.analyze_results(all_results, "Login Load Test")
    
    async def load_test_api_endpoints(self, concurrent_users: int, requests_per_user: int):
        """API 엔드포인트 부하 테스트"""
        print(f"Starting API endpoints load test: {concurrent_users} users, {requests_per_user} requests each")
        
        async def user_workload(user_id: int):
            async with aiohttp.ClientSession() as session:
                # 사용자 생성 및 토큰 획득
                token = await self.create_test_user(session, user_id)
                if not token:
                    return []
                
                headers = {"Authorization": f"Bearer {token}"}
                results = []
                
                # 다양한 API 엔드포인트 테스트
                endpoints = [
                    ("GET", "/api/v1/ai/status"),
                    ("GET", "/api/v1/trading/portfolio"),
                    ("GET", "/api/v1/subscriptions/plans"),
                    ("GET", "/api/v1/monitoring/metrics"),
                    ("GET", "/api/v1/monitoring/health"),
                ]
                
                for i in range(requests_per_user):
                    method, endpoint = endpoints[i % len(endpoints)]
                    url = f"{self.base_url}{endpoint}"
                    
                    result = await self.make_api_request(
                        session, method, url, headers=headers
                    )
                    results.append(result)
                
                return results
        
        # 동시 사용자 실행
        tasks = [user_workload(i) for i in range(concurrent_users)]
        user_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 집계
        all_results = []
        for user_result in user_results:
            if isinstance(user_result, Exception):
                print(f"User workload failed: {user_result}")
                continue
            all_results.extend(user_result)
        
        return self.analyze_results(all_results, "API Endpoints Load Test")
    
    async def stress_test(self, max_users: int, step: int = 50):
        """스트레스 테스트"""
        print(f"Starting stress test: up to {max_users} users, step {step}")
        
        results = []
        
        for users in range(step, max_users + 1, step):
            print(f"Testing with {users} concurrent users...")
            
            start_time = time.time()
            result = await self.load_test_api_endpoints(users, 5)
            end_time = time.time()
            
            result["concurrent_users"] = users
            result["test_duration"] = end_time - start_time
            results.append(result)
            
            # 에러율이 5%를 초과하면 중단
            if result["error_rate"] > 5.0:
                print(f"Error rate exceeded 5% at {users} users: {result['error_rate']:.2f}%")
                break
            
            # 응답 시간이 5초를 초과하면 중단
            if result["avg_response_time"] > 5000:
                print(f"Response time exceeded 5s at {users} users: {result['avg_response_time']:.2f}ms")
                break
        
        return results
    
    async def spike_test(self, base_users: int = 100, spike_users: int = 300):
        """스파이크 테스트"""
        print(f"Starting spike test: base {base_users} users, spike {spike_users} users")
        
        results = []
        
        # 1. 기본 부하 (5분)
        print("Phase 1: Base load")
        base_result = await self.load_test_api_endpoints(base_users, 10)
        base_result["phase"] = "base_load"
        results.append(base_result)
        
        # 2. 스파이크 부하 (2분)
        print("Phase 2: Spike load")
        spike_result = await self.load_test_api_endpoints(spike_users, 5)
        spike_result["phase"] = "spike_load"
        results.append(spike_result)
        
        # 3. 기본 부하로 복구 (3분)
        print("Phase 3: Recovery")
        recovery_result = await self.load_test_api_endpoints(base_users, 10)
        recovery_result["phase"] = "recovery"
        results.append(recovery_result)
        
        return results
    
    def analyze_results(self, results: List[Dict[str, Any]], test_name: str) -> Dict[str, Any]:
        """테스트 결과 분석"""
        if not results:
            return {"error": "No results to analyze"}
        
        response_times = [r["response_time"] for r in results if r["success"]]
        success_count = sum(1 for r in results if r["success"])
        total_count = len(results)
        error_count = total_count - success_count
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = self.percentile(response_times, 95)
            p99_response_time = self.percentile(response_times, 99)
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        success_rate = (success_count / total_count) * 100
        error_rate = (error_count / total_count) * 100
        
        return {
            "test_name": test_name,
            "total_requests": total_count,
            "successful_requests": success_count,
            "failed_requests": error_count,
            "success_rate": success_rate,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "min_response_time": min_response_time,
            "max_response_time": max_response_time,
            "p95_response_time": p95_response_time,
            "p99_response_time": p99_response_time,
            "requests_per_second": total_count / (self.end_time - self.start_time) if self.end_time and self.start_time else 0
        }
    
    def percentile(self, data: List[float], percentile: int) -> float:
        """백분위수 계산"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def print_results(self, results: Dict[str, Any]):
        """결과 출력"""
        print(f"\n=== {results['test_name']} Results ===")
        print(f"Total Requests: {results['total_requests']}")
        print(f"Successful Requests: {results['successful_requests']}")
        print(f"Failed Requests: {results['failed_requests']}")
        print(f"Success Rate: {results['success_rate']:.2f}%")
        print(f"Error Rate: {results['error_rate']:.2f}%")
        print(f"Average Response Time: {results['avg_response_time']:.2f}ms")
        print(f"Min Response Time: {results['min_response_time']:.2f}ms")
        print(f"Max Response Time: {results['max_response_time']:.2f}ms")
        print(f"95th Percentile: {results['p95_response_time']:.2f}ms")
        print(f"99th Percentile: {results['p99_response_time']:.2f}ms")
        print(f"Requests Per Second: {results['requests_per_second']:.2f}")
        print("=" * 50)

async def main():
    """메인 테스트 실행"""
    runner = PerformanceTestRunner()
    
    print("Starting Performance Tests...")
    print("=" * 50)
    
    # 1. 로그인 부하 테스트
    runner.start_time = time.time()
    login_results = await runner.load_test_login(50, 10)
    runner.end_time = time.time()
    runner.print_results(login_results)
    
    # 2. API 엔드포인트 부하 테스트
    runner.start_time = time.time()
    api_results = await runner.load_test_api_endpoints(100, 5)
    runner.end_time = time.time()
    runner.print_results(api_results)
    
    # 3. 스트레스 테스트
    stress_results = await runner.stress_test(200, 50)
    print("\n=== Stress Test Results ===")
    for result in stress_results:
        print(f"Users: {result['concurrent_users']}, "
              f"Error Rate: {result['error_rate']:.2f}%, "
              f"Avg Response Time: {result['avg_response_time']:.2f}ms")
    
    # 4. 스파이크 테스트
    spike_results = await runner.spike_test(100, 300)
    print("\n=== Spike Test Results ===")
    for result in spike_results:
        print(f"Phase: {result['phase']}, "
              f"Error Rate: {result['error_rate']:.2f}%, "
              f"Avg Response Time: {result['avg_response_time']:.2f}ms")
    
    print("\nPerformance Tests Completed!")

if __name__ == "__main__":
    asyncio.run(main())
