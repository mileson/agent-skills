---
name: backend-fastapi-endpoint-creator
description: 自动创建 FastAPI 端点，包括路由定义、Pydantic 模型、业务逻辑、错误处理、认证授权、OpenAPI 文档和单元测试，遵循项目的后端架构规范
---

# FastAPI 端点创建器

## When to Use

Use this skill when you need to:
- 在 FastAPI 后端项目中快速创建标准化的 API 端点
- 快速实现 CRUD 操作接口
- 标准化 API 设计和实现
- 保持后端代码结构一致性
- 创建新的 RESTful API 端点

## Prerequisites

确保项目具备以下结构：
- `app/api/v1/endpoints/` - API 路由目录
- `app/models/` - SQLAlchemy 数据模型
- `app/schemas/` - Pydantic 请求/响应模型
- `app/services/` - 业务逻辑层
- `app/core/deps.py` - 依赖注入
- `app/core/security.py` - 认证授权

## Instructions

### 步骤 1: 确定端点基本信息

收集以下信息：
- **资源名称**: 如 `user`, `template`, `task`
- **操作类型**: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`
- **路径**: 如 `/api/v1/users`, `/api/v1/users/{user_id}`
- **认证要求**: 是否需要登录、特定权限
- **请求/响应数据**: 数据字段和类型

### 步骤 2: 创建 Pydantic Schema 模型

在 `app/schemas/[resource].py` 创建请求和响应模型：

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# ============================================
# 基础 Schema
# ============================================

class [Resource]Base(BaseModel):
    """[资源]基础 Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="名称")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('名称不能为空')
        return v.strip()


# ============================================
# 创建 Schema (POST 请求)
# ============================================

class [Resource]Create(BaseModel):
    """创建[资源]请求 Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="名称")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "示例名称",
                "description": "示例描述"
            }
        }


# ============================================
# 更新 Schema (PUT/PATCH 请求)
# ============================================

class [Resource]Update(BaseModel):
    """更新[资源]请求 Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "更新后的名称"
            }
        }


# ============================================
# 响应 Schema
# ============================================

class [Resource]Response(BaseModel):
    """[资源]响应 Schema"""
    id: str = Field(..., description="资源ID")
    name: str = Field(..., description="名称")
    description: Optional[str] = Field(None, description="描述")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True  # 允许从 ORM 模型创建


class [Resource]ListResponse(BaseModel):
    """[资源]列表响应 Schema"""
    items: List[[Resource]Response] = Field(..., description="资源列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "page_size": 20
            }
        }
```

### 步骤 3: 创建 API 路由端点

在 `app/api/v1/endpoints/[resource].py` 创建路由：

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.[resource] import (
    [Resource]Create,
    [Resource]Update,
    [Resource]Response,
    [Resource]ListResponse
)
from app.services.[resource]_service import [Resource]Service

router = APIRouter()

# ============================================
# 创建[资源]
# ============================================

@router.post(
    "/",
    response_model=[Resource]Response,
    status_code=status.HTTP_201_CREATED,
    summary="创建[资源]",
    description="创建新的[资源]记录",
    responses={
        201: {"description": "创建成功"},
        400: {"description": "请求参数错误"},
        401: {"description": "未授权"},
        409: {"description": "资源已存在"}
    }
)
async def create_[resource](
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    [resource]_in: [Resource]Create
) -> [Resource]Response:
    """
    创建新的[资源]
    
    - **name**: 资源名称（必填）
    - **description**: 资源描述（可选）
    """
    try:
        service = [Resource]Service(db)
        [resource] = await service.create(
            user_id=current_user.id,
            **[resource]_in.model_dump()
        )
        return [Resource]Response.model_validate([resource])
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # 记录日志
        logger.error(f"创建[资源]失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建失败，请稍后重试"
        )


# ============================================
# 获取[资源]列表（支持分页和筛选）
# ============================================

