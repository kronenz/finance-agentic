"""
사용자 수용 테스트 (UAT)
"""

import pytest
import requests
import json
import time
from typing import Dict, List, Any, Optional

class UserAcceptanceTester:
    """사용자 수용 테스트 클래스"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_user = None
        self.test_token = None
    
    def setup_test_user(self):
        """테스트 사용자 설정"""
        print("Setting up test user...")
        
        # 사용자 등록
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/register", json=user_data)
            if response.status_code == 201:
                print("✓ Test user registered")
            elif response.status_code == 409:
                print("✓ Test user already exists")
            else:
                print(f"⚠ User registration failed: {response.status_code}")
        except Exception as e:
            print(f"⚠ User registration error: {e}")
        
        # 로그인
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.test_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.test_token}"})
                print("✓ Test user logged in")
                return True
            else:
                print(f"⚠ Login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠ Login error: {e}")
            return False
    
    def test_user_registration_flow(self):
        """사용자 등록 플로우 테스트"""
        print("Testing user registration flow...")
        
        # 새 사용자 등록
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User"
        }
        
        response = self.session.post(f"{self.base_url}/auth/register", json=user_data)
        
        if response.status_code == 201:
            data = response.json()
            assert "user_id" in data, "Registration response missing user_id"
            assert "message" in data, "Registration response missing message"
            print("✓ User registration successful")
            return True
        elif response.status_code == 409:
            print("✓ User already exists (expected)")
            return True
        else:
            print(f"⚠ Registration failed: {response.status_code}")
            return False
    
    def test_user_login_flow(self):
        """사용자 로그인 플로우 테스트"""
        print("Testing user login flow...")
        
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data, "Login response missing access token"
            assert "refresh_token" in data, "Login response missing refresh token"
            assert "token_type" in data, "Login response missing token type"
            assert data["token_type"] == "bearer", "Token type should be 'bearer'"
            
            # 토큰을 세션에 저장
            self.test_token = data["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.test_token}"})
            
            print("✓ User login successful")
            return True
        else:
            print(f"⚠ Login failed: {response.status_code}")
            return False
    
    def test_trading_dashboard_access(self):
        """거래 대시보드 접근 테스트"""
        print("Testing trading dashboard access...")
        
        # 포지션 조회
        response = self.session.get(f"{self.base_url}/api/v1/trading/positions")
        assert response.status_code == 200, f"Positions access failed: {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Positions should be a list"
        
        # 거래 신호 조회
        response = self.session.get(f"{self.base_url}/api/v1/trading/signals")
        assert response.status_code == 200, f"Signals access failed: {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Signals should be a list"
        
        print("✓ Trading dashboard access successful")
        return True
    
    def test_market_analysis_access(self):
        """시장 분석 접근 테스트"""
        print("Testing market analysis access...")
        
        # 시장 국면 분석
        response = self.session.get(f"{self.base_url}/api/v1/analysis/market-regime")
        assert response.status_code == 200, f"Market regime analysis failed: {response.status_code}"
        
        data = response.json()
        assert "regime" in data, "Market regime response missing 'regime' field"
        assert "confidence" in data, "Market regime response missing 'confidence' field"
        assert "timestamp" in data, "Market regime response missing 'timestamp' field"
        
        # VWAP 분석
        response = self.session.get(f"{self.base_url}/api/v1/analysis/vwap")
        assert response.status_code == 200, f"VWAP analysis failed: {response.status_code}"
        
        data = response.json()
        assert "vwap" in data, "VWAP response missing 'vwap' field"
        assert "deviation" in data, "VWAP response missing 'deviation' field"
        
        # 볼륨 프로파일 분석
        response = self.session.get(f"{self.base_url}/api/v1/analysis/volume-profile")
        assert response.status_code == 200, f"Volume profile analysis failed: {response.status_code}"
        
        data = response.json()
        assert "poc" in data, "Volume profile response missing 'poc' field"
        assert "value_area" in data, "Volume profile response missing 'value_area' field"
        
        print("✓ Market analysis access successful")
        return True
    
    def test_risk_management_access(self):
        """리스크 관리 접근 테스트"""
        print("Testing risk management access...")
        
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
        
        print("✓ Risk management access successful")
        return True
    
    def test_ai_agent_monitoring(self):
        """AI 에이전트 모니터링 테스트"""
        print("Testing AI agent monitoring...")
        
        # AI 에이전트 상태
        response = self.session.get(f"{self.base_url}/api/v1/monitoring/agents")
        assert response.status_code == 200, f"Agents monitoring failed: {response.status_code}"
        
        data = response.json()
        assert "agents" in data, "Agents monitoring missing 'agents' field"
        assert isinstance(data["agents"], list), "Agents should be a list"
        
        # 각 에이전트의 상태 확인
        for agent in data["agents"]:
            assert "name" in agent, "Agent missing 'name' field"
            assert "status" in agent, "Agent missing 'status' field"
            assert "last_activity" in agent, "Agent missing 'last_activity' field"
        
        # 시스템 상태
        response = self.session.get(f"{self.base_url}/api/v1/monitoring/system")
        assert response.status_code == 200, f"System monitoring failed: {response.status_code}"
        
        data = response.json()
        assert "status" in data, "System monitoring missing 'status' field"
        assert "uptime" in data, "System monitoring missing 'uptime' field"
        assert "memory_usage" in data, "System monitoring missing 'memory_usage' field"
        
        print("✓ AI agent monitoring successful")
        return True
    
    def test_trading_order_flow(self):
        """거래 주문 플로우 테스트"""
        print("Testing trading order flow...")
        
        # 주문 생성
        order_data = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "amount": 0.001,
            "price": 50000,
            "order_type": "LIMIT"
        }
        
        response = self.session.post(f"{self.base_url}/api/v1/trading/orders", json=order_data)
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "order_id" in data, "Order creation missing 'order_id' field"
            assert "status" in data, "Order creation missing 'status' field"
            
            order_id = data["order_id"]
            
            # 주문 조회
            response = self.session.get(f"{self.base_url}/api/v1/trading/orders/{order_id}")
            assert response.status_code == 200, f"Order retrieval failed: {response.status_code}"
            
            data = response.json()
            assert data["order_id"] == order_id, "Retrieved order ID mismatch"
            
            # 주문 취소
            response = self.session.delete(f"{self.base_url}/api/v1/trading/orders/{order_id}")
            assert response.status_code == 200, f"Order cancellation failed: {response.status_code}"
            
            print("✓ Trading order flow successful")
            return True
        else:
            print(f"⚠ Order creation failed: {response.status_code}")
            return False
    
    def test_real_time_data_streaming(self):
        """실시간 데이터 스트리밍 테스트"""
        print("Testing real-time data streaming...")
        
        # WebSocket 연결 테스트 (HTTP로 시뮬레이션)
        response = self.session.get(f"{self.base_url}/api/v1/streaming/market-data")
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data, "Streaming response missing 'status' field"
            assert "channels" in data, "Streaming response missing 'channels' field"
            
            print("✓ Real-time data streaming accessible")
            return True
        else:
            print(f"⚠ Streaming not available: {response.status_code}")
            return False
    
    def test_user_preferences(self):
        """사용자 설정 테스트"""
        print("Testing user preferences...")
        
        # 사용자 설정 조회
        response = self.session.get(f"{self.base_url}/api/v1/user/preferences")
        
        if response.status_code == 200:
            data = response.json()
            assert "theme" in data, "User preferences missing 'theme' field"
            assert "notifications" in data, "User preferences missing 'notifications' field"
            
            # 사용자 설정 업데이트
            preferences_data = {
                "theme": "dark",
                "notifications": {
                    "email": True,
                    "push": False
                }
            }
            
            response = self.session.put(f"{self.base_url}/api/v1/user/preferences", json=preferences_data)
            assert response.status_code == 200, f"Preferences update failed: {response.status_code}"
            
            print("✓ User preferences successful")
            return True
        else:
            print(f"⚠ User preferences not available: {response.status_code}")
            return False
    
    def test_error_handling_user_perspective(self):
        """사용자 관점에서의 에러 처리 테스트"""
        print("Testing error handling from user perspective...")
        
        # 잘못된 엔드포인트 접근
        response = self.session.get(f"{self.base_url}/api/v1/invalid-endpoint")
        assert response.status_code == 404, f"404 error not handled: {response.status_code}"
        
        # 잘못된 데이터로 주문 생성
        invalid_order = {
            "symbol": "",
            "side": "INVALID",
            "amount": -1,
            "price": 0
        }
        
        response = self.session.post(f"{self.base_url}/api/v1/trading/orders", json=invalid_order)
        assert response.status_code == 400, f"Invalid order not rejected: {response.status_code}"
        
        # 에러 응답 형식 확인
        data = response.json()
        assert "error" in data, "Error response missing 'error' field"
        assert "message" in data, "Error response missing 'message' field"
        
        print("✓ Error handling from user perspective successful")
        return True
    
    def test_performance_user_experience(self):
        """사용자 경험 관점에서의 성능 테스트"""
        print("Testing performance from user experience perspective...")
        
        endpoints = [
            "/api/v1/trading/positions",
            "/api/v1/analysis/market-regime",
            "/api/v1/monitoring/agents",
            "/api/v1/risk/portfolio"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}{endpoint}")
            end_time = time.time()
            
            duration = end_time - start_time
            
            assert response.status_code == 200, f"Endpoint failed: {endpoint}"
            assert duration < 2.0, f"Response time too slow for user experience: {endpoint} took {duration:.2f}s"
            
            print(f"  {endpoint}: {duration:.3f}s")
        
        print("✓ Performance from user experience perspective successful")
        return True
    
    def run_user_acceptance_tests(self) -> Dict[str, Any]:
        """사용자 수용 테스트 실행"""
        print("Starting user acceptance tests...")
        
        # 테스트 사용자 설정
        if not self.setup_test_user():
            print("⚠ Test user setup failed, continuing with limited tests")
        
        test_results = {}
        passed_tests = 0
        total_tests = 0
        
        tests = [
            ("user_registration_flow", self.test_user_registration_flow),
            ("user_login_flow", self.test_user_login_flow),
            ("trading_dashboard_access", self.test_trading_dashboard_access),
            ("market_analysis_access", self.test_market_analysis_access),
            ("risk_management_access", self.test_risk_management_access),
            ("ai_agent_monitoring", self.test_ai_agent_monitoring),
            ("trading_order_flow", self.test_trading_order_flow),
            ("real_time_data_streaming", self.test_real_time_data_streaming),
            ("user_preferences", self.test_user_preferences),
            ("error_handling_user_perspective", self.test_error_handling_user_perspective),
            ("performance_user_experience", self.test_performance_user_experience)
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
def test_user_registration_flow():
    """사용자 등록 플로우 테스트"""
    tester = UserAcceptanceTester()
    result = tester.test_user_registration_flow()
    assert result, "User registration flow test failed"

def test_user_login_flow():
    """사용자 로그인 플로우 테스트"""
    tester = UserAcceptanceTester()
    result = tester.test_user_login_flow()
    assert result, "User login flow test failed"

def test_trading_dashboard_access():
    """거래 대시보드 접근 테스트"""
    tester = UserAcceptanceTester()
    result = tester.test_trading_dashboard_access()
    assert result, "Trading dashboard access test failed"

def test_market_analysis_access():
    """시장 분석 접근 테스트"""
    tester = UserAcceptanceTester()
    result = tester.test_market_analysis_access()
    assert result, "Market analysis access test failed"

def test_risk_management_access():
    """리스크 관리 접근 테스트"""
    tester = UserAcceptanceTester()
    result = tester.test_risk_management_access()
    assert result, "Risk management access test failed"

def test_ai_agent_monitoring():
    """AI 에이전트 모니터링 테스트"""
    tester = UserAcceptanceTester()
    result = tester.test_ai_agent_monitoring()
    assert result, "AI agent monitoring test failed"

def test_trading_order_flow():
    """거래 주문 플로우 테스트"""
    tester = UserAcceptanceTester()
    result = tester.test_trading_order_flow()
    assert result, "Trading order flow test failed"

def test_real_time_data_streaming():
    """실시간 데이터 스트리밍 테스트"""
    tester = UserAcceptanceTester()
    result = tester.test_real_time_data_streaming()
    assert result, "Real-time data streaming test failed"

def test_user_preferences():
    """사용자 설정 테스트"""
    tester = UserAcceptanceTester()
    result = tester.test_user_preferences()
    assert result, "User preferences test failed"

def test_error_handling_user_perspective():
    """사용자 관점에서의 에러 처리 테스트"""
    tester = UserAcceptanceTester()
    result = tester.test_error_handling_user_perspective()
    assert result, "Error handling from user perspective test failed"

def test_performance_user_experience():
    """사용자 경험 관점에서의 성능 테스트"""
    tester = UserAcceptanceTester()
    result = tester.test_performance_user_experience()
    assert result, "Performance from user experience perspective test failed"

def test_user_acceptance_comprehensive():
    """사용자 수용 종합 테스트"""
    tester = UserAcceptanceTester()
    results = tester.run_user_acceptance_tests()
    
    # 전체 테스트 성공률이 85% 이상이어야 함
    assert results["success_rate"] >= 85, f"UAT success rate too low: {results['success_rate']}%"
    
    # 실패한 테스트가 2개 이하여야 함
    assert results["failed_tests"] <= 2, f"Too many failed UAT tests: {results['failed_tests']}"

if __name__ == "__main__":
    # 사용자 수용 테스트 실행
    tester = UserAcceptanceTester()
    results = tester.run_user_acceptance_tests()
    
    print(f"\nUser acceptance tests completed:")
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
        print("\nAll UAT tests passed! ✓")
