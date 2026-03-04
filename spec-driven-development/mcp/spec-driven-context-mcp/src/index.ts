#!/usr/bin/env node

import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const execFileAsync = promisify(execFile);
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const skillRoot =
  process.env.SPEC_DRIVEN_SKILL_ROOT ??
  resolve(__dirname, "..", "..", "..");
const scriptsRoot = resolve(skillRoot, "scripts");

type StructuredPayload = Record<string, unknown>;

function buildScriptPath(scriptName: string): string {
  return resolve(scriptsRoot, scriptName);
}

async function runPythonJsonScript(scriptName: string, args: string[]): Promise<StructuredPayload> {
  const commandArgs = [buildScriptPath(scriptName), ...args];
  try {
    const { stdout } = await execFileAsync("python3", commandArgs, {
      env: process.env,
      maxBuffer: 10 * 1024 * 1024,
    });
    const trimmed = stdout.trim();
    if (!trimmed) {
      throw new Error(`${scriptName} 未返回 JSON 内容`);
    }
    const parsed = JSON.parse(trimmed) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      throw new Error(`${scriptName} 返回的不是 JSON 对象`);
    }
    return parsed as StructuredPayload;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`执行 ${scriptName} 失败: ${message}`);
  }
}

async function runPythonTextScript(scriptName: string, args: string[]): Promise<string> {
  const commandArgs = [buildScriptPath(scriptName), ...args];
  try {
    const { stdout } = await execFileAsync("python3", commandArgs, {
      env: process.env,
      maxBuffer: 10 * 1024 * 1024,
    });
    const trimmed = stdout.trim();
    if (!trimmed) {
      throw new Error(`${scriptName} 未返回文本内容`);
    }
    return trimmed;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`执行 ${scriptName} 失败: ${message}`);
  }
}

function jsonContent(payload: StructuredPayload) {
  return [{ type: "text" as const, text: JSON.stringify(payload, null, 2) }];
}

const server = new McpServer({
  name: "spec-driven-context-mcp-server",
  version: "1.0.0",
});

const docPathSchema = z.object({
  doc_path: z.string().min(1).describe("Documentation 目录路径"),
});

