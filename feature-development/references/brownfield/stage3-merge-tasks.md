# 阶段3: 增量任务拆解（Brownfield）

## 目标

将增量需求拆解为任务，合并到现有 feature_list.json。

## 任务合并策略

### 1. 读取现有 feature_list.json

```bash
python3 scripts/merge_feature_list.py \
  --existing doc/06_dev-logs/feature_list.json \
  --new-features new_features.json \
  --new-phase-name "Phase 03: 智能推荐系统" \
  --new-version "2.0"
```

### 2. 生成新的 Phase

**Phase 编号延续**：
- 当前最新 Phase: Phase 02
- 新增 Phase: Phase 03

**标记版本号**：
- version: "2.0"
- baseVersion: "1.5"

**标记依赖关系**：
- baseFeatures: ["TASK-001", "TASK-014", "TASK-020"]

### 3. 合并后的 feature_list.json

```json
{
  "project": {
    "name": "电商平台",
    "version": "2.0.0",
    "baseVersion": "1.5",
    "lastUpdated": "2026-02-04T14:30:00Z"
  },
  "phases": [
    {
      "phaseId": "phase-01",
      "phaseName": "Phase 01: 基础环境（v1.0）",
      "version": "1.0",
      "status": "completed"
    },
    {
      "phaseId": "phase-02",
      "phaseName": "Phase 02: 核心功能（v1.0-v1.5）",
      "version": "1.5",
      "status": "completed"
    },
    {
      "phaseId": "phase-03",
      "phaseName": "Phase 03: 智能推荐系统（v2.0 新增）",
      "version": "2.0",
      "status": "pending",
      "baseFeatures": ["TASK-001", "TASK-014", "TASK-020"],
      "features": [
        {
          "featureId": "TASK-051",
          "category": "functional",
          "description": "推荐引擎基础框架",
          "status": "pending",
          "dependencies": []
        }
      ]
    }
  ],
  "metadata": {
    "totalFeatures": 55,
    "completedFeatures": 50,
    "pendingFeatures": 5,
    "currentVersion": "2.0",
    "baseVersion": "1.5"
  }
}
```

## 完成标准

feature_list.json 合并并通过用户确认后，阶段3 完成，进入阶段4。

## 输出清单

- ✅ `doc/06_dev-logs/feature_list.json`（已合并）
