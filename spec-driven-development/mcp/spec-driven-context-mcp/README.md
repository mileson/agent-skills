# spec-driven-context-mcp-server

将 `spec-driven-development` Skill 中已有的文档上下文脚本封装成一组可被 Agent 统一调用的 MCP tools。

## 提供的工具

- `spec_get_project_context`
- `spec_get_module_context`
- `spec_get_capability_context`
- `spec_get_problem_context`
- `spec_suggest_docs_for_task`
- `spec_suggest_doc_updates`
- `spec_generate_revision_history_draft`
- `spec_generate_context_report`

## 设计原则

- 不重复实现文档解析逻辑，直接复用 Skill 内已有 Python 脚本
- MCP 层只负责输入校验、调用脚本、返回结构化数据
- 默认使用 `stdio`，便于本地 Agent 直接接入

## 构建

```bash
npm install
npm run build
```

## 运行

```bash
npm start
```

## 环境变量

- `SPEC_DRIVEN_SKILL_ROOT`：可选，默认为当前包上三级目录的 Skill 根目录

## 与 Skill 脚本的对应关系

- `read_existing_docs.py`
- `generate_context_report.py`
- `query_doc_context.py`
- `suggest_doc_updates.py`
- `generate_revision_history_draft.py`
