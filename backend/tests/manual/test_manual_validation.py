"""
수동 테스트 및 검증
"""

import pytest
import requests
import json
import time
from typing import Dict, List, Any

class ManualTester:
    """수동 테스트 클래스"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health_check(self):
        """헬스체크 테스트"""
        print("Testing health check endpoint...")
        
        response = self.session.get(f"{self.base_url}/health")
        
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Health check response missing 'status' field"
        assert data["status"] == "healthy", f"Health check status not healthy: {data['status']}"
        
        print("✓ Health check passed")
        return True
    
    def test_api_documentation(self):
        """API 문서 테스트"""
        print("Testing API documentation...")
        
        # OpenAPI 스키마 확인
        response = self.session.get(f"{self.base_url}/api/v1/openapi.json")
        
        assert response.status_code == 200, f"OpenAPI schema not accessible: {response.status_code}"
        
        schema = response.json()
        assert "openapi" in schema, "OpenAPI schema missing 'openapi' field"
        assert "paths" in schema, "OpenAPI schema missing 'paths' field"
        
        # Swagger UI 확인
        response = self.session.get(f"{self.base_url}/docs")
        assert response.status_code == 200, f"Swagger UI not accessible: {response.status_code}"
        
        print("✓ API documentation accessible")
        return True
    
    def test_authentication_flow(self):
        """인증 플로우 테스트"""
        print("Testing authentication flow...")
        
        # 로그인 테스트
        login_data = {
            "email": "admin@example.com",
            "password": "password"
        }
        
        response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data, "Login response missing access token"
            assert "refresh_token" in data, "Login response missing refresh token"
            
            # 토큰을 세션에 저장
            self.session.headers.update({"Authorization": f"Bearer {data['access_token']}"})
            
            print("✓ Authentication flow passed")
            return True
        else:
            print(f"⚠ Authentication flow failed: {response.status_code}")
            return False
    
    def test_trading_endpoints(self):
        """거래 엔드포인트 테스트"""
        print("Testing trading endpoints...")
        
        # 포지션 조회
        response = self.session.get(f"{self.base_url}/api/v1/trading/positions")
        assert response.status_code == 200, f"Positions endpoint failed: {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Positions response should be a list"
        
        # 주문 생성 (모의)
        order_data = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "amount": 0.001,
            "price": 50000
        }
        
        response = self.session.post(f"{self.base_url}/api/v1/trading/orders", json=order_data)
        # 주문 생성은 인증이 필요할 수 있음
        assert response.status_code in [200, 201, 401, 403], f"Order creation failed: {response.status_code}"
        
        print("✓ Trading endpoints passed")
        return True
    
    def test_analysis_endpoints(self):
        """분석 엔드포인트 테스트"""
        print("Testing analysis endpoints...")
        
        # 시장 국면 분석
        response = self.session.get(f"{self.base_url}/api/v1/analysis/market-regime")
        assert response.status_code == 200, f"Market regime analysis failed: {response.status_code}"
        
        data = response.json()
        assert "regime" in data, "Market regime response missing 'regime' field"
        assert "confidence" in data, "Market regime response missing 'confidence' field"
        
        # VWAP 분석
        response = self.session.get(f"{self.base_url}/api/v1/analysis/vwap")
        assert response.status_code == 200, f"VWAP analysis failed: {response.status_code}"
        
        data = response.json()
        assert "vwap" in data, "VWAP response missing 'vwap' field"
        
        print("✓ Analysis endpoints passed")
        return True
    
    def test_monitoring_endpoints(self):
        """모니터링 엔드포인트 테스트"""
        print("Testing monitoring endpoints...")
        
        # AI 에이전트 상태
        response = self.session.get(f"{self.base_url}/api/v1/monitoring/agents")
        assert response.status_code == 200, f"Agents monitoring failed: {response.status_code}"
        
        data = response.json()
        assert "agents" in data, "Agents monitoring response missing 'agents' field"
        assert isinstance(data["agents"], list), "Agents should be a list"
        
        # 시스템 상태
        response = self.session.get(f"{self.base_url}/api/v1/monitoring/system")
        assert response.status_code == 200, f"System monitoring failed: {response.status_code}"
        
        data = response.json()
        assert "status" in data, "System monitoring response missing 'status' field"
        
        print("✓ Monitoring endpoints passed")
        return True
    
    def test_error_handling(self):
        """에러 처리 테스트"""
        print("Testing error handling...")
        
        # 404 에러 테스트
        response = self.session.get(f"{self.base_url}/api/v1/nonexistent")
        assert response.status_code == 404, f"404 error not handled: {response.status_code}"
        
        # 잘못된 JSON 테스트
        response = self.session.post(
            f"{self.base_url}/api/v1/trading/orders",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400, f"Invalid JSON not handled: {response.status_code}"
        
        print("✓ Error handling passed")
        return True
    
    def test_cors_headers(self):
        """CORS 헤더 테스트"""
        print("Testing CORS headers...")
        
        response = self.session.options(f"{self.base_url}/api/v1/trading/positions")
        
        # CORS 헤더 확인
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        for header in cors_headers:
            assert header in response.headers, f"CORS header missing: {header}"
        
        print("✓ CORS headers passed")
        return True
    
    def test_security_headers(self):
        """보안 헤더 테스트"""
        print("Testing security headers...")
        
        response = self.session.get(f"{self.base_url}/api/v1/trading/positions")
        
        # 보안 헤더 확인
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block"
        }
        
        for header, expected_value in security_headers.items():
            assert header in response.headers, f"Security header missing: {header}"
            assert response.headers[header] == expected_value, f"Security header value incorrect: {header}"
        
        print("✓ Security headers passed")
        return True
    
    def test_response_times(self):
        """응답 시간 테스트"""
        print("Testing response times...")
        
        endpoints = [
            "/api/v1/trading/positions",
            "/api/v1/analysis/market-regime",
            "/api/v1/monitoring/agents"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}{endpoint}")
            end_time = time.time()
            
            duration = end_time - start_time
            
            assert response.status_code == 200, f"Endpoint failed: {endpoint}"
            assert duration < 1.0, f"Response time too slow: {endpoint} took {duration:.2f}s"
            
            print(f"  {endpoint}: {duration:.3f}s")
        
        print("✓ Response times passed")
        return True
    
    def test_data_validation(self):
        """데이터 검증 테스트"""
        print("Testing data validation...")
        
        # 잘못된 거래 주문 데이터
        invalid_orders = [
            {"symbol": "", "side": "BUY", "amount": 0.001, "price": 50000},  # 빈 심볼
            {"symbol": "BTCUSDT", "side": "INVALID", "amount": 0.001, "price": 50000},  # 잘못된 사이드
            {"symbol": "BTCUSDT", "side": "BUY", "amount": -0.001, "price": 50000},  # 음수 금액
            {"symbol": "BTCUSDT", "side": "BUY", "amount": 0.001, "price": 0},  # 0 가격
        ]
        
        for order in invalid_orders:
            response = self.session.post(f"{self.base_url}/api/v1/trading/orders", json=order)
            assert response.status_code == 400, f"Invalid order accepted: {order}"
        
        print("✓ Data validation passed")
        return True
    
    def run_all_tests(self) -> Dict[str, Any]:
        """모든 수동 테스트 실행"""
        print("Starting manual validation tests...")
        
        test_results = {}
        passed_tests = 0
        total_tests = 0
        
        tests = [
            ("health_check", self.test_health_check),
            ("api_documentation", self.test_api_documentation),
            ("authentication_flow", self.test_authentication_flow),
            ("trading_endpoints", self.test_trading_endpoints),
            ("analysis_endpoints", self.test_analysis_endpoints),
            ("monitoring_endpoints", self.test_monitoring_endpoints),
            ("error_handling", self.test_error_handling),
            ("cors_headers", self.test_cors_headers),
            ("security_headers", self.test_security_headers),
            ("response_times", self.test_response_times),
            ("data_validation", self.test_data_validation)
        ]
        
        for test_name, test_func in tests:
            total_tests += 1
            try:
                result = test_func()
                test_results[test_name] = {"passed": result, "error": None}
                if result:
                    passed_tests += 1
            except Exception as e:
                test_results[test_name] = {"passed": False, "error": str(e)}
                print(f"✗ {test_name} failed: {e}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "test_results": test_results
        }

# 테스트 함수들
def test_manual_health_check():
    """수동 헬스체크 테스트"""
    tester = ManualTester()
    result = tester.test_health_check()
    assert result, "Health check test failed"

def test_manual_api_documentation():
    """수동 API 문서 테스트"""
    tester = ManualTester()
    result = tester.test_api_documentation()
    assert result, "API documentation test failed"

def test_manual_trading_endpoints():
    """수동 거래 엔드포인트 테스트"""
    tester = ManualTester()
    result = tester.test_trading_endpoints()
    assert result, "Trading endpoints test failed"

def test_manual_analysis_endpoints():
    """수동 분석 엔드포인트 테스트"""
    tester = ManualTester()
    result = tester.test_analysis_endpoints()
    assert result, "Analysis endpoints test failed"

def test_manual_monitoring_endpoints():
    """수동 모니터링 엔드포인트 테스트"""
    tester = ManualTester()
    result = tester.test_monitoring_endpoints()
    assert result, "Monitoring endpoints test failed"

def test_manual_error_handling():
    """수동 에러 처리 테스트"""
    tester = ManualTester()
    result = tester.test_error_handling()
    assert result, "Error handling test failed"

def test_manual_cors_headers():
    """수동 CORS 헤더 테스트"""
    tester = ManualTester()
    result = tester.test_cors_headers()
    assert result, "CORS headers test failed"

def test_manual_security_headers():
    """수동 보안 헤더 테스트"""
    tester = ManualTester()
    result = tester.test_security_headers()
    assert result, "Security headers test failed"

def test_manual_response_times():
    """수동 응답 시간 테스트"""
    tester = ManualTester()
    result = tester.test_response_times()
    assert result, "Response times test failed"

def test_manual_data_validation():
    """수동 데이터 검증 테스트"""
    tester = ManualTester()
    result = tester.test_data_validation()
    assert result, "Data validation test failed"

def test_manual_comprehensive():
    """수동 종합 테스트"""
    tester = ManualTester()
    results = tester.run_all_tests()
    
    # 전체 테스트 성공률이 90% 이상이어야 함
    assert results["success_rate"] >= 90, f"Manual test success rate too low: {results['success_rate']}%"
    
    # 실패한 테스트가 1개 이하여야 함
    assert results["failed_tests"] <= 1, f"Too many failed tests: {results['failed_tests']}"

if __name__ == "__main__":
    # 수동 테스트 실행
    tester = ManualTester()
    results = tester.run_all_tests()
    
    print(f"\nManual validation completed:")
    print(f"Total tests: {results['total_tests']}")
    print(f"Passed tests: {results['passed_tests']}")
    print(f"Failed tests: {results['failed_tests']}")
    print(f"Success rate: {results['success_rate']:.1f}%")
    
    if results['failed_tests'] > 0:
        print("\nFailed tests:")
        for test_name, result in results['test_results'].items():
            if not result['passed']:
                print(f"  - {test_name}: {result['error']}")
    else:
        print("\nAll tests passed! ✓")