server.registerTool(
  "spec_get_project_context",
  {
    title: "Get Project Context",
    description:
      "读取 Documentation 目录并返回项目级结构化上下文摘要，包括 Framework 能力、问题方案和模块索引。",
    inputSchema: docPathSchema.shape,
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
  async ({ doc_path }) => {
    const result = await runPythonJsonScript("query_doc_context.py", [
      "--doc-path",
      doc_path,
      "--query-type",
      "project",
    ]);
    return { content: jsonContent(result), structuredContent: result };
  }
);

server.registerTool(
  "spec_get_module_context",
  {
    title: "Get Module Context",
    description: "按模块名或关键字查询模块主文档的结构化上下文。",
    inputSchema: {
      ...docPathSchema.shape,
      name: z.string().min(1).describe("模块名或关键字"),
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
  async ({ doc_path, name }) => {
    const result = await runPythonJsonScript("query_doc_context.py", [
      "--doc-path",
      doc_path,
      "--query-type",
      "module",
      "--name",
      name,
    ]);
    return { content: jsonContent(result), structuredContent: result };
  }
);

server.registerTool(
  "spec_get_capability_context",
  {
    title: "Get Capability Context",
    description: "按能力名或关键字查询 CommonCapabilities 文档的结构化上下文。",
    inputSchema: {
      ...docPathSchema.shape,
      name: z.string().min(1).describe("能力名或关键字"),
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
  async ({ doc_path, name }) => {
    const result = await runPythonJsonScript("query_doc_context.py", [
      "--doc-path",
      doc_path,
      "--query-type",
      "capability",
      "--name",
      name,
    ]);
    return { content: jsonContent(result), structuredContent: result };
  }
);

server.registerTool(
  "spec_get_problem_context",
  {
    title: "Get Problem Solution Context",
    description: "按问题名或关键字查询 ProblemSolutions 文档的结构化上下文。",
    inputSchema: {
      ...docPathSchema.shape,
      name: z.string().min(1).describe("问题方案名或关键字"),
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
  async ({ doc_path, name }) => {
    const result = await runPythonJsonScript("query_doc_context.py", [
      "--doc-path",
      doc_path,
      "--query-type",
      "problem",
      "--name",
      name,
    ]);
    return { content: jsonContent(result), structuredContent: result };
  }
);

server.registerTool(
  "spec_suggest_docs_for_task",
  {
    title: "Suggest Docs For Task",
    description:
      "根据任务描述推荐 Agent 在编码前应读取和绑定的文档，并返回任务分类、风险等级、是否需要先读问题方案，以及推荐阅读顺序。",
    inputSchema: {
      ...docPathSchema.shape,
      task_text: z.string().min(1).describe("任务描述"),
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
  async ({ doc_path, task_text }) => {
    const result = await runPythonJsonScript("query_doc_context.py", [
      "--doc-path",
      doc_path,
      "--query-type",
      "suggest-docs",
      "--task-text",
      task_text,
    ]);
    return { content: jsonContent(result), structuredContent: result };
  }
);

server.registerTool(
  "spec_suggest_doc_updates",
  {
    title: "Suggest Doc Updates",
    description:
      "根据代码变更文件列表和任务描述，建议本次实现后应回写哪些 Spec 文档。",
    inputSchema: {
      ...docPathSchema.shape,
      changed_files: z.array(z.string().min(1)).min(1).describe("本次变更的代码文件路径列表"),
      task_text: z.string().optional().describe("可选的任务描述，用于增强推荐准确度"),
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
  async ({ doc_path, changed_files, task_text }) => {
    const args = ["--doc-path", doc_path];
    for (const changedFile of changed_files) {
      args.push("--changed-file", changedFile);
    }
    if (task_text) {
      args.push("--task-text", task_text);
    }
    const result = await runPythonJsonScript("suggest_doc_updates.py", args);
    return { content: jsonContent(result), structuredContent: result };
  }
);

server.registerTool(
  "spec_generate_revision_history_draft",
  {
    title: "Generate Revision History Draft",
    description:
      "根据代码变更文件列表、任务描述和可选版本号，生成修订历史表格行与代码同步说明草案。",
    inputSchema: {
      ...docPathSchema.shape,
      changed_files: z.array(z.string().min(1)).min(1).describe("本次变更的代码文件路径列表"),
      task_text: z.string().optional().describe("可选的任务描述，用于增强修订内容"),
      version: z.string().optional().describe("可选的修订版本号"),
      author: z.string().optional().describe("可选的修订人"),
      draft_date: z.string().optional().describe("可选的修订日期，格式 YYYY-MM-DD"),
      git_repo: z.string().optional().describe("可选的 Git 仓库路径，用于抓取真实 diff"),
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
  async ({ doc_path, changed_files, task_text, version, author, draft_date, git_repo }) => {
    const args = ["--doc-path", doc_path];
    for (const changedFile of changed_files) {
      args.push("--changed-file", changedFile);
    }
    if (task_text) {
      args.push("--task-text", task_text);
    }
    if (version) {
      args.push("--version", version);
    }
    if (author) {
      args.push("--author", author);
    }
    if (draft_date) {
      args.push("--date", draft_date);
    }
    if (git_repo) {
      args.push("--git-repo", git_repo);
    }
    const result = await runPythonJsonScript("generate_revision_history_draft.py", args);
    return { content: jsonContent(result), structuredContent: result };
  }
);

server.registerTool(
  "spec_generate_context_report",
  {
    title: "Generate Context Report",
    description:
      "生成面向人类和 Agent 的当前系统上下文报告 Markdown，可用于 Brownfield 阶段审查。",
    inputSchema: {
      ...docPathSchema.shape,
      project_name: z.string().optional().describe("可选的项目名称"),
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  },
  async ({ doc_path, project_name }) => {
    const args = ["--doc-path", doc_path];
    if (project_name) {
      args.push("--project-name", project_name);
    }
    const markdown = await runPythonTextScript("generate_context_report.py", args);
    const payload = { markdown };
    return { content: jsonContent(payload), structuredContent: payload };
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