@router.get(
    "/",
    response_model=[Resource]ListResponse,
    summary="获取[资源]列表",
    description="获取[资源]列表，支持分页和筛选"
)
async def list_[resource]s(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: Optional[str] = Query("created_at", description="排序字段"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="排序方向")
) -> [Resource]ListResponse:
    """
    获取[资源]列表
    
    支持参数：
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认20，最大100）
    - **search**: 搜索关键词
    - **sort_by**: 排序字段
    - **sort_order**: 排序方向（asc/desc）
    """
    service = [Resource]Service(db)
    
    items, total = await service.get_list(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return [Resource]ListResponse(
        items=[Resource]Response.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


# ============================================
# 获取单个[资源]详情
# ============================================

@router.get(
    "/{[resource]_id}",
    response_model=[Resource]Response,
    summary="获取[资源]详情",
    responses={
        200: {"description": "获取成功"},
        404: {"description": "资源不存在"}
    }
)
async def get_[resource](
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    [resource]_id: str
) -> [Resource]Response:
    """
    根据ID获取[资源]详情
    """
    service = [Resource]Service(db)
    [resource] = await service.get_by_id([resource]_id, user_id=current_user.id)
    
    if not [resource]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    return [Resource]Response.model_validate([resource])


# ============================================
# 更新[资源]
# ============================================

@router.put(
    "/{[resource]_id}",
    response_model=[Resource]Response,
    summary="更新[资源]",
    responses={
        200: {"description": "更新成功"},
        404: {"description": "资源不存在"}
    }
)
async def update_[resource](
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    [resource]_id: str,
    [resource]_in: [Resource]Update
) -> [Resource]Response:
    """
    更新[资源]信息
    """
    service = [Resource]Service(db)
    
    # 检查资源是否存在
    existing = await service.get_by_id([resource]_id, user_id=current_user.id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    # 执行更新
    updated = await service.update(
        [resource]_id=existing.id,
        user_id=current_user.id,
        **[resource]_in.model_dump(exclude_unset=True)
    )
    
    return [Resource]Response.model_validate(updated)


# ============================================
# 删除[资源]（软删除）
# ============================================

@router.delete(
    "/{[resource]_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除[资源]",
    responses={
        204: {"description": "删除成功"},
        404: {"description": "资源不存在"}
    }
)
async def delete_[resource](
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    [resource]_id: str
):
    """
    软删除[资源]（标记为已删除，不实际删除数据）
    """
    service = [Resource]Service(db)
    
    # 检查资源是否存在
    existing = await service.get_by_id([resource]_id, user_id=current_user.id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    # 执行软删除
    await service.soft_delete([resource]_id, user_id=current_user.id)
    
    return None
```

### 步骤 4: 创建 Service 业务逻辑层

在 `app/services/[resource]_service.py` 创建服务：

```python
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple, Optional
from datetime import datetime

from app.models.[resource] import [Resource]
from app.core.logger import logger

class [Resource]Service:
    """[资源]业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        **kwargs
    ) -> [Resource]:
        """创建[资源]"""
        [resource] = [Resource](
            user_id=user_id,
            name=name,
            description=description,
            **kwargs
        )
        
        self.db.add([resource])
        await self.db.commit()
        await self.db.refresh([resource])
        
        logger.info(f"创建[资源]成功: id={[resource].id}, name={name}")
        return [resource]
    
    async def get_by_id(
        self,
        [resource]_id: str,
        user_id: str
    ) -> Optional[[Resource]]:
        """根据ID获取[资源]"""
        query = select([Resource]).where(
            [Resource].id == [resource]_id,
            [Resource].user_id == user_id,
            [Resource].deleted_at.is_(None)  # 排除已删除
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_list(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[[Resource]], int]:
        """获取[资源]列表（支持分页和搜索）"""
        # 基础查询
        query = select([Resource]).where(
            [Resource].user_id == user_id,
            [Resource].deleted_at.is_(None)
        )
        
        # 搜索过滤
        if search:
            query = query.where(
                or_(
                    [Resource].name.ilike(f"%{search}%"),
                    [Resource].description.ilike(f"%{search}%")
                )
            )
        
        # 排序
        order_column = getattr([Resource], sort_by, [Resource].created_at)
        if sort_order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
        
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0
        
        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # 执行查询
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def update(
        self,
        [resource]_id: str,
        user_id: str,
        **update_data
    ) -> [Resource]:
        """更新[资源]"""
        [resource] = await self.get_by_id([resource]_id, user_id)
        if not [resource]:
            raise ValueError("资源不存在")
        
        # 更新字段
        for field, value in update_data.items():
            if hasattr([resource], field) and value is not None:
                setattr([resource], field, value)
        
        [resource].updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh([resource])
        
        logger.info(f"更新[资源]成功: id={[resource]_id}")
        return [resource]
    
    async def soft_delete(self, [resource]_id: str, user_id: str):
        """软删除[资源]"""
        [resource] = await self.get_by_id([resource]_id, user_id)
        if not [resource]:
            raise ValueError("资源不存在")
        
        [resource].deleted_at = datetime.utcnow()
        await self.db.commit()
        
        logger.info(f"软删除[资源]成功: id={[resource]_id}")
```

### 步骤 5: 注册路由到主应用

在 `app/api/v1/api.py` 注册路由：

```python
from fastapi import APIRouter
from app.api.v1.endpoints import [resource]

api_router = APIRouter()

# 注册[资源]路由
api_router.include_router(
    [resource].router,
    prefix="/[resources]",  # 复数形式
    tags=["[Resources]"]     # OpenAPI 标签
)
```

### 步骤 6: 创建单元测试

在 `tests/api/test_[resource].py` 创建测试：

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from tests.utils import create_test_user, get_auth_headers

@pytest.mark.asyncio
async def test_create_[resource](
    client: AsyncClient,
    db: AsyncSession
):
    """测试创建[资源]"""
    user = await create_test_user(db)
    headers = get_auth_headers(user)
    
    response = await client.post(
        "/api/v1/[resources]/",
        headers=headers,
        json={
            "name": "测试[资源]",
            "description": "测试描述"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "测试[资源]"
    assert "id" in data

@pytest.mark.asyncio
async def test_list_[resource]s(
    client: AsyncClient,
    db: AsyncSession
):
    """测试获取[资源]列表"""
    user = await create_test_user(db)
    headers = get_auth_headers(user)
    
    response = await client.get(
        "/api/v1/[resources]/?page=1&page_size=20",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
```

### 步骤 7: 更新 OpenAPI 文档

确保在 `app/main.py` 中配置了 OpenAPI：

```python
app = FastAPI(
    title="[Project Name] API",
    description="[项目描述]",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

访问 `http://localhost:8000/docs` 查看自动生成的 API 文档。

## Best Practices

1. **错误处理**: 使用 `HTTPException` 返回标准化错误
2. **日志记录**: 记录关键操作和错误
3. **软删除**: 使用 `deleted_at` 字段而非物理删除
4. **分页查询**: 默认限制 `page_size` 最大值
5. **参数验证**: 使用 Pydantic 的 `Field` 和 `validator`
6. **认证授权**: 所有端点都应有适当的权限检查

## Output Checklist

完成后确认：
- ✅ Pydantic Schema 已创建
- ✅ API 路由已定义
- ✅ Service 业务逻辑已实现
- ✅ 路由已注册到主应用
- ✅ 单元测试已创建
- ✅ OpenAPI 文档可访问
