#!/usr/bin/env python3
# ============================================================
# 文件说明书 (File Manual)
# ============================================================
# 核心功能 (Core Function)
# 定义所有平台发布器的抽象基类，统一接口规范。
#
# 输入 (Input)
# - workspace_path: 工作区路径（含 Output/{platform}/ 目录）
# - 凭证: 通过 secrets-vault 的 get_secret.py 获取
#
# 输出 (Output)
# - 统一的发布结果 dict: {status, draft_id, publish_id, url, message}
#
# 定位 (Position)
# content-publisher skill 的平台抽象层，所有具体平台实现继承此基类。
#
# 依赖 (Dependency)
# - secrets-vault skill 的 get_secret.py 脚本
# - Python 3.6+ 标准库: abc, subprocess, json, os
#
# 维护规则 (Maintenance Rules)
# 1. 每次修改代码逻辑后，必须检查并更新上述信息。
# 2. 禁止修改或删除本【维护规则】章节的内容。
# ============================================================

import json
import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

SECRETS_SCRIPT = os.path.expanduser(
    "~/.cursor/skills/secrets-vault/scripts/get_secret.py"
)


class PublishResult:
    """Standardized publish result."""

    def __init__(self, status, message="", draft_id=None, publish_id=None, url=None):
        self.status = status  # "success", "draft_created", "error"
        self.message = message
        self.draft_id = draft_id
        self.publish_id = publish_id
        self.url = url

    def to_dict(self):
        return {
            k: v for k, v in {
                "status": self.status,
                "message": self.message,
                "draft_id": self.draft_id,
                "publish_id": self.publish_id,
                "url": self.url,
            }.items() if v is not None
        }

    def __str__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class PlatformPublisher(ABC):
    """Abstract base class for all platform publishers."""

    platform_id: str = ""
    platform_name: str = ""

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.output_dir = self.workspace_path / "Output" / self.platform_id
        self._credentials = None

    def get_credentials(self, namespace: str = None) -> dict:
        """Retrieve credentials from secrets-vault."""
        ns = namespace or self.platform_id
        try:
            result = subprocess.run(
                ["python3", SECRETS_SCRIPT, ns],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"secrets-vault error: {result.stderr.strip()}"
                )
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            raise RuntimeError(
                f"Invalid JSON from secrets-vault for namespace '{ns}'"
            )
        except FileNotFoundError:
            raise RuntimeError(
                "secrets-vault not found. Install secrets-vault skill first."
            )

    def load_metadata(self) -> dict:
        """Load platform metadata.yaml."""
        meta_path = self.output_dir / "metadata.yaml"
        if not meta_path.exists():
            raise FileNotFoundError(
                f"metadata.yaml not found at {meta_path}"
            )
        import yaml
        with open(meta_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_article_html(self) -> str:
        """Load the HTML article file."""
        html_path = self.output_dir / "article.html"
        if not html_path.exists():
            # Fallback to markdown
            md_path = self.output_dir / "article.md"
            if md_path.exists():
                raise FileNotFoundError(
                    f"article.html not found (article.md exists — "
                    f"convert to HTML first using markdown-to-wechat skill)"
                )
            raise FileNotFoundError(
                f"No article file found in {self.output_dir}"
            )
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()

    # Supported image extensions (shared by all image-related methods)
    IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

    def list_images(self) -> list:
        """List image files in the platform output directory."""
        img_dir = self.output_dir / "images"
        if not img_dir.exists():
            return []
        return sorted(
            p for p in img_dir.iterdir()
            if p.suffix.lower() in self.IMAGE_EXTS
        )

    def get_cover_path(self, metadata: dict) -> Path | None:
        """Resolve cover image path from metadata.yaml.

        The caller (content-creator Stage 6) is responsible for specifying
        the cover path in metadata.yaml under:
            medias:
              cover:
                path: "./images/cover.jpg"   # relative to Output/{platform}/

        Supported formats: .jpg, .jpeg, .png, .gif, .webp, .bmp
        """
        cover_info = metadata.get("medias", {}).get("cover", {})
        rel_path = cover_info.get("path")
        if not rel_path:
            return None
        cover = self.output_dir / rel_path
        if cover.exists() and cover.suffix.lower() in self.IMAGE_EXTS:
            return cover
        return None

    def update_metadata(self, publish_record: dict):
        """Append publish record to metadata.yaml."""
        import yaml
        meta_path = self.output_dir / "metadata.yaml"
        meta = self.load_metadata()
        if "publish_records" not in meta:
            meta["publish_records"] = []
        meta["publish_records"].append(publish_record)
        with open(meta_path, "w", encoding="utf-8") as f:
            yaml.dump(meta, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform. Return True if successful."""
        pass

    @abstractmethod
    def upload_image(self, image_path: Path) -> str:
        """Upload an image and return the platform URL."""
        pass

    @abstractmethod
    def create_draft(self, title: str, content: str, metadata: dict) -> PublishResult:
        """Create a draft article. Return PublishResult with draft_id."""
        pass

    @abstractmethod
    def publish(self, draft_id: str) -> PublishResult:
        """Publish a draft. Return PublishResult with publish_id/url."""
        pass

    @abstractmethod
    def get_status(self, publish_id: str) -> PublishResult:
        """Check publish status. Return PublishResult."""
        pass

    def full_publish_flow(self, auto_publish: bool = False) -> PublishResult:
        """Default publish flow. Subclasses can override for custom logic."""
        self.authenticate()
        meta = self.load_metadata()
        article_meta = meta.get("article", {})
        title = article_meta.get("title", "Untitled")
        html = self.load_article_html()
        return self.create_draft(title, html, meta)
