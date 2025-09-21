# 보안 테스트 및 취약점 스캔
import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import patch
import json
import base64
import hmac
import hashlib
from datetime import datetime, timedelta

from app.main import app
from app.core.config import settings

class SecurityTestSuite:
    """보안 테스트 스위트"""
    
    def __init__(self):
        self.vulnerabilities_found = []
        self.security_issues = []
    
    def add_vulnerability(self, category: str, description: str, severity: str, recommendation: str):
        """취약점 기록"""
        self.vulnerabilities_found.append({
            "category": category,
            "description": description,
            "severity": severity,
            "recommendation": recommendation,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def add_security_issue(self, issue: str, details: str):
        """보안 이슈 기록"""
        self.security_issues.append({
            "issue": issue,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })

@pytest.fixture
async def security_suite():
    """보안 테스트 스위트 생성"""
    return SecurityTestSuite()

@pytest.fixture
async def test_client():
    """테스트 클라이언트 생성"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

class TestAuthenticationSecurity:
    """인증 보안 테스트"""
    
    async def test_password_strength_validation(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """비밀번호 강도 검증 테스트"""
        weak_passwords = [
            "123456",
            "password",
            "admin",
            "qwerty",
            "abc123",
            "test",
            "12345678",
            "password123"
        ]
        
        for weak_password in weak_passwords:
            register_data = {
                "email": f"test_{weak_password}@example.com",
                "password": weak_password,
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = await test_client.post("/api/v1/auth/register", json=register_data)
            
            if response.status_code == 200:
                security_suite.add_vulnerability(
                    "Authentication",
                    f"Weak password '{weak_password}' was accepted",
                    "Medium",
                    "Implement password strength validation"
                )
            else:
                # 약한 비밀번호가 거부되어야 함
                assert response.status_code in [400, 422]
    
    async def test_sql_injection_in_auth(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """인증에서 SQL Injection 테스트"""
        sql_injection_payloads = [
            "admin' OR '1'='1",
            "admin' OR 1=1--",
            "admin'; DROP TABLE users;--",
            "admin' UNION SELECT * FROM users--",
            "admin' OR '1'='1' AND password='anything",
            "admin' OR '1'='1' OR '1'='1",
            "admin' OR '1'='1' LIMIT 1--",
            "admin' OR '1'='1' ORDER BY 1--"
        ]
        
        for payload in sql_injection_payloads:
            login_data = {
                "username": payload,
                "password": "anything"
            }
            
            response = await test_client.post("/api/v1/auth/login", data=login_data)
            
            # SQL Injection이 성공하면 200을 반환할 수 있음
            if response.status_code == 200:
                security_suite.add_vulnerability(
                    "SQL Injection",
                    f"SQL Injection payload '{payload}' was successful",
                    "Critical",
                    "Implement proper input validation and parameterized queries"
                )
            else:
                # SQL Injection이 차단되어야 함
                assert response.status_code in [400, 401, 422]
    
    async def test_brute_force_protection(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """무차별 대입 공격 보호 테스트"""
        # 여러 번의 실패한 로그인 시도
        for i in range(10):
            login_data = {
                "username": "test@example.com",
                "password": f"wrong_password_{i}"
            }
            
            response = await test_client.post("/api/v1/auth/login", data=login_data)
            
            # 처음 몇 번은 401을 반환해야 함
            if i < 5:
                assert response.status_code == 401
            else:
                # 5번 이상 실패하면 429 (Rate Limited)를 반환해야 함
                if response.status_code != 429:
                    security_suite.add_vulnerability(
                        "Brute Force",
                        "No brute force protection detected",
                        "High",
                        "Implement rate limiting for failed login attempts"
                    )

class TestInputValidationSecurity:
    """입력 검증 보안 테스트"""
    
    async def test_xss_in_inputs(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """XSS 공격 테스트"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>",
            "<keygen onfocus=alert('XSS') autofocus>"
        ]
        
        for payload in xss_payloads:
            # 등록 폼에서 XSS 테스트
            register_data = {
                "email": f"test_{hash(payload)}@example.com",
                "password": "testpassword123",
                "first_name": payload,
                "last_name": "User"
            }
            
            response = await test_client.post("/api/v1/auth/register", json=register_data)
            
            # XSS 페이로드가 응답에 포함되어 있으면 취약점
            if payload in response.text:
                security_suite.add_vulnerability(
                    "XSS",
                    f"XSS payload '{payload}' was reflected in response",
                    "High",
                    "Implement proper input sanitization and output encoding"
                )
    
    async def test_json_injection(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """JSON Injection 테스트"""
        json_injection_payloads = [
            '{"email": "test@example.com", "password": "test123", "admin": true}',
            '{"email": "test@example.com", "password": "test123", "role": "admin"}',
            '{"email": "test@example.com", "password": "test123", "is_admin": true}',
            '{"email": "test@example.com", "password": "test123", "privileges": ["admin"]}'
        ]
        
        for payload in json_injection_payloads:
            try:
                data = json.loads(payload)
                response = await test_client.post("/api/v1/auth/register", json=data)
                
                # JSON Injection이 성공하면 200을 반환할 수 있음
                if response.status_code == 200:
                    security_suite.add_vulnerability(
                        "JSON Injection",
                        f"JSON Injection payload was successful: {payload}",
                        "Medium",
                        "Validate all input fields and reject unexpected properties"
                    )
            except json.JSONDecodeError:
                # 잘못된 JSON은 거부되어야 함
                pass
    
    async def test_large_payload_handling(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """대용량 페이로드 처리 테스트"""
        # 매우 큰 페이로드 생성
        large_payload = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "A" * 10000,  # 10KB 문자열
            "last_name": "B" * 10000
        }
        
        response = await test_client.post("/api/v1/auth/register", json=large_payload)
        
        # 대용량 페이로드는 413 (Payload Too Large)을 반환해야 함
        if response.status_code != 413:
            security_suite.add_vulnerability(
                "DoS",
                "Large payload was accepted without size limit",
                "Medium",
                "Implement request size limits"
            )

class TestAuthorizationSecurity:
    """인증 및 권한 보안 테스트"""
    
    async def test_unauthorized_access(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """인증되지 않은 접근 테스트"""
        protected_endpoints = [
            "/api/v1/subscriptions/",
            "/api/v1/subscriptions/active",
            "/api/v1/ai/strategies/recommend",
            "/api/v1/ai/risk/assess",
            "/api/v1/ai/profile"
        ]
        
        for endpoint in protected_endpoints:
            response = await test_client.get(endpoint)
            
            # 인증되지 않은 접근은 401을 반환해야 함
            if response.status_code != 401:
                security_suite.add_vulnerability(
                    "Authorization",
                    f"Unauthorized access to {endpoint} was allowed",
                    "High",
                    "Implement proper authentication checks"
                )
    
    async def test_token_manipulation(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """토큰 조작 테스트"""
        # 잘못된 토큰으로 접근 시도
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "Bearer " + "A" * 100,
            "Bearer " + base64.b64encode(b"fake_token").decode(),
            "Bearer " + "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.invalid_signature"
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": token}
            response = await test_client.get("/api/v1/auth/me", headers=headers)
            
            # 잘못된 토큰은 401을 반환해야 함
            if response.status_code == 200:
                security_suite.add_vulnerability(
                    "Token Security",
                    f"Invalid token '{token}' was accepted",
                    "Critical",
                    "Implement proper JWT token validation"
                )
    
    async def test_privilege_escalation(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """권한 상승 테스트"""
        # 일반 사용자로 관리자 기능 접근 시도
        admin_endpoints = [
            "/api/v1/admin/users",
            "/api/v1/admin/settings",
            "/api/v1/admin/logs"
        ]
        
        for endpoint in admin_endpoints:
            response = await test_client.get(endpoint)
            
            # 관리자 엔드포인트는 403 또는 404를 반환해야 함
            if response.status_code == 200:
                security_suite.add_vulnerability(
                    "Privilege Escalation",
                    f"Unauthorized access to admin endpoint {endpoint}",
                    "Critical",
                    "Implement proper role-based access control"
                )

class TestDataSecurity:
    """데이터 보안 테스트"""
    
    async def test_sensitive_data_exposure(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """민감한 데이터 노출 테스트"""
        # 등록 후 사용자 정보 조회
        register_data = {
            "email": "sensitive@example.com",
            "password": "testpassword123",
            "first_name": "Sensitive",
            "last_name": "Data"
        }
        
        register_response = await test_client.post("/api/v1/auth/register", json=register_data)
        
        if register_response.status_code == 200:
            user_data = register_response.json()
            
            # 민감한 정보가 노출되었는지 확인
            sensitive_fields = ["password", "hashed_password", "secret", "private_key"]
            
            for field in sensitive_fields:
                if field in user_data:
                    security_suite.add_vulnerability(
                        "Data Exposure",
                        f"Sensitive field '{field}' was exposed in response",
                        "High",
                        "Remove sensitive fields from API responses"
                    )
    
    async def test_data_validation_bypass(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """데이터 검증 우회 테스트"""
        # 다양한 데이터 타입으로 검증 우회 시도
        bypass_attempts = [
            {"email": None, "password": "test123"},
            {"email": 123, "password": "test123"},
            {"email": [], "password": "test123"},
            {"email": {}, "password": "test123"},
            {"email": "test@example.com", "password": None},
            {"email": "test@example.com", "password": 123},
            {"email": "test@example.com", "password": []},
            {"email": "test@example.com", "password": {}}
        ]
        
        for attempt in bypass_attempts:
            response = await test_client.post("/api/v1/auth/register", json=attempt)
            
            # 잘못된 데이터 타입은 422를 반환해야 함
            if response.status_code == 200:
                security_suite.add_vulnerability(
                    "Data Validation",
                    f"Data validation bypass successful: {attempt}",
                    "Medium",
                    "Implement strict data type validation"
                )

class TestInfrastructureSecurity:
    """인프라 보안 테스트"""
    
    async def test_security_headers(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """보안 헤더 테스트"""
        response = await test_client.get("/api/v1/subscriptions/plans")
        
        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        for header, expected_value in required_headers.items():
            actual_value = response.headers.get(header)
            if actual_value != expected_value:
                security_suite.add_vulnerability(
                    "Security Headers",
                    f"Missing or incorrect security header: {header}",
                    "Medium",
                    f"Set {header} header to {expected_value}"
                )
    
    async def test_cors_configuration(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """CORS 설정 테스트"""
        # OPTIONS 요청으로 CORS 테스트
        response = await test_client.options("/api/v1/subscriptions/plans")
        
        cors_headers = response.headers.get("Access-Control-Allow-Origin")
        if cors_headers == "*":
            security_suite.add_vulnerability(
                "CORS",
                "CORS is configured to allow all origins (*)",
                "Medium",
                "Restrict CORS to specific trusted origins"
            )
    
    async def test_error_information_disclosure(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """에러 정보 노출 테스트"""
        # 존재하지 않는 엔드포인트 접근
        response = await test_client.get("/api/v1/nonexistent")
        
        # 에러 응답에 민감한 정보가 포함되어 있으면 안됨
        error_text = response.text.lower()
        sensitive_terms = [
            "stack trace",
            "file path",
            "database",
            "password",
            "secret",
            "key",
            "token"
        ]
        
        for term in sensitive_terms:
            if term in error_text:
                security_suite.add_vulnerability(
                    "Information Disclosure",
                    f"Sensitive information '{term}' found in error response",
                    "Low",
                    "Sanitize error messages to prevent information disclosure"
                )

class TestCryptographicSecurity:
    """암호화 보안 테스트"""
    
    async def test_password_hashing(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """비밀번호 해싱 테스트"""
        # 등록 후 데이터베이스에서 비밀번호 확인 (실제로는 데이터베이스 접근 필요)
        # 여기서는 응답에서 비밀번호가 노출되지 않는지만 확인
        register_data = {
            "email": "hash_test@example.com",
            "password": "testpassword123",
            "first_name": "Hash",
            "last_name": "Test"
        }
        
        response = await test_client.post("/api/v1/auth/register", json=register_data)
        
        if response.status_code == 200:
            user_data = response.json()
            
            # 원본 비밀번호가 응답에 포함되어 있으면 안됨
            if "testpassword123" in str(user_data):
                security_suite.add_vulnerability(
                    "Password Security",
                    "Plain text password found in response",
                    "Critical",
                    "Ensure passwords are properly hashed and never returned in responses"
                )
    
    async def test_jwt_security(self, test_client: AsyncClient, security_suite: SecurityTestSuite):
        """JWT 보안 테스트"""
        # 로그인하여 토큰 획득
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        
        # 먼저 사용자 등록
        register_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        await test_client.post("/api/v1/auth/register", json=register_data)
        
        login_response = await test_client.post("/api/v1/auth/login", data=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            
            if token:
                # JWT 토큰 구조 확인
                try:
                    # JWT는 3부분으로 구성되어야 함 (header.payload.signature)
                    parts = token.split(".")
                    if len(parts) != 3:
                        security_suite.add_vulnerability(
                            "JWT Security",
                            "Invalid JWT token structure",
                            "High",
                            "Ensure JWT tokens are properly formatted"
                        )
                    
                    # 헤더와 페이로드 디코딩 시도
                    header = json.loads(base64.b64decode(parts[0] + "=="))
                    payload = json.loads(base64.b64decode(parts[1] + "=="))
                    
                    # 알고리즘이 안전한지 확인
                    if header.get("alg") not in ["HS256", "RS256", "ES256"]:
                        security_suite.add_vulnerability(
                            "JWT Security",
                            f"Unsafe JWT algorithm: {header.get('alg')}",
                            "Medium",
                            "Use secure JWT algorithms (HS256, RS256, ES256)"
                        )
                    
                except Exception as e:
                    security_suite.add_vulnerability(
                        "JWT Security",
                        f"JWT token parsing failed: {str(e)}",
                        "Medium",
                        "Ensure JWT tokens are properly formatted"
                    )

# 보안 테스트 실행을 위한 헬퍼 함수
async def run_security_tests():
    """보안 테스트 실행"""
    print("Running security tests...")
    
    # 테스트 실행
    pytest.main(["-v", "tests/test_security.py", "-s"])
    
    print("Security tests completed!")

if __name__ == "__main__":
    asyncio.run(run_security_tests())
