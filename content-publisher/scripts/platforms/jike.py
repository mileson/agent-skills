#!/usr/bin/env python3
# ============================================================
# 文件说明书 (File Manual)
# ============================================================
# 核心功能 (Core Function)
# 即刻发布器，负责读取工作区内容、解析频道配置、调用 Node 适配器上传图片并发布动态。
#
# 输入 (Input)
# - workspace_path: 工作区路径（含 Output/jike/ 目录）
# - metadata.yaml: 含 article / medias / platform_specific.jike 配置
# - article.md: 即刻适配后的纯文字动态内容
# - secrets-vault: jike 命名空间下的 phone / password
#
# 输出 (Output)
# - PublishResult: 包含 publish_id / url / status / message
# - metadata.yaml 的 publish_records 新增即刻发布记录
#
# 定位 (Position)
# content-publisher 的即刻平台实现，复用 Node 适配器处理认证与发布。
#
# 依赖 (Dependency)
# - platforms/base.py: PlatformPublisher 基类
# - platforms/jike_toolkit.mjs: 即刻 API 适配器
# - Node.js 18+: 执行 jike_toolkit.mjs
# - secrets-vault: 获取 jike 命名空间凭证
#
# 维护规则 (Maintenance Rules)
# 1. 每次修改代码逻辑后，必须检查并更新上述信息。
# 2. 禁止修改或删除本【维护规则】章节的内容。
# ============================================================

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from .base import PlatformPublisher, PublishResult


