# 测试：工作区自动检测

## 测试场景 1：content-creator 工作区（唯一平台）

**目录结构**：
```
在 mac 任何文件夹都可以打开 claude code 的免费方法/
├── Materials/
├── Medias/
└── Output/
    └── wechat/
        ├── article.md  ← 目标文件
        └── images/     ← 10 张图片
```

**执行**：
```bash
cd "工作区目录"
@markdown-to-wechat
```

**预期 AI 行为**：
1. ✅ 执行 `detect_workspace.py --json`
2. ✅ 获取推荐：`{"action": "auto_select", "target": "Output/wechat/article.md"}`
3. ✅ 告知用户："检测到唯一文章，自动选择：Output/wechat/article.md"
4. ✅ 扫描文章，发现 10 张本地图片（`images/` 路径）
5. ✅ 调用 `/markdown-image-uploader` 上传图片
6. ✅ 使用上传后的 Markdown 转换为 HTML
7. ✅ 在浏览器中预览

**实际测试结果**：
```json
{
  "recommendation": {
    "action": "auto_select",
    "target": "Output/wechat/article.md",
    "platform": "wechat",
    "message": "自动选择唯一的文章：Output/wechat/article.md"
  }
}
```

✅ **脚本输出正确**

---

## 测试场景 2：多平台工作区

**目录结构**：
```
文章工作区/
└── Output/
    ├── wechat/
    │   └── article.md
    └── xhs/
        └── article.md
```

**预期 AI 行为**：
1. ✅ 执行 `detect_workspace.py --json`
2. ✅ 获取推荐：`{"action": "ask_user", "options": [...]}`
3. ✅ 展示选项：
   ```
   发现 2 个平台的文章：
   1. wechat - Output/wechat/article.md
   2. xhs - Output/xhs/article.md
   
   请选择要转换的平台：
   ```

---

## 测试场景 3：无 Output 目录

**目录结构**：
```
standalone_article/
├── article.md
└── draft.md
```

**预期 AI 行为**：
1. ✅ 执行 `detect_workspace.py --json`
2. ✅ 获取推荐：`{"action": "ask_user", "message": "当前目录有 2 个 Markdown 文件..."}`
3. ✅ 询问用户：
   ```
   当前目录有 2 个 Markdown 文件，请指定要转换的文件：
   - article.md
   - draft.md
   ```

---

## 优势总结

### ✅ 代码层面
- 所有检测逻辑封装在 `detect_workspace.py`
- SKILL.md 只需 3 步流程，简洁清晰
- 易于维护和扩展

### ✅ AI 体验
- AI 只需读取 JSON，无需理解复杂逻辑
- 决策表格清晰（`auto_select` / `ask_user` / `no_article`）
- 减少 token 消耗（精简 SKILL.md）

### ✅ 用户体验
- 单一命令，自动化程度高
- 智能检测，减少重复询问
- 清晰反馈，知道正在做什么
