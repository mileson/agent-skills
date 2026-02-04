# 模式检测逻辑说明

## 检测规则

Feature Development Skill 支持两种开发模式：

### 模式1: Greenfield（从0到1全新项目开发）

**触发条件**:
- Workspace 目录下**不存在** `doc/` 目录

**特征**:
- 全新项目，无历史代码和文档
- 需要完整的需求沟通和架构设计
- 生成完整的文档结构

### 模式2: Brownfield（基于已有系统的迭代优化）

**触发条件**:
- Workspace 目录下**存在** `doc/` 目录

**特征**:
- 已有系统基础
- 需要理解现有架构和文档
- 生成增量文档，更新版本号

## 检测脚本

使用 `scripts/detect_project_mode.py` 自动检测：

```python
import os
from pathlib import Path

def detect_project_mode(workspace_path: str) -> dict:
    doc_path = Path(workspace_path) / "doc"
    
    if not doc_path.exists():
        return {
            "mode": "greenfield",
            "hasDocStructure": False
        }
    
    # 扫描已有文档结构
    existing_docs = {}
    for folder in ["01_PRD", "02_arch", "03_database", "04_api"]:
        folder_path = doc_path / folder
        if folder_path.exists():
            md_files = list(folder_path.glob("*.md"))
            existing_docs[folder.split("_")[1].lower()] = [f.name for f in md_files]
    
    # 检查 feature_list.json
    feature_list = doc_path / "06_dev-logs" / "feature_list.json"
    existing_feature_list = str(feature_list) if feature_list.exists() else None
    
    return {
        "mode": "brownfield",
        "hasDocStructure": True,
        "existingDocs": existing_docs,
        "existingFeatureList": existing_feature_list
    }
```

## 检测结果示例

### Greenfield 示例

```json
{
  "mode": "greenfield",
  "hasDocStructure": false
}
```

### Brownfield 示例

```json
{
  "mode": "brownfield",
  "hasDocStructure": true,
  "existingDocs": {
    "prd": ["1_产品概述.md", "2_用户画像.md", "3_核心流程.md"],
    "arch": ["1_技术选型.md", "2_系统架构.md"],
    "database": ["1_数据表设计.md", "2_建表SQL.sql"],
    "api": ["1_RESTful_API.md"]
  },
  "existingFeatureList": "/path/to/doc/06_dev-logs/feature_list.json"
}
```

## 如何使用

在启动 Feature Development Skill 时，首先运行模式检测：

```bash
python3 scripts/detect_project_mode.py
```

根据检测结果，选择对应的工作流：
- Greenfield: 阅读 `references/greenfield/` 下的指南
- Brownfield: 阅读 `references/brownfield/` 下的指南
