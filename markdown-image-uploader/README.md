# Markdown 图床自动上传工具

## 项目简介

一个专业的 Markdown 图片自动上传到图床的工具，支持阿里云 OSS 等多种图床服务。

## 主要特性

- ✅ 支持阿里云 OSS（首个支持的图床）
- ✅ 智能识别 `Medias/images/` 路径的图片
- ✅ 自动替换为 CDN URL
- ✅ 按文章名称自动归类
- ✅ 配置化管理
- ✅ 可独立使用或与其他 skill 集成

## 快速开始

### 1. 安装依赖

```bash
cd ~/.cursor/skills/markdown-image-uploader
pip install -r requirements.txt
```

### 2. 配置图床

```bash
# 复制配置模板
cp config/image_hosts.yaml config/my_hosts.yaml

# 编辑配置文件，填写阿里云 OSS 信息
vi config/my_hosts.yaml
```

### 3. 基础使用

```bash
# 上传并替换图片路径
python scripts/cli.py article.md -o article_with_cdn.md

# 指定文章名称（用于路径归类）
python scripts/cli.py article.md -o output.md --article-name "my-article"

# 测试单张图片上传
python scripts/cli.py --test-upload ./test.png

# 模拟运行（不实际上传）
python scripts/cli.py article.md --dry-run
```

## 与其他 Skill 集成

### 与 markdown-to-wechat 集成

```bash
cd ~/.cursor/skills/markdown-to-wechat
./convert.sh article.md --upload-images -o output.html
```

### 与 content-creator 配合

1. 使用 content-creator 生成文章（会自动生成符合规范的图片路径）
2. 使用 markdown-to-wechat 转换（会自动调用图床上传）

## 配置说明

### 阿里云 OSS 配置

```yaml
aliyun_oss:
  access_key_id: "你的 AccessKey ID"
  access_key_secret: "你的 AccessKey Secret"
  bucket: "你的 Bucket 名称"
  region: "oss-cn-hangzhou"
  endpoint: "oss-cn-hangzhou.aliyuncs.com"
  use_ssl: true
  cdn_domain: ""  # 可选
  base_path: "markdown-images"
  path_strategy: article_name  # 推荐
  filename_strategy: keep_original
```

### 路径组织策略

- **article_name**（推荐）：按文章名称归类
- **date_based**：按日期归类（2026/01/25/）
- **flat**：平铺到同一目录

## 开发状态

- [x] 阿里云 OSS 支持
- [ ] 七牛云支持（待实现）
- [ ] 腾讯云 COS 支持（待实现）
- [ ] GitHub 图床支持（待实现）
- [ ] 自定义上传支持（待实现）

## 许可证

MIT License

---

详细使用说明请查看 [SKILL.md](./SKILL.md)
