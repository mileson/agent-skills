# 开源发布检查清单

在每个阶段完成时勾选对应项，确保无遗漏。

---

## Stage 1: Git 环境 ✓

- [ ] 确认是 Git 仓库（或已完成初始化）
- [ ] Git 身份配置正确（user.name / user.email）
- [ ] `.gitignore` 存在且基本完善

---

## Stage 2: 远程仓库 ✓

- [ ] 远程仓库已配置（git remote -v 有输出）
- [ ] 仓库可见性已确认（公开 / 私有）
- [ ] 如果是新仓库，已在 GitHub 创建

---

## Stage 3: 当前文件敏感扫描 ✓

- [ ] API 密钥 / Secret：无硬编码
- [ ] 数据库连接字符串：无明文密码
- [ ] Token / JWT：无硬编码令牌
- [ ] 密码：无明文密码或默认密码
- [ ] 内网地址：无私有 IP 或内部域名
- [ ] 云服务 ID：无项目 ID 泄露（或确认可公开）
- [ ] 私钥 / 证书：无 PEM 文件内容
- [ ] Webhook URL：无含密钥的回调地址
- [ ] 个人信息：无私人联系方式
- [ ] 技术栈特定项：已按实际技术栈补充检查
- [ ] 边界场景：注释、测试报告、嵌套配置等已走查
- [ ] 扫描报告已呈现给用户并确认处理方案

---

## Stage 4: Git 历史敏感扫描 ✓

- [ ] 基于 Stage 3 发现的敏感字符串已在历史中搜索
- [ ] 已删除的敏感文件在历史中不可恢复（或已清理）
- [ ] Commit Message 中无敏感信息
- [ ] 如有历史清理：
  - [ ] 已创建备份分支
  - [ ] git filter-repo 执行成功
  - [ ] remote origin 已重新添加
  - [ ] 用户已确认 force push

---

## Stage 5: 开源资产 ✓

### README.md
- [ ] 存在且内容完整
- [ ] 包含项目简介（一句话说清做什么）
- [ ] 包含功能特性列表
- [ ] 包含技术栈说明
- [ ] 包含快速开始指南（安装 + 运行）
- [ ] 包含项目结构说明
- [ ] 包含贡献指南
- [ ] 包含许可证声明
- [ ] 已参考竞品 README 优化
- [ ] 无敏感信息（URL、密钥等已脱敏）

### LICENSE
- [ ] 存在且内容完整
- [ ] 许可证类型已确认（MIT / Apache 2.0 / GPL 等）
- [ ] 年份和作者信息正确

### .env.example
- [ ] 存在
- [ ] 包含所有代码中引用的环境变量
- [ ] 所有值均为占位符（无真实值）
- [ ] 包含注释说明每个变量的用途

### .gitignore
- [ ] 排除 .env / .env.local / .env.*.local
- [ ] 排除依赖目录（node_modules / venv 等）
- [ ] 排除构建产物（dist / build / .next 等）
- [ ] 排除 IDE 配置
- [ ] 排除操作系统文件（.DS_Store 等）
- [ ] 排除敏感文件（*.pem, *.key 等）
- [ ] 排除项目特定的敏感目录

---

## Stage 6: Commit & Push ✓

- [ ] 所有变更已 stage（git add）
- [ ] Commit 信息符合功能导向规范
- [ ] Commit 信息标题 ≤ 50 字符
- [ ] Push 成功

---

## Stage 7: 发布 & 验证 ✓

- [ ] 仓库可见性已设置为公开（如需）
- [ ] 仓库描述（description）已设置
- [ ] 仓库主页（homepage）已设置
- [ ] Topics 标签已设置
- [ ] 最终验证：
  - [ ] README.md 正常渲染
  - [ ] LICENSE 可访问
  - [ ] 无敏感信息泄露
  - [ ] 所有链接有效

---

## 快速检查命令

```bash
# 检查是否有敏感文件被追踪
git ls-files | grep -iE '\.env$|\.env\.local|\.pem$|\.key$|credential|secret'

# 检查 .gitignore 是否排除了常见敏感文件
cat .gitignore | grep -iE 'env|pem|key|secret|credential'

# 检查环境变量引用是否都在 .env.example 中有对应
grep -rh "process\.env\." src/ --include="*.ts" --include="*.tsx" | \
  sed 's/.*process\.env\.\([A-Z_]*\).*/\1/' | sort -u

# 检查历史中的敏感文件
git log --all --diff-filter=D --summary -- "*.env" "*.pem" "*.key"

# 检查 README 是否存在
test -f README.md && echo "✅ README exists" || echo "❌ README missing"

# 检查 LICENSE 是否存在
test -f LICENSE && echo "✅ LICENSE exists" || echo "❌ LICENSE missing"
```
