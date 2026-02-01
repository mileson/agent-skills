"""
用户登录 API 测试

测试用户认证相关接口，包括登录、登出、token 刷新等。
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def get_test_user(db: AsyncSession):
    """获取或创建测试用户"""
    from app.models.user import User
    from app.core.security import hash_password

    user = await db.get(User, "test_user_id")
    if not user:
        user = User(
            id="test_user_id",
            username="testuser",
            hashed_password=hash_password("testpass123")
        )
        db.add(user)
        await db.commit()
    return user


# ============================================
# 登录接口测试
# ============================================

class TestLoginAPI:
    """登录 API 测试类"""

    async def test_login_success(self, client: AsyncClient, db: AsyncSession):
        """测试用户登录 - 成功场景"""
        # Arrange
        await get_test_user(db)

        # Act
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, db: AsyncSession):
        """测试用户登录 - 错误密码"""
        # Arrange
        await get_test_user(db)

        # Act
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )

        # Assert
        assert response.status_code == 401

    async def test_login_user_not_found(self, client: AsyncClient):
        """测试用户登录 - 用户不存在"""
        # Act
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "anypassword"}
        )

        # Assert
        assert response.status_code == 401

    async def test_login_missing_fields(self, client: AsyncClient):
        """测试用户登录 - 缺少必填字段"""
        # Act
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser"}  # 缺少密码
        )

        # Assert
        assert response.status_code == 422


# ============================================
# Token 刷新测试
# ============================================

class TestTokenRefresh:
    """Token 刷新 API 测试类"""

    async def test_refresh_token_success(self, client: AsyncClient, db: AsyncSession):
        """测试刷新 token - 成功场景"""
        # Arrange
        await get_test_user(db)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        refresh_token = login_response.json()["refresh_token"]

        # Act
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    async def test_refresh_token_invalid(self, client: AsyncClient):
        """测试刷新 token - 无效 token"""
        # Act
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )

        # Assert
        assert response.status_code == 401
