"""
API 测试脚本模板

用于测试后端 API 接口，包含请求构造、响应验证、错误处理等标准模式。
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


# ============================================
# 测试配置和辅助函数
# ============================================

async def get_auth_headers(client: AsyncClient, username: str, password: str) -> dict:
    """获取认证头信息"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    return {"Authorization": f"Bearer {data['access_token']}"}


async def create_test_user(db: AsyncSession, username: str = "test_user"):
    """创建测试用户"""
    # 实现用户创建逻辑
    pass


# ============================================
# API 端点测试
# ============================================

class Test[EndpointName]:
    """[API 端点名称] 测试类"""

    async def test_list_[resources]_success(
        self,
        client: AsyncClient,
        db: AsyncSession
    ):
        """测试获取 [资源] 列表 - 成功场景"""
        # Arrange
        user = await create_test_user(db)
        headers = await get_auth_headers(client, user.username, "password")

        # Act
        response = await client.get(
            "/api/v1/[resources]/",
            headers=headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    async def test_get_[resource]_by_id_success(
        self,
        client: AsyncClient,
        db: AsyncSession
    ):
        """测试根据 ID 获取 [资源] - 成功场景"""
        # Arrange
        user = await create_test_user(db)
        headers = await get_auth_headers(client, user.username, "password")
        resource_id = "test_id_123"

        # Act
        response = await client.get(
            f"/api/v1/[resources]/{resource_id}",
            headers=headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resource_id

    async def test_create_[resource]_success(
        self,
        client: AsyncClient,
        db: AsyncSession
    ):
        """测试创建 [资源] - 成功场景"""
        # Arrange
        user = await create_test_user(db)
        headers = await get_auth_headers(client, user.username, "password")

        # Act
        response = await client.post(
            "/api/v1/[resources]/",
            headers=headers,
            json={
                "name": "测试 [资源]",
                "description": "测试描述"
            }
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "测试 [资源]"
        assert "id" in data

    async def test_create_[resource]_validation_error(
        self,
        client: AsyncClient,
        db: AsyncSession
    ):
        """测试创建 [资源] - 参数验证失败"""
        # Arrange
        user = await create_test_user(db)
        headers = await get_auth_headers(client, user.username, "password")

        # Act
        response = await client.post(
            "/api/v1/[resources]/",
            headers=headers,
            json={"name": ""}  # 无效的名称
        )

        # Assert
        assert response.status_code == 422

    async def test_update_[resource]_success(
        self,
        client: AsyncClient,
        db: AsyncSession
    ):
        """测试更新 [资源] - 成功场景"""
        # Arrange
        user = await create_test_user(db)
        headers = await get_auth_headers(client, user.username, "password")
        resource_id = "test_id_123"

        # Act
        response = await client.put(
            f"/api/v1/[resources]/{resource_id}",
            headers=headers,
            json={"name": "更新后的名称"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新后的名称"

    async def test_delete_[resource]_success(
        self,
        client: AsyncClient,
        db: AsyncSession
    ):
        """测试删除 [资源] - 成功场景"""
        # Arrange
        user = await create_test_user(db)
        headers = await get_auth_headers(client, user.username, "password")
        resource_id = "test_id_123"

        # Act
        response = await client.delete(
            f"/api/v1/[resources]/{resource_id}",
            headers=headers
        )

        # Assert
        assert response.status_code == 204

    async def test_unauthorized_access(
        self,
        client: AsyncClient
    ):
        """测试未授权访问 - 失败场景"""
        # Act
        response = await client.get("/api/v1/[resources]/")

        # Assert
        assert response.status_code == 401
