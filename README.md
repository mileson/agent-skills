<a id="agent-skills"></a>

<div align="center">

# Agent Skills · 按任务复用的技能集合

**找到对应任务的 Skill，连同规则、脚本和素材一起使用。**

任务分类 · Skill 入口 · 参考规则 · 配套脚本

[![中文说明](https://img.shields.io/badge/%E8%AF%B4%E6%98%8E-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-059669)](#readme-detail-features)
[![项目类型](https://img.shields.io/badge/%E9%A1%B9%E7%9B%AE-Skill-6366f1)](#readme-detail-features)

[✨ 核心特性](#readme-detail-features) · [✅ 适用场景](#readme-detail-audience) · [🚀 快速开始](#readme-detail-4) · [🧩 模块速查](#readme-detail-6)

</div>

---

面向 Claude Code、Cursor 和 Codex 的 Agent Skills 集合，按任务查找并复用完整的技能目录。

<a id="readme-detail-features"></a>

## ✨ 核心特性

- **按任务选择。** 不同任务对应独立 Skill 目录，先定位场景再读取规则。
- **整包复用。** 使用时保留 SKILL.md 与配套参考、脚本和资源。
- **各自核对条件。** 每个 Skill 的依赖、权限和交付要求以自身入口为准。

<a id="readme-detail-audience"></a>

## ✅ 适用场景

适合使用 Claude Code、Cursor 或 Codex 的读者。

<a id="readme-section-1"></a>

<a id="快速开始"></a>

<a id="readme-detail-4"></a>

## 🚀 快速开始

从目录导航中选择与当前任务对应的 Skill，读取该目录内的 `SKILL.md`。需要安装时保留整个 Skill 目录及其引用资源。

不同 Skill 的依赖与操作权限分别定义；调用前按对应入口核对运行条件。

<a id="readme-section-2"></a>

<a id="仓库导航"></a>

<a id="readme-detail-6"></a>

## 🧩 模块速查

按要处理的工作选择入口，先看模块职责，再进入对应文件或目录。

| 模块入口 | 负责什么 | 什么时候看 |
| --- | --- | --- |
| [`pdf/`](pdf/) | PDF 文档处理技能 | 按当前职责查阅实现及目录内说明 |
| [`frontend-design/`](frontend-design/) | 对应任务的技能目录 | 按当前职责查阅实现及目录内说明 |
| [`browser-automation/`](browser-automation/) | 对应任务的技能目录 | 按当前职责查阅实现及目录内说明 |
| [`ios-feature-creator/`](ios-feature-creator/) | 对应任务的技能目录 | 按当前职责查阅实现及目录内说明 |
| [`docx/`](docx/) | 对应任务的技能目录 | 按当前职责查阅实现及目录内说明 |
| [`pptx/`](pptx/) | 对应任务的技能目录 | 按当前职责查阅实现及目录内说明 |
| [`xlsx/`](xlsx/) | 对应任务的技能目录 | 按当前职责查阅实现及目录内说明 |
| [`skill-creator/`](skill-creator/) | 对应任务的技能目录 | 按当前职责查阅实现及目录内说明 |
