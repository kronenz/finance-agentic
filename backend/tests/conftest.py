"""
pytest 설정 및 픽스처
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# 테스트용 데이터베이스 URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# 테스트용 엔진 생성
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

# 테스트용 세션 팩토리
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 픽스처"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session():
    """데이터베이스 세션 픽스처"""
    # 테이블 생성
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 세션 생성
    async with TestSessionLocal() as session:
        yield session
    
    # 테이블 삭제
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(db_session):
    """테스트 클라이언트 픽스처"""
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    """테스트 사용자 데이터"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }

@pytest.fixture
def test_login_data():
    """테스트 로그인 데이터"""
    return {
        "username": "test@example.com",
        "password": "TestPassword123!"
    }
