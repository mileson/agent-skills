# Markdown 转微信公众号格式转换器

一个专业的 Cursor Skill，用于将 Markdown 文档快速转换为微信公众号格式，提供优雅的淡蓝色主题和完善的排版优化。

## 快速开始

### 方法一：使用便捷脚本（推荐）

```bash
cd ~/.cursor/skills/markdown-to-wechat

# 使用深蓝色主题（专业风格）⭐ 推荐
./convert.sh your_article.md --theme deep-blue -o output.html

# 或使用淡蓝色主题（清新风格）
./convert.sh your_article.md --theme light-blue -o output.html
```

### 方法二：手动管理环境

```bash
cd ~/.cursor/skills/markdown-to-wechat

# 1. 首次使用：创建环境并安装依赖
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# 2. 日常使用：直接转换（复用已安装环境）
./venv/bin/python scripts/cli.py your_article.md -o output.html
```

## 主要功能

- ✅ 完整 Markdown 支持
- ✅ 多主题支持（淡蓝色 + 深蓝色）⭐
- ✅ **淡橙色强调效果** ⭐ 新增
  - `**加粗**` → 淡橙色背景高亮
  - `~~删除线~~` → 橙色虚线下划线
- ✅ 代码语法高亮
- ✅ 链接自动转脚注
- ✅ 排版自动优化
- ✅ 一键复制粘贴

## 🎨 主题选择

- **淡蓝色主题** (`light-blue`): 清新风格，适合技术文章、教程
- **深蓝色主题** (`deep-blue`): 专业风格，适合商务内容、报告 ⭐ 推荐

查看[主题指南](./THEMES.md)了解更多

## 详细文档

查看 [SKILL.md](./SKILL.md) 了解完整使用说明。

## 示例

```bash
# 查看示例效果
python scripts/cli.py examples/sample.md -p
```

## License

MIT
