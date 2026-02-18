# 开源资产完善指南

Stage 5 的详细执行参考。

---

## 1. README.md

### 评估标准

已存在的 README 需满足以下条目（至少 7/9 通过）：

| # | 条目 | 说明 |
|---|------|------|
| 1 | 项目标题和简介 | 一句话说清项目做什么 |
| 2 | 特性列表 | 功能亮点，3-8 条 |
| 3 | 技术栈说明 | 主要依赖和框架 |
| 4 | 快速开始指南 | 安装 + 运行，可直接复制执行 |
| 5 | 项目结构说明 | 关键目录和文件的用途 |
| 6 | API 文档 | 后端项目或有公开 API 时必须 |
| 7 | 贡献指南 | 或指向 CONTRIBUTING.md |
| 8 | 许可证声明 | 底部标注许可证类型 |
| 9 | 徽章 | CI status、License、版本等 |

### 编写策略

1. 分析 `package.json` / `Cargo.toml` / `pyproject.toml` 等了解项目元信息
2. 阅读核心源码理解项目功能
3. **Web 搜索同类竞品**开源项目的 README，参考结构和表达
4. 从用户/开发者视角编写：**这是什么 → 为什么用 → 怎么用**
5. 确保所有示例代码和命令可直接执行

### 模板结构

```markdown
# Project Name

> 一句话介绍

[![License](badge_url)](license_url)
[![CI](badge_url)](ci_url)

## Features

- Feature 1
- Feature 2

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | ... |
| Backend | ... |

## Quick Start

### Prerequisites
### Installation
### Running

## Project Structure

## API Reference (if applicable)

## Contributing

## License
```

---

## 2. LICENSE

### 选择指南

| 许可证 | 特点 | 适合 |
|--------|------|------|
| **MIT** | 最宽松，仅要求保留版权声明 | 大多数项目（默认推荐） |
| **Apache 2.0** | 明确专利授权，要求声明变更 | 企业级项目 |
| **GPL 3.0** | 强 copyleft，衍生作品需同许可 | 希望保持开源的项目 |
| **BSD 3-Clause** | 类 MIT，额外禁止用名字做背书 | 学术项目 |

### 检查要点
- 年份是否为当前年份
- 作者信息是否正确
- 全文是否完整（部分许可证有附加条款）

---

## 3. .env.example

### 生成策略

```
1. 从代码中提取所有环境变量引用：
   grep -rh "process\.env\." src/ --include="*.ts" --include="*.tsx"
   grep -rh "os\.environ" . --include="*.py"

2. 生成 .env.example，每个变量附带注释：
   # Supabase 项目 URL
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   # Supabase 匿名公钥（公开安全）
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

3. 确认规则：
   - 所有值均为占位符（your_xxx / xxx_here）
   - 绝对不能包含真实值
   - 敏感变量标注 # ⚠️ 必须配置
```

### 已存在时的检查

对比代码实际引用的环境变量，确认 .env.example 无遗漏且无真实值。

---

## 4. .gitignore

### 通用必备条目

```gitignore
# 环境变量
.env
.env.local
.env.*.local

# 依赖
node_modules/
venv/
__pycache__/

# 构建产物
dist/
build/
.next/
.nuxt/

# IDE
.idea/
.vscode/settings.json
*.swp

# 系统文件
.DS_Store
Thumbs.db

# 日志
*.log
logs/

# 敏感文件
*.pem
*.key
*.p12
credentials.*
```

### 检查策略

根据项目实际技术栈补充特定条目（如 Docker volumes、Terraform state 等）。