class JikePublisher(PlatformPublisher):
    """Jike publisher using a Node.js adapter."""

    platform_id = "jike"
    platform_name = "即刻"

    def __init__(self, workspace_path: str):
        super().__init__(workspace_path)
        self.toolkit_path = Path(__file__).with_name("jike_toolkit.mjs")
        self._identity = None

    def _ensure_node(self):
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError("Node.js 不可用，无法执行即刻发布适配器")

    def _build_env(self) -> dict:
        creds = self.get_credentials("jike")
        phone = creds.get("phone") or ""
        password = creds.get("password") or ""
        if not phone or not password:
            raise RuntimeError(
                "jike 凭证不完整，需要在 secrets-vault 的 jike 命名空间配置 phone 和 password"
            )

        env = os.environ.copy()
        env["JIKE_PHONE"] = str(phone)
        env["JIKE_PASSWORD"] = str(password)
        return env

    def _run_toolkit(self, args: list[str]) -> dict:
        self._ensure_node()
        env = self._build_env()
        result = subprocess.run(
            ["node", str(self.toolkit_path), *args],
            capture_output=True,
            text=True,
            env=env,
            timeout=180,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        if stderr:
            raise RuntimeError(f"即刻适配器执行失败: {stderr}")
        if not stdout:
            raise RuntimeError("即刻适配器未返回结果")

        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"即刻适配器返回了非 JSON 内容: {stdout[:300]}") from exc

        if result.returncode != 0 or payload.get("status") == "error":
            raise RuntimeError(payload.get("message") or "即刻适配器执行失败")

        return payload

    @staticmethod
    def _strip_cover_comment_blocks(text: str) -> str:
        return re.sub(r"<!--\s*AI封面图.*?-->\s*", "", text, flags=re.DOTALL)

    @staticmethod
    def _strip_markdown_image_lines(text: str) -> str:
        return re.sub(r"^\s*!\[\[.*\]\([^)]+\)\s*$", "", text, flags=re.MULTILINE)

    @staticmethod
    def _strip_screenshot_guides(text: str) -> str:
        return re.sub(r"^\s*>\s*💡\s*\*\*截图指引\*\*：.*$\n?", "", text, flags=re.MULTILINE)

    @staticmethod
    def _strip_screenshot_placeholders(text: str) -> str:
        return re.sub(r"^\s*>?\s*\[待截图\].*$\n?", "", text, flags=re.MULTILINE)

    @staticmethod
    def _normalize_blank_lines(text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _prepare_content(self, metadata: dict) -> str:
        raw = self.load_article_markdown()
        content = self._strip_cover_comment_blocks(raw)
        content = self._strip_markdown_image_lines(content)
        content = self._strip_screenshot_guides(content)
        content = self._strip_screenshot_placeholders(content)
        content = self._normalize_blank_lines(content)

        title = metadata.get("article", {}).get("title", "").strip()
        leading_lines = []
        for line in content.splitlines():
            normalized = re.sub(r"^#+\s*", "", line).strip()
            if normalized:
                leading_lines.append(normalized)
            if len(leading_lines) >= 2:
                break

        if title and title not in leading_lines:
            content = f"{title}\n\n{content}" if content else title

        return content.strip()

    def _resolve_rel_path(self, rel_path: str | None) -> Path | None:
        if not rel_path:
            return None
        cleaned = rel_path[2:] if rel_path.startswith("./") else rel_path
        path = self.output_dir / cleaned
        if path.exists():
            return path
        return None

    def _collect_images(self, metadata: dict) -> list[Path]:
        jike_cfg = metadata.get("platform_specific", {}).get("jike", {})
        image_mode = jike_cfg.get("image_mode", "selected")
        max_images = int(jike_cfg.get("max_images", 9) or 9)
        explicit_paths = jike_cfg.get("image_paths") or []

        if image_mode == "none":
            return []

        images: list[Path] = []

        if explicit_paths:
            for rel in explicit_paths:
                resolved = self._resolve_rel_path(rel)
                if resolved:
                    images.append(resolved)
        else:
            cover = self.get_cover_path(metadata)
            if cover:
                images.append(cover)

            for item in metadata.get("medias", {}).get("inline_images", []) or []:
                resolved = self._resolve_rel_path(item.get("path"))
                if resolved:
                    images.append(resolved)

        deduped: list[Path] = []
        seen = set()
        for image in images:
            key = str(image.resolve())
            if key in seen:
                continue
            seen.add(key)
            deduped.append(image)

        return deduped[:max_images]

    def search_topics(self, query: str) -> list[dict]:
        payload = self._run_toolkit(["search-topic", query])
        return payload.get("topics", [])

    def _resolve_topic_id(self, metadata: dict) -> str:
        cfg = metadata.get("platform_specific", {}).get("jike", {})
        topic_id = cfg.get("topic_id", "").strip()
        topic_name = cfg.get("topic_name", "").strip()
        keyword = cfg.get("topic_search_keyword", "").strip()
        inferred_mode = "topic" if (topic_id or topic_name or keyword) else "personal"
        mode = metadata.get("publish_target", {}).get("mode") or cfg.get("mode") or inferred_mode
        if mode == "personal":
            return ""

        if topic_id:
            return topic_id

        keyword = keyword or topic_name
        if not keyword:
            raise RuntimeError("即刻发布目标为频道，但 metadata.yaml 缺少 topic_id 或 topic_search_keyword")

        topics = self.search_topics(keyword)
        if not topics:
            raise RuntimeError(f"未找到匹配的即刻频道: {keyword}")

        if topic_name:
            exact = [t for t in topics if t.get("name", "").strip() == topic_name]
            if len(exact) == 1:
                return exact[0]["id"]
            if len(exact) > 1:
                raise RuntimeError(f"匹配到多个同名即刻频道，请手动指定 topic_id: {topic_name}")

        if len(topics) == 1:
            return topics[0]["id"]

        candidates = " / ".join(f"{t.get('name')}({t.get('id')})" for t in topics[:5])
        raise RuntimeError(
            f"即刻频道搜索结果不唯一，请在 metadata.yaml 中明确 topic_id。候选: {candidates}"
        )

    def authenticate(self) -> bool:
        payload = self._run_toolkit(["whoami"])
        self._identity = payload.get("user", {})
        return True

    def upload_image(self, image_path: Path) -> str:
        payload = self._run_toolkit(["upload-image", str(image_path)])
        return payload.get("key", "")

    def create_draft(self, title: str, content: str, metadata: dict) -> PublishResult:
        return PublishResult(status="error", message="即刻不支持草稿模式，请直接执行 full_publish_flow")

    def publish(self, draft_id: str) -> PublishResult:
        return PublishResult(status="error", message="即刻不支持二段式 publish 接口")

    def get_status(self, publish_id: str) -> PublishResult:
        return PublishResult(status="error", message="即刻暂不支持发布后状态轮询")

    def full_publish_flow(self, auto_publish: bool = False) -> PublishResult:
        del auto_publish  # 即刻仅支持直接发布
        self.authenticate()

        metadata = self.load_metadata()
        content = self._prepare_content(metadata)
        images = self._collect_images(metadata)
        topic_id = self._resolve_topic_id(metadata)
        sync_cfg = metadata.get("publish_target", {}).get("sync_to_personal_update")
        if sync_cfg is None:
            sync_cfg = metadata.get("platform_specific", {}).get("jike", {}).get("sync_to_personal_update", True)

        payload = {
            "content": content,
            "images": [str(p.resolve()) for p in images],
            "topicId": topic_id,
            "syncToPersonalUpdate": bool(sync_cfg),
        }

        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as tmp:
            json.dump(payload, tmp, ensure_ascii=False, indent=2)
            tmp_path = tmp.name

        try:
            result = self._run_toolkit(["publish-json", tmp_path])
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

        post = result.get("post", {})
        publish_record = {
            "platform": self.platform_id,
            "post_id": post.get("id"),
            "url": post.get("url"),
            "topic_id": post.get("topicId", ""),
            "image_count": len(images),
            "sync_to_personal_update": bool(sync_cfg),
        }
        self.update_metadata(publish_record)

        channel_message = "已发布到个人动态"
        if topic_id:
            channel_message = f"已发布到即刻频道（topic_id={topic_id}）并同步个人动态"

        return PublishResult(
            status="success",
            message=channel_message,
            publish_id=post.get("id"),
            url=post.get("url"),
        )
