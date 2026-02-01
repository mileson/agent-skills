# AI 执行标准流程（最终版）

## 🎯 核心原则

1. ⭐ **先上传图床，再转换 HTML**（顺序不能错）
2. ⭐ **解析 JSON 输出，获取路径映射**
3. ⭐ **使用上传后的文件进行转换**

---

## 📝 完整执行日志示例

### 场景：用户在工作区运行 `@markdown-to-wechat`

```
❯ @markdown-to-wechat

【步骤1：工作区检测】
⏺ Bash(python ~/.cursor/skills/markdown-to-wechat/scripts/detect_workspace.py --json)
  ⎿ {
      "recommendation": {
        "action": "auto_select",
        "target": "Output/wechat/article.md",
        "platform": "wechat"
      },
      "platforms": [{
        "name": "wechat",
        "article_exists": true,
        "images_exists": true,
        "image_count": 10
      }]
    }

⏺ 📍 自动选择文章：Output/wechat/article.md
  （检测到 Output/wechat/images/ 目录有 10 张图片）

【步骤2：图片检测】
⏺ Read(Output/wechat/article.md)
  ⎿ # 保姆级教程：一键在Mac任意文件夹启动Claude Code
    
    ![图片：01 预览效果](images/01-preview.png)
    *▲ 配置完成后的效果展示*
    
    ![图片：02 查询automator](images/02-automator.png)
    *▲ 在 Spotlight 中搜索 Automator*
    
    ... 共 10 张图片

⏺ 🔍 检测到 10 张本地图片（images/ 路径），需要上传到阿里云 OSS

【步骤2：执行图片上传】⭐ 关键步骤
⏺ Bash(cd ~/.cursor/skills/markdown-image-uploader && \
      ./venv/bin/python scripts/cli.py \
      "/Users/mileson/Workspace/.../Output/wechat/article.md" \
      -o "/Users/mileson/Workspace/.../Output/wechat/article_cdn.md" \
      --article-name "yi-jian-zai-mac-ren-yi-wen-jian-jia-qi-dong-claude-code")
      
  ⎿ 📄 Processing: .../Output/wechat/article.md
    📦 Output: .../Output/wechat/article_cdn.md
    
    🔍 Found 10 images to process
    📤 Uploading: 01-preview.png → yi-jian-zai-mac.../01-preview.png
    ✅ Success: https://mileson-documents.oss-cn-hangzhou.aliyuncs.com/markdown-images/yi-jian-zai-mac.../01-preview.png
    
    📤 Uploading: 02-automator.png → yi-jian-zai-mac.../02-automator.png
    ✅ Success: https://mileson-documents.oss-cn-hangzhou.aliyuncs.com/markdown-images/yi-jian-zai-mac.../02-automator.png
    
    ... (省略 8 张)
    
    💾 Saved to: .../Output/wechat/article_cdn.md
    
    📊 Summary:
      Total: 10
      Uploaded: 10
      Skipped: 0
      Failed: 0
    
    ==================================================
    📋 JSON Output (for AI):
    {
      "status": "success",
      "total_images": 10,
      "uploaded": 10,
      "skipped": 0,
      "failed": 0,
      "output_file": "/Users/mileson/Workspace/.../Output/wechat/article_cdn.md",
      "mappings": [
        {
          "local": "images/01-preview.png",
          "cdn": "https://mileson-documents.oss-cn-hangzhou.aliyuncs.com/markdown-images/yi-jian-zai-mac.../01-preview.png",
          "status": "uploaded"
        },
        ...
      ]
    }
    ==================================================
    
    ✅ Processing completed!

⏺ ✅ 图片上传完成：10/10 成功
  所有图片已自动替换为 CDN URL

【步骤3：转换 HTML】⭐ 使用上传后的文件
⏺ Bash(~/.cursor/skills/markdown-to-wechat/convert.sh \
      "/Users/mileson/Workspace/.../Output/wechat/article_cdn.md" \
      --theme deep-blue \
      -o "/Users/mileson/Workspace/.../Output/wechat/article.html" \
      -p)
      
  ⎿ 📄 读取文件: .../article_cdn.md
    🎨 应用主题: deep-blue
    ⚙️  正在转换...
    💾 保存到: .../article.html
    🌐 在浏览器中预览
    ✅ 转换完成！

【完成反馈】
⏺ ✅ 全部完成！

  📊 处理结果：
  ┌─────────────┬─────────────────────────────────┐
  │    项目     │              结果               │
  ├─────────────┼─────────────────────────────────┤
  │ 工作区检测  │ ✅ 自动选择 Output/wechat       │
  ├─────────────┼─────────────────────────────────┤
  │ 图片上传    │ ✅ 10/10 成功上传到阿里云 OSS   │
  ├─────────────┼─────────────────────────────────┤
  │ 路径替换    │ ✅ 已替换为 CDN URL             │
  ├─────────────┼─────────────────────────────────┤
  │ HTML 生成   │ ✅ article.html                 │
  ├─────────────┼─────────────────────────────────┤
  │ 图片可用性  │ ✅ 可正常加载（CDN）            │
  ├─────────────┼─────────────────────────────────┤
  │ 可发布性    │ ✅ 可直接复制到微信公众号       │
  └─────────────┴─────────────────────────────────┘

  💡 下一步操作：
  1. ✅ 浏览器已自动打开预览
  2. 检查图片是否正常显示（应该是 CDN URL）
  3. Cmd+A 全选 → Cmd+C 复制
  4. 粘贴到微信公众号编辑器
  5. 预览并发布

  🔗 CDN URL 示例：
  https://mileson-documents.oss-cn-hangzhou.aliyuncs.com/markdown-images/yi-jian-zai-mac.../01-preview.png
```

---

## 🎯 AI 必须执行的关键检查

### 检查点 1：JSON 解析

```python
# AI 必须从输出中提取 JSON（在 === 之间）
json_str = extract_between_markers(output, "==================================================")
result = json.loads(json_str)

# 检查状态
if result["status"] == "success":
    markdown_file = result["output_file"]  # 使用这个文件！
    uploaded_count = result["uploaded"]
    print(f"✅ 图片上传完成：{uploaded_count}/{result['total_images']} 成功")
else:
    # 处理失败情况
    ...
```

### 检查点 2：文件路径验证

```python
# 使用上传后的文件
markdown_file = result["output_file"]

# 验证文件存在
if not Path(markdown_file).exists():
    print(f"❌ 错误：上传后的文件不存在：{markdown_file}")
    exit(1)

# 继续转换
convert_to_html(markdown_file)
```

### 检查点 3：HTML 验证

```python
# 转换完成后，验证 HTML 中的图片 URL
with open("article.html", "r") as f:
    html = f.read()

# 检查是否包含 CDN URL
if "oss-cn-hangzhou.aliyuncs.com" in html:
    print("✅ HTML 中的图片已是 CDN URL")
else:
    print("⚠️ 警告：HTML 中可能仍有本地路径")
```

---

## ✅ 最终验证清单

执行完成后，AI 必须确认：
- [ ] 图片已上传到阿里云 OSS
- [ ] Markdown 中的路径已替换为 CDN URL
- [ ] HTML 中的 `<img src>` 是 CDN URL
- [ ] 浏览器预览中图片正常显示
- [ ] 告知用户可以直接复制到微信公众号
