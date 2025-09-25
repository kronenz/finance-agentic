"""
통합 검증 테스트
"""

import pytest
import requests
import json
import time
from typing import Dict, List, Any, Optional

class IntegrationValidator:
    """통합 검증 클래스"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_token = None
    
    def setup_authentication(self):
        """인증 설정"""
        print("Setting up authentication...")
        
        login_data = {
            "email": "admin@example.com",
            "password": "password"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.test_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.test_token}"})
                print("✓ Authentication setup successful")
                return True
            else:
                print(f"⚠ Authentication setup failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠ Authentication setup error: {e}")
            return False
    
    def test_database_connectivity(self):
        """데이터베이스 연결 테스트"""
        print("Testing database connectivity...")
        
        # 시장 데이터 조회
        response = self.session.get(f"{self.base_url}/api/v1/analysis/market-regime")
        assert response.status_code == 200, f"Database connectivity failed: {response.status_code}"
        
        data = response.json()
        assert "regime" in data, "Database response missing 'regime' field"
        assert "timestamp" in data, "Database response missing 'timestamp' field"
        
        print("✓ Database connectivity successful")
        return True
    
    def test_redis_connectivity(self):
        """Redis 연결 테스트"""
        print("Testing Redis connectivity...")
        
        # 실시간 데이터 스트리밍
        response = self.session.get(f"{self.base_url}/api/v1/streaming/market-data")
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data, "Redis response missing 'status' field"
            assert "channels" in data, "Redis response missing 'channels' field"
            
            print("✓ Redis connectivity successful")
            return True
        else:
            print(f"⚠ Redis connectivity failed: {response.status_code}")
            return False
    
    def test_ai_agent_integration(self):
        """AI 에이전트 통합 테스트"""
        print("Testing AI agent integration...")
        
        # AI 에이전트 상태 확인
        response = self.session.get(f"{self.base_url}/api/v1/monitoring/agents")
        assert response.status_code == 200, f"AI agent integration failed: {response.status_code}"
        
        data = response.json()
        assert "agents" in data, "AI agent response missing 'agents' field"
        assert isinstance(data["agents"], list), "Agents should be a list"
        
        # 각 에이전트의 상태 확인
        for agent in data["agents"]:
            assert "name" in agent, "Agent missing 'name' field"
            assert "status" in agent, "Agent missing 'status' field"
            assert agent["status"] in ["active", "inactive", "error"], f"Invalid agent status: {agent['status']}"
        
        print("✓ AI agent integration successful")
        return True
    
    def test_trading_system_integration(self):
        """거래 시스템 통합 테스트"""
        print("Testing trading system integration...")
        
        # 포지션 조회
        response = self.session.get(f"{self.base_url}/api/v1/trading/positions")
        assert response.status_code == 200, f"Trading system integration failed: {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Positions should be a list"
        
        # 거래 신호 조회
        response = self.session.get(f"{self.base_url}/api/v1/trading/signals")
        assert response.status_code == 200, f"Trading signals failed: {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Signals should be a list"
        
        print("✓ Trading system integration successful")
        return True
    
    def test_analysis_system_integration(self):
        """분석 시스템 통합 테스트"""
        print("Testing analysis system integration...")
        
        # 시장 국면 분석
        response = self.session.get(f"{self.base_url}/api/v1/analysis/market-regime")
        assert response.status_code == 200, f"Market regime analysis failed: {response.status_code}"
        
        data = response.json()
        assert "regime" in data, "Market regime missing 'regime' field"
        assert "confidence" in data, "Market regime missing 'confidence' field"
        assert "timestamp" in data, "Market regime missing 'timestamp' field"
        
        # VWAP 분석
        response = self.session.get(f"{self.base_url}/api/v1/analysis/vwap")
        assert response.status_code == 200, f"VWAP analysis failed: {response.status_code}"
        
        data = response.json()
        assert "vwap" in data, "VWAP analysis missing 'vwap' field"
        assert "deviation" in data, "VWAP analysis missing 'deviation' field"
        
        # 볼륨 프로파일 분석
        response = self.session.get(f"{self.base_url}/api/v1/analysis/volume-profile")
        assert response.status_code == 200, f"Volume profile analysis failed: {response.status_code}"
        
        data = response.json()
        assert "poc" in data, "Volume profile missing 'poc' field"
        assert "value_area" in data, "Volume profile missing 'value_area' field"
        
        print("✓ Analysis system integration successful")
        return True
    
    def test_risk_management_integration(self):
        """리스크 관리 통합 테스트"""
        print("Testing risk management integration...")
        
        # 포트폴리오 리스크
        response = self.session.get(f"{self.base_url}/api/v1/risk/portfolio")
        assert response.status_code == 200, f"Portfolio risk failed: {response.status_code}"
        
        data = response.json()
        assert "total_exposure" in data, "Portfolio risk missing 'total_exposure' field"
        assert "max_drawdown" in data, "Portfolio risk missing 'max_drawdown' field"
        assert "risk_score" in data, "Portfolio risk missing 'risk_score' field"
        
        # 포지션 리스크
        response = self.session.get(f"{self.base_url}/api/v1/risk/positions")
        assert response.status_code == 200, f"Position risk failed: {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Position risk should be a list"
        
        print("✓ Risk management integration successful")
        return True
    
    def test_monitoring_system_integration(self):
        """모니터링 시스템 통합 테스트"""
        print("Testing monitoring system integration...")
        
        # 시스템 상태
        response = self.session.get(f"{self.base_url}/api/v1/monitoring/system")
        assert response.status_code == 200, f"System monitoring failed: {response.status_code}"
        
        data = response.json()
        assert "status" in data, "System monitoring missing 'status' field"
        assert "uptime" in data, "System monitoring missing 'uptime' field"
        assert "memory_usage" in data, "System monitoring missing 'memory_usage' field"
        assert "cpu_usage" in data, "System monitoring missing 'cpu_usage' field"
        
        # AI 에이전트 상태
        response = self.session.get(f"{self.base_url}/api/v1/monitoring/agents")
        assert response.status_code == 200, f"Agents monitoring failed: {response.status_code}"
        
        data = response.json()
        assert "agents" in data, "Agents monitoring missing 'agents' field"
        assert isinstance(data["agents"], list), "Agents should be a list"
        
        print("✓ Monitoring system integration successful")
        return True
    
    def test_data_flow_integration(self):
        """데이터 플로우 통합 테스트"""
        print("Testing data flow integration...")
        
        # 시장 데이터 수집
        response = self.session.get(f"{self.base_url}/api/v1/streaming/market-data")
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data, "Market data streaming missing 'status' field"
            assert "channels" in data, "Market data streaming missing 'channels' field"
            
            # 데이터 처리 확인
            response = self.session.get(f"{self.base_url}/api/v1/analysis/market-regime")
            assert response.status_code == 200, f"Data processing failed: {response.status_code}"
            
            data = response.json()
            assert "regime" in data, "Processed data missing 'regime' field"
            
            print("✓ Data flow integration successful")
            return True
        else:
            print(f"⚠ Data flow integration failed: {response.status_code}")
            return False
    
    def test_api_consistency(self):
        """API 일관성 테스트"""
        print("Testing API consistency...")
        
        # 모든 API 엔드포인트의 응답 형식 확인
        endpoints = [
            "/api/v1/trading/positions",
            "/api/v1/trading/signals",
            "/api/v1/analysis/market-regime",
            "/api/v1/analysis/vwap",
            "/api/v1/analysis/volume-profile",
            "/api/v1/risk/portfolio",
            "/api/v1/risk/positions",
            "/api/v1/monitoring/system",
            "/api/v1/monitoring/agents"
        ]
        
        for endpoint in endpoints:
            response = self.session.get(f"{self.base_url}{endpoint}")
            assert response.status_code == 200, f"API endpoint failed: {endpoint}"
            
            data = response.json()
            assert isinstance(data, (dict, list)), f"API response should be dict or list: {endpoint}"
            
            # 에러 응답 형식 확인
            if "error" in data:
                assert "message" in data, f"Error response missing message: {endpoint}"
        
        print("✓ API consistency successful")
        return True
    
    def test_error_handling_integration(self):
        """에러 처리 통합 테스트"""
        print("Testing error handling integration...")
        
        # 404 에러 처리
        response = self.session.get(f"{self.base_url}/api/v1/nonexistent")
        assert response.status_code == 404, f"404 error not handled: {response.status_code}"
        
        data = response.json()
        assert "error" in data, "404 error response missing 'error' field"
        assert "message" in data, "404 error response missing 'message' field"
        
        # 400 에러 처리
        invalid_data = {"invalid": "data"}
        response = self.session.post(f"{self.base_url}/api/v1/trading/orders", json=invalid_data)
        assert response.status_code == 400, f"400 error not handled: {response.status_code}"
        
        data = response.json()
        assert "error" in data, "400 error response missing 'error' field"
        assert "message" in data, "400 error response missing 'message' field"
        
        print("✓ Error handling integration successful")
        return True
    
    def test_performance_integration(self):
        """성능 통합 테스트"""
        print("Testing performance integration...")
        
        # 응답 시간 측정
        endpoints = [
            "/api/v1/trading/positions",
            "/api/v1/analysis/market-regime",
            "/api/v1/monitoring/system"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}{endpoint}")
            end_time = time.time()
            
            duration = end_time - start_time
            
            assert response.status_code == 200, f"Endpoint failed: {endpoint}"
            assert duration < 1.0, f"Response time too slow: {endpoint} took {duration:.2f}s"
            
            print(f"  {endpoint}: {duration:.3f}s")
        
        print("✓ Performance integration successful")
        return True
    
    def test_security_integration(self):
        """보안 통합 테스트"""
        print("Testing security integration...")
        
        # 인증되지 않은 요청
        unauth_session = requests.Session()
        response = unauth_session.get(f"{self.base_url}/api/v1/trading/positions")
        
        # 인증이 필요한 엔드포인트는 401 또는 403을 반환해야 함
        assert response.status_code in [401, 403], f"Unauthenticated request not blocked: {response.status_code}"
        
        # CORS 헤더 확인
        response = self.session.options(f"{self.base_url}/api/v1/trading/positions")
        assert "Access-Control-Allow-Origin" in response.headers, "CORS headers missing"
        
        # 보안 헤더 확인
        response = self.session.get(f"{self.base_url}/api/v1/trading/positions")
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection"
        ]
        
        for header in security_headers:
            assert header in response.headers, f"Security header missing: {header}"
        
        print("✓ Security integration successful")
        return True
    
    def run_integration_validation(self) -> Dict[str, Any]:
        """통합 검증 실행"""
        print("Starting integration validation...")
        
        # 인증 설정
        if not self.setup_authentication():
            print("⚠ Authentication setup failed, continuing with limited tests")
        
        test_results = {}
        passed_tests = 0
        total_tests = 0
        
        tests = [
            ("database_connectivity", self.test_database_connectivity),
            ("redis_connectivity", self.test_redis_connectivity),
            ("ai_agent_integration", self.test_ai_agent_integration),
            ("trading_system_integration", self.test_trading_system_integration),
            ("analysis_system_integration", self.test_analysis_system_integration),
            ("risk_management_integration", self.test_risk_management_integration),
            ("monitoring_system_integration", self.test_monitoring_system_integration),
            ("data_flow_integration", self.test_data_flow_integration),
            ("api_consistency", self.test_api_consistency),
            ("error_handling_integration", self.test_error_handling_integration),
            ("performance_integration", self.test_performance_integration),
            ("security_integration", self.test_security_integration)
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
def test_database_connectivity():
    """데이터베이스 연결 테스트"""
    validator = IntegrationValidator()
    result = validator.test_database_connectivity()
    assert result, "Database connectivity test failed"

def test_redis_connectivity():
    """Redis 연결 테스트"""
    validator = IntegrationValidator()
    result = validator.test_redis_connectivity()
    assert result, "Redis connectivity test failed"

def test_ai_agent_integration():
    """AI 에이전트 통합 테스트"""
    validator = IntegrationValidator()
    result = validator.test_ai_agent_integration()
    assert result, "AI agent integration test failed"

def test_trading_system_integration():
    """거래 시스템 통합 테스트"""
    validator = IntegrationValidator()
    result = validator.test_trading_system_integration()
    assert result, "Trading system integration test failed"

def test_analysis_system_integration():
    """분석 시스템 통합 테스트"""
    validator = IntegrationValidator()
    result = validator.test_analysis_system_integration()
    assert result, "Analysis system integration test failed"

def test_risk_management_integration():
    """리스크 관리 통합 테스트"""
    validator = IntegrationValidator()
    result = validator.test_risk_management_integration()
    assert result, "Risk management integration test failed"

def test_monitoring_system_integration():
    """모니터링 시스템 통합 테스트"""
    validator = IntegrationValidator()
    result = validator.test_monitoring_system_integration()
    assert result, "Monitoring system integration test failed"

def test_data_flow_integration():
    """데이터 플로우 통합 테스트"""
    validator = IntegrationValidator()
    result = validator.test_data_flow_integration()
    assert result, "Data flow integration test failed"

def test_api_consistency():
    """API 일관성 테스트"""
    validator = IntegrationValidator()
    result = validator.test_api_consistency()
    assert result, "API consistency test failed"

def test_error_handling_integration():
    """에러 처리 통합 테스트"""
    validator = IntegrationValidator()
    result = validator.test_error_handling_integration()
    assert result, "Error handling integration test failed"

def test_performance_integration():
    """성능 통합 테스트"""
    validator = IntegrationValidator()
    result = validator.test_performance_integration()
    assert result, "Performance integration test failed"

def test_security_integration():
    """보안 통합 테스트"""
    validator = IntegrationValidator()
    result = validator.test_security_integration()
    assert result, "Security integration test failed"

def test_integration_comprehensive():
    """통합 검증 종합 테스트"""
    validator = IntegrationValidator()
    results = validator.run_integration_validation()
    
    # 전체 테스트 성공률이 90% 이상이어야 함
    assert results["success_rate"] >= 90, f"Integration validation success rate too low: {results['success_rate']}%"
    
    # 실패한 테스트가 1개 이하여야 함
    assert results["failed_tests"] <= 1, f"Too many failed integration tests: {results['failed_tests']}"

if __name__ == "__main__":
    # 통합 검증 실행
    validator = IntegrationValidator()
    results = validator.run_integration_validation()
    
    print(f"\nIntegration validation completed:")
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
        print("\nAll integration validation tests passed! ✓")
