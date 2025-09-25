# 보안 테스트: 취약점 검증
import pytest
import asyncio
import aiohttp
import json
from typing import Dict, Any, List
import random
import string

class SecurityTestRunner:
    """보안 테스트 실행기"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
    
    async def test_sql_injection(self, session: aiohttp.ClientSession):
        """SQL 인젝션 테스트"""
        print("Testing SQL Injection vulnerabilities...")
        
        # SQL 인젝션 페이로드
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "' OR 1=1 --",
            "admin'--",
            "admin'/*",
            "' OR 'x'='x",
            "' OR 1=1#",
            "') OR ('1'='1",
        ]
        
        results = []
        
        for payload in sql_payloads:
            # 로그인 시도
            login_data = {
                "email": payload,
                "password": "password"
            }
            
            try:
                async with session.post(
                    f"{self.base_url}/api/v1/auth/login",
                    data=login_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = {
                        "payload": payload,
                        "status_code": response.status,
                        "vulnerable": response.status == 200 and "access_token" in await response.text()
                    }
                    results.append(result)
                    
                    if result["vulnerable"]:
                        print(f"POTENTIAL SQL INJECTION: {payload}")
            except Exception as e:
                print(f"SQL injection test error with payload {payload}: {e}")
        
        return results
    
    async def test_xss_vulnerabilities(self, session: aiohttp.ClientSession):
        """XSS 취약점 테스트"""
        print("Testing XSS vulnerabilities...")
        
        # XSS 페이로드
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "\"><script>alert('XSS')</script>",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
        ]
        
        results = []
        
        for payload in xss_payloads:
            # 사용자 등록 시도
            register_data = {
                "first_name": payload,
                "last_name": "Test",
                "email": f"xss_test_{random.randint(1000, 9999)}@example.com",
                "password": "TestPassword123!",
                "agreeToTerms": True
            }
            
            try:
                async with session.post(
                    f"{self.base_url}/api/v1/auth/register",
                    json=register_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_text = await response.text()
                    result = {
                        "payload": payload,
                        "status_code": response.status,
                        "vulnerable": payload in response_text,
                        "response_contains_payload": payload in response_text
                    }
                    results.append(result)
                    
                    if result["vulnerable"]:
                        print(f"POTENTIAL XSS: {payload}")
            except Exception as e:
                print(f"XSS test error with payload {payload}: {e}")
        
        return results
    
    async def test_authentication_bypass(self, session: aiohttp.ClientSession):
        """인증 우회 테스트"""
        print("Testing authentication bypass...")
        
        results = []
        
        # 1. 토큰 없이 보호된 엔드포인트 접근
        protected_endpoints = [
            "/api/v1/ai/status",
            "/api/v1/trading/portfolio",
            "/api/v1/subscriptions/plans",
            "/api/v1/monitoring/metrics",
        ]
        
        for endpoint in protected_endpoints:
            try:
                async with session.get(
                    f"{self.base_url}{endpoint}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = {
                        "endpoint": endpoint,
                        "status_code": response.status,
                        "bypassed": response.status == 200
                    }
                    results.append(result)
                    
                    if result["bypassed"]:
                        print(f"AUTHENTICATION BYPASS: {endpoint}")
            except Exception as e:
                print(f"Auth bypass test error for {endpoint}: {e}")
        
        # 2. 잘못된 토큰으로 접근
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
            "",
            "null",
            "undefined",
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            
            try:
                async with session.get(
                    f"{self.base_url}/api/v1/ai/status",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = {
                        "token": token,
                        "status_code": response.status,
                        "bypassed": response.status == 200
                    }
                    results.append(result)
                    
                    if result["bypassed"]:
                        print(f"AUTHENTICATION BYPASS with token: {token}")
            except Exception as e:
                print(f"Auth bypass test error with token {token}: {e}")
        
        return results
    
    async def test_authorization_bypass(self, session: aiohttp.ClientSession):
        """권한 우회 테스트"""
        print("Testing authorization bypass...")
        
        # 테스트 사용자 생성
        test_user_email = f"auth_test_{random.randint(1000, 9999)}@example.com"
        test_user_password = "TestPassword123!"
        
        # 사용자 등록
        register_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": test_user_email,
            "password": test_user_password,
            "agreeToTerms": True
        }
        
        try:
            async with session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=register_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status not in [201, 409]:
                    print("Failed to create test user for authorization test")
                    return []
        except Exception as e:
            print(f"Failed to create test user: {e}")
            return []
        
        # 로그인
        login_data = {
            "email": test_user_email,
            "password": test_user_password
        }
        
        try:
            async with session.post(
                f"{self.base_url}/api/v1/auth/login",
                data=login_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    print("Failed to login test user")
                    return []
                
                login_result = await response.json()
                token = login_result.get("access_token")
                if not token:
                    print("No access token received")
                    return []
        except Exception as e:
            print(f"Failed to login test user: {e}")
            return []
        
        headers = {"Authorization": f"Bearer {token}"}
        results = []
        
        # 다른 사용자의 데이터 접근 시도
        # (실제로는 사용자 ID를 조작하여 다른 사용자의 데이터에 접근 시도)
        
        # 1. 다른 사용자의 주문 조회 시도
        other_user_orders = [
            "order_999999",
            "order_000001",
            "order_000002",
        ]
        
        for order_id in other_user_orders:
            try:
                async with session.get(
                    f"{self.base_url}/api/v1/trading/orders/{order_id}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = {
                        "endpoint": f"/api/v1/trading/orders/{order_id}",
                        "status_code": response.status,
                        "unauthorized_access": response.status == 200
                    }
                    results.append(result)
                    
                    if result["unauthorized_access"]:
                        print(f"UNAUTHORIZED ACCESS: {order_id}")
            except Exception as e:
                print(f"Authorization test error for order {order_id}: {e}")
        
        return results
    
    async def test_input_validation(self, session: aiohttp.ClientSession):
        """입력값 검증 테스트"""
        print("Testing input validation...")
        
        results = []
        
        # 1. 매우 긴 입력값 테스트
        long_string = "A" * 10000
        
        register_data = {
            "first_name": long_string,
            "last_name": "Test",
            "email": f"long_input_{random.randint(1000, 9999)}@example.com",
            "password": "TestPassword123!",
            "agreeToTerms": True
        }
        
        try:
            async with session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=register_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                result = {
                    "test_type": "long_input",
                    "status_code": response.status,
                    "handled_properly": response.status in [400, 422, 413]
                }
                results.append(result)
                
                if not result["handled_properly"]:
                    print(f"INPUT VALIDATION ISSUE: Long input not properly handled")
        except Exception as e:
            print(f"Long input test error: {e}")
        
        # 2. 특수문자 입력 테스트
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        register_data = {
            "first_name": special_chars,
            "last_name": special_chars,
            "email": f"special_chars_{random.randint(1000, 9999)}@example.com",
            "password": "TestPassword123!",
            "agreeToTerms": True
        }
        
        try:
            async with session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=register_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                result = {
                    "test_type": "special_chars",
                    "status_code": response.status,
                    "handled_properly": response.status in [201, 400, 422]
                }
                results.append(result)
        except Exception as e:
            print(f"Special chars test error: {e}")
        
        # 3. SQL 특수문자 입력 테스트
        sql_chars = "'; DROP TABLE users; --"
        
        register_data = {
            "first_name": sql_chars,
            "last_name": "Test",
            "email": f"sql_chars_{random.randint(1000, 9999)}@example.com",
            "password": "TestPassword123!",
            "agreeToTerms": True
        }
        
        try:
            async with session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=register_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                result = {
                    "test_type": "sql_chars",
                    "status_code": response.status,
                    "handled_properly": response.status in [201, 400, 422]
                }
                results.append(result)
        except Exception as e:
            print(f"SQL chars test error: {e}")
        
        return results
    
    async def test_rate_limiting(self, session: aiohttp.ClientSession):
        """속도 제한 테스트"""
        print("Testing rate limiting...")
        
        results = []
        
        # 빠른 연속 요청으로 속도 제한 테스트
        rapid_requests = 100
        success_count = 0
        rate_limited_count = 0
        
        for i in range(rapid_requests):
            try:
                async with session.get(
                    f"{self.base_url}/api/v1/ai/status",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        success_count += 1
                    elif response.status == 429:  # Too Many Requests
                        rate_limited_count += 1
            except Exception as e:
                print(f"Rate limiting test error: {e}")
        
        result = {
            "total_requests": rapid_requests,
            "successful_requests": success_count,
            "rate_limited_requests": rate_limited_count,
            "rate_limiting_working": rate_limited_count > 0
        }
        results.append(result)
        
        if not result["rate_limiting_working"]:
            print("RATE LIMITING ISSUE: No rate limiting detected")
        
        return results
    
    async def test_cors_vulnerabilities(self, session: aiohttp.ClientSession):
        """CORS 취약점 테스트"""
        print("Testing CORS vulnerabilities...")
        
        results = []
        
        # CORS preflight 요청 테스트
        cors_origins = [
            "https://malicious-site.com",
            "http://localhost:3000",
            "https://trusted-site.com",
            "null",
            "*",
        ]
        
        for origin in cors_origins:
            headers = {
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
            
            try:
                async with session.options(
                    f"{self.base_url}/api/v1/auth/login",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    cors_headers = {
                        "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                        "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                        "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                    }
                    
                    result = {
                        "origin": origin,
                        "status_code": response.status,
                        "cors_headers": cors_headers,
                        "vulnerable": cors_headers.get("Access-Control-Allow-Origin") == "*"
                    }
                    results.append(result)
                    
                    if result["vulnerable"]:
                        print(f"CORS VULNERABILITY: Wildcard CORS for origin {origin}")
            except Exception as e:
                print(f"CORS test error for origin {origin}: {e}")
        
        return results
    
    async def run_all_tests(self):
        """모든 보안 테스트 실행"""
        print("Starting Security Tests...")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            # SQL 인젝션 테스트
            sql_results = await self.test_sql_injection(session)
            self.test_results.extend(sql_results)
            
            # XSS 테스트
            xss_results = await self.test_xss_vulnerabilities(session)
            self.test_results.extend(xss_results)
            
            # 인증 우회 테스트
            auth_bypass_results = await self.test_authentication_bypass(session)
            self.test_results.extend(auth_bypass_results)
            
            # 권한 우회 테스트
            authz_bypass_results = await self.test_authorization_bypass(session)
            self.test_results.extend(authz_bypass_results)
            
            # 입력값 검증 테스트
            input_validation_results = await self.test_input_validation(session)
            self.test_results.extend(input_validation_results)
            
            # 속도 제한 테스트
            rate_limiting_results = await self.test_rate_limiting(session)
            self.test_results.extend(rate_limiting_results)
            
            # CORS 테스트
            cors_results = await self.test_cors_vulnerabilities(session)
            self.test_results.extend(cors_results)
        
        # 결과 요약
        self.print_summary()
    
    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 50)
        print("SECURITY TEST SUMMARY")
        print("=" * 50)
        
        vulnerabilities_found = 0
        
        for result in self.test_results:
            if result.get("vulnerable") or result.get("bypassed") or result.get("unauthorized_access"):
                vulnerabilities_found += 1
                print(f"VULNERABILITY FOUND: {result}")
        
        print(f"\nTotal vulnerabilities found: {vulnerabilities_found}")
        print(f"Total tests run: {len(self.test_results)}")
        
        if vulnerabilities_found == 0:
            print("✅ No security vulnerabilities detected!")
        else:
            print("❌ Security vulnerabilities detected! Please review and fix.")

async def main():
    """메인 테스트 실행"""
    runner = SecurityTestRunner()
    await runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
