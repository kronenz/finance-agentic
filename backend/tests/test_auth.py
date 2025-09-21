"""
인증 API 테스트
"""

import pytest
from httpx import AsyncClient
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate

class TestAuthAPI:
    """인증 API 테스트 클래스"""
    
    async def test_register_user_success(self, client: AsyncClient, test_user_data):
        """사용자 회원가입 성공 테스트"""
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["first_name"] == test_user_data["first_name"]
        assert data["last_name"] == test_user_data["last_name"]
        assert "id" in data
        assert data["is_active"] is True
        assert data["email_verified"] is False
    
    async def test_register_user_duplicate_email(self, client: AsyncClient, test_user_data):
        """중복 이메일 회원가입 실패 테스트"""
        # 첫 번째 회원가입
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # 두 번째 회원가입 (중복 이메일)
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "이미 등록된 이메일입니다" in data["detail"]
    
    async def test_register_user_invalid_email(self, client: AsyncClient):
        """잘못된 이메일 형식 회원가입 실패 테스트"""
        invalid_data = {
            "email": "invalid-email",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = await client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422
    
    async def test_register_user_weak_password(self, client: AsyncClient):
        """약한 비밀번호 회원가입 실패 테스트"""
        weak_password_data = {
            "email": "test@example.com",
            "password": "123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = await client.post("/api/v1/auth/register", json=weak_password_data)
        assert response.status_code == 422
    
    async def test_login_success(self, client: AsyncClient, test_user_data, test_login_data):
        """로그인 성공 테스트"""
        # 먼저 회원가입
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # 로그인
        response = await client.post("/api/v1/auth/login", data=test_login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800
    
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """잘못된 자격증명 로그인 실패 테스트"""
        invalid_login_data = {
            "username": "nonexistent@example.com",
            "password": "WrongPassword123!"
        }
        
        response = await client.post("/api/v1/auth/login", data=invalid_login_data)
        assert response.status_code == 401
        data = response.json()
        assert "이메일 또는 비밀번호가 올바르지 않습니다" in data["detail"]
    
    async def test_get_current_user_success(self, client: AsyncClient, test_user_data, test_login_data):
        """현재 사용자 정보 조회 성공 테스트"""
        # 회원가입 및 로그인
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post("/api/v1/auth/login", data=test_login_data)
        token = login_response.json()["access_token"]
        
        # 현재 사용자 정보 조회
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["first_name"] == test_user_data["first_name"]
        assert data["last_name"] == test_user_data["last_name"]
    
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """인증되지 않은 사용자 정보 조회 실패 테스트"""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    async def test_logout_success(self, client: AsyncClient, test_user_data, test_login_data):
        """로그아웃 성공 테스트"""
        # 회원가입 및 로그인
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post("/api/v1/auth/login", data=test_login_data)
        token = login_response.json()["access_token"]
        
        # 로그아웃
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post("/api/v1/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "성공적으로 로그아웃되었습니다" in data["message"]
    
    async def test_forgot_password_success(self, client: AsyncClient, test_user_data):
        """비밀번호 재설정 요청 성공 테스트"""
        # 먼저 회원가입
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # 비밀번호 재설정 요청
        response = await client.post("/api/v1/auth/forgot-password", params={"email": test_user_data["email"]})
        
        assert response.status_code == 200
        data = response.json()
        assert "비밀번호 재설정 링크가 이메일로 전송되었습니다" in data["message"]
    
    async def test_forgot_password_nonexistent_email(self, client: AsyncClient):
        """존재하지 않는 이메일 비밀번호 재설정 요청 테스트"""
        response = await client.post("/api/v1/auth/forgot-password", params={"email": "nonexistent@example.com"})
        
        # 이메일이 존재하지 않아도 성공으로 응답 (보안상 이유)
        assert response.status_code == 200
