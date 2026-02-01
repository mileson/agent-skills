---
name: ai-news-daily
description: 每日 AI 新闻汇总技能。当用户询问"今天的热门 AI 新闻有哪些"、"最新 AI 资讯"、"AI 行业动态"、"今天 AI 圈发生了什么"等问题时触发。从 Reddit (r/MachineLearning, r/Artificial, r/singularity)、x.com (@OpenAI, @AnthropicAI, @GoogleDeepMind 官方账号)、知乎 (人工智能话题)、小红书 (AI话题、AI工具、ChatGPT技巧) 等多平台搜索最新 AI 资讯，按 5 大分类整理成 Markdown 报告。
---

# AI 每日新闻汇总

从多个平台搜索最新的 AI 资讯，智能分类整理后生成每日报告。

## 数据源

| 平台 | 搜索内容 |
|------|----------|
| Reddit | r/MachineLearning, r/Artificial, r/singularity |
| x.com | @OpenAI, @AnthropicAI, @GoogleDeepMind |
| 知乎 | 人工智能话题下的热门内容 |
| 小红书 | AI话题、AI工具、ChatGPT技巧、Midjourney教程 |

## 分类标准

1. **🤖 大模型发布/更新** - GPT/Claude/Gemini/Llama 等模型版本更新
2. **📄 研究论文/突破** - arXiv 论文、技术突破、算法创新
3. **🚀 产品发布/功能更新** - 新功能、API 更新、产品上线
4. **💰 行业动态/融资新闻** - 融资、收购、政策、合作动态
5. **🛠️ 开源项目/工具** - GitHub 开源项目、开发工具、框架

详细的分类判断标准参见 `references/categories.md`

## 工作流程

### 1. 多平台搜索

使用 WebSearch 工具并行搜索各平台：

```
WebSearch: "site:reddit.com AI artificial intelligence 2025"
WebSearch: "site:x.com OpenAI AnthropicAI DeepMind"
WebSearch: "site:zhihu.com 人工智能"
WebSearch: "site:xiaohongshu.com AI工具 ChatGPT"
```

### 2. 内容收集与去重

- 提取每条新闻的标题、来源、链接
- 基于标题相似度去除重复新闻
- 过滤掉非 AI 相关或低质量内容

### 3. 智能分类

根据 `references/categories.md` 中的分类标准，将新闻归类。

分类优先级：大模型 > 研究论文 > 产品功能 > 行业动态 > 开源工具

### 4. 生成报告

按以下格式输出 Markdown 报告：

```markdown
# AI 每日资讯 - 2025年1月30日

## 🤖 大模型发布/更新

- [标题](链接) - 来源
  简短摘要...

## 📄 研究论文/突破

...

---
*数据来源: Reddit, x.com, 知乎, 小红书*
```

## 注意事项

1. **时效性**: 优先展示今天和最近 24 小时的新闻
2. **去重**: 同一新闻在不同平台只保留一次
3. **摘要**: 每条新闻生成 1-2 句话的简短摘要
4. **来源标注**: 每条新闻标注具体来源平台
5. **数量控制**: 每个分类最多展示 5-10 条新闻
