#!/usr/bin/env python3
# ============================================================
# 文件说明书 (File Manual)
# ============================================================
# 核心功能 (Core Function)
# 微信公众号发布器，通过官方 API 实现图片上传、草稿创建、文章发布。
#
# 输入 (Input)
# - workspace_path: 工作区路径（含 Output/wechat/ 目录）
# - 凭证: 通过 secrets-vault 获取 wechat_mp 命名空间
# - article.html: 微信公众号格式的 HTML 文章
# - metadata.yaml: 含 title, digest, author 等元数据
#
# 输出 (Output)
# - PublishResult: 包含 draft_id / publish_id / url / status
# - 更新 metadata.yaml 添加 publish_records
#
# 定位 (Position)
# content-publisher 的微信公众号平台实现（Phase 1）。
#
# 依赖 (Dependency)
# - wechatpy: 微信公众号 Python SDK（用于认证和素材上传）
# - requests: HTTP 请求（用于 draft/freepublish API，wechatpy 暂未封装）
# - base.py: PlatformPublisher 基类
# - secrets-vault: 获取 wechat_mp 凭证
#
# 维护规则 (Maintenance Rules)
# 1. 每次修改代码逻辑后，必须检查并更新上述信息。
# 2. 禁止修改或删除本【维护规则】章节的内容。
# ============================================================

import json
import re
import time
from pathlib import Path

import requests

from .base import PlatformPublisher, PublishResult

API_BASE = "https://api.weixin.qq.com/cgi-bin"


class WeChatPublisher(PlatformPublisher):
    """WeChat Official Account publisher using official API.

    Uses wechatpy SDK for authentication and media upload.
    Uses direct HTTP requests for draft/freepublish APIs
    (not yet available in wechatpy 1.8.x).
    """

    platform_id = "wechat"
    platform_name = "微信公众号"

    def __init__(self, workspace_path: str):
        super().__init__(workspace_path)
        self._client = None
        self._access_token = None

    def _ensure_deps(self):
        """Check required dependencies."""
        try:
            from wechatpy import WeChatClient  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "wechatpy not installed. Run: pip install wechatpy cryptography"
            )

    def authenticate(self) -> bool:
        """Authenticate with WeChat API using app_id and app_secret."""
        self._ensure_deps()
        from wechatpy import WeChatClient

        creds = self.get_credentials("wechat_mp")
        app_id = creds.get("app_id")
        app_secret = creds.get("app_secret")

        if not app_id or not app_secret:
            raise RuntimeError(
                "wechat_mp credentials incomplete. "
                "Need app_id and app_secret in secrets-vault."
            )

        self._client = WeChatClient(app_id, app_secret)

        try:
            token = self._client.fetch_access_token()
            self._access_token = token.get("access_token")
            return True
        except Exception as e:
            raise RuntimeError(f"WeChat authentication failed: {e}")

    def _api_post(self, path: str, data: dict) -> dict:
        """Make a POST request to WeChat API with access_token.

        CRITICAL: Must use ensure_ascii=False to preserve Chinese characters.
        Using requests.post(json=...) would escape CJK to \\uXXXX, causing
        garbled text in WeChat drafts.
        """
        url = f"{API_BASE}/{path}?access_token={self._access_token}"
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        resp = requests.post(
            url,
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("errcode", 0) != 0:
            raise RuntimeError(
                f"WeChat API error: [{result.get('errcode')}] {result.get('errmsg')}"
            )
        return result

    @staticmethod
    def _truncate_utf8(text: str, max_bytes: int) -> str:
        """Truncate text to fit within max_bytes in UTF-8 encoding."""
        if not text:
            return text
        encoded = text.encode("utf-8")
        if len(encoded) <= max_bytes:
            return text
        truncated = encoded[:max_bytes]
        return truncated.decode("utf-8", errors="ignore").rstrip()

    @staticmethod
    def _truncate_chars(text: str, max_chars: int) -> str:
        """Truncate text to fit within max_chars (character count)."""
        if not text or len(text) <= max_chars:
            return text
        return text[:max_chars]

    def _validate_fields(self, title: str, author: str, digest: str):
        """Validate and truncate fields to WeChat API limits.

        Official limits (draft/add API):
          title:  ≤ 64 bytes (UTF-8)
          author: ≤ 16 characters (字)
          digest: ≤ 120 bytes (UTF-8)
        """
        TITLE_MAX_BYTES = 64
        AUTHOR_MAX_CHARS = 16
        DIGEST_MAX_BYTES = 120

        new_title = self._truncate_utf8(title, TITLE_MAX_BYTES)
        new_author = self._truncate_chars(author, AUTHOR_MAX_CHARS)
        new_digest = self._truncate_utf8(digest, DIGEST_MAX_BYTES)

        if new_title != title:
            print(f"  ⚠️ 标题截断: {len(title.encode('utf-8'))}B -> {TITLE_MAX_BYTES}B")
            print(f"     原: {title}")
            print(f"     新: {new_title}")
        if new_author != author:
            print(f"  ⚠️ 作者截断: {len(author)}字 -> {AUTHOR_MAX_CHARS}字")
        if new_digest != digest:
            print(f"  ⚠️ 摘要截断: {len(digest.encode('utf-8'))}B -> {DIGEST_MAX_BYTES}B")

        return new_title, new_author, new_digest

    def upload_image(self, image_path: Path) -> str:
        """Upload an image to WeChat CDN for use in article content."""
        if not self._client:
            self.authenticate()

        with open(image_path, "rb") as f:
            result = self._client.media.upload_mass_image(f)

        if isinstance(result, str):
            return result
        elif isinstance(result, dict) and "url" in result:
            return result["url"]
        else:
            raise RuntimeError(f"Unexpected uploadimg response: {result}")

    def upload_cover(self, image_path: Path) -> str:
        """Upload a cover image as permanent material. Returns thumb_media_id."""
        if not self._client:
            self.authenticate()

        with open(image_path, "rb") as f:
            result = self._client.material.add("image", f)

        if isinstance(result, dict) and "media_id" in result:
            return result["media_id"]
        else:
            raise RuntimeError(f"Unexpected cover upload response: {result}")

    def _upload_external_image(self, url: str) -> str:
        """Download an external image by URL and upload to WeChat CDN.

        Uses requests to download, then wechatpy's upload_mass_image
        (media/uploadimg API) which accepts io.BytesIO file-like objects.
        Returns the WeChat CDN URL (mmbiz.qpic.cn).
        """
        import io
        from urllib.parse import unquote, urlparse

        if not self._client:
            self.authenticate()

        resp = requests.get(url, timeout=30)
        resp.raise_for_status()

        # Extract filename from URL for MIME type detection
        parsed = urlparse(url)
        filename = unquote(parsed.path.split("/")[-1]) or "image.jpg"

        file_obj = io.BytesIO(resp.content)
        file_obj.name = filename  # wechatpy uses .name for multipart filename

        result = self._client.media.upload_mass_image(file_obj)

        if isinstance(result, str):
            return result
        elif isinstance(result, dict) and "url" in result:
            return result["url"]
        else:
            raise RuntimeError(f"Unexpected uploadimg response: {result}")

    def _replace_images_in_html(self, html: str) -> str:
        """Ensure all images in HTML are hosted on WeChat CDN.

        Handles three types of image sources:
          1. mmbiz.qpic.cn URLs  → already on WeChat CDN, skip
          2. External HTTP URLs   → download & re-upload to WeChat CDN
          3. Local relative paths → read from disk & upload to WeChat CDN
        """
        img_pattern = re.compile(
            r'<img\s+[^>]*src=["\']([^"\']+)["\']', re.IGNORECASE
        )
        matches = img_pattern.findall(html)
        replaced = 0
        skipped = 0

        for src in matches:
            # Case 1: Already on WeChat CDN — no action needed
            if "mmbiz.qpic.cn" in src:
                skipped += 1
                continue

            # Case 2: External HTTP/HTTPS URL — download & re-upload
            if src.startswith("http://") or src.startswith("https://"):
                try:
                    wx_url = self._upload_external_image(src)
                    html = html.replace(src, wx_url)
                    replaced += 1
                    # Show truncated original URL for readability
                    short_src = src[:60] + "..." if len(src) > 60 else src
                    print(f"  Uploaded: {short_src}")
                    print(f"       -> {wx_url[:60]}...")
                except Exception as e:
                    print(f"  Warning: Failed to upload external image: {e}")
                    print(f"       URL: {src[:80]}")
                continue

            # Case 3: Local relative path — read from output directory
            local_path = self.output_dir / src

            if local_path.exists():
                try:
                    wx_url = self.upload_image(local_path)
                    html = html.replace(src, wx_url)
                    replaced += 1
                    print(f"  Uploaded: {local_path.name} -> {wx_url[:60]}...")
                except Exception as e:
                    print(f"  Warning: Failed to upload {local_path.name}: {e}")
            else:
                print(f"  Warning: Image not found: {local_path}")

        print(f"  共处理 {replaced} 张图片（跳过 {skipped} 张已在微信 CDN）")
        return html

    def create_draft(self, title: str, content: str, metadata: dict) -> PublishResult:
        """Create a draft article via POST /cgi-bin/draft/add.

        Automatically validates and truncates title/author/digest
        to comply with WeChat API byte limits.
        """
        if not self._access_token:
            self.authenticate()

        raw_author = metadata.get("author", "")
        raw_digest = metadata.get("digest", "")

        # Validate and auto-truncate fields
        safe_title, safe_author, safe_digest = self._validate_fields(
            title, raw_author, raw_digest
        )

        article = {
            "title": safe_title,
            "content": content,
            "digest": safe_digest,
        }
        # Only include author if non-empty
        if safe_author:
            article["author"] = safe_author

        thumb_media_id = metadata.get("thumb_media_id")
        if thumb_media_id:
            article["thumb_media_id"] = thumb_media_id

        if metadata.get("content_source_url"):
            article["content_source_url"] = metadata["content_source_url"]
        if metadata.get("need_open_comment"):
            article["need_open_comment"] = 1

        try:
            result = self._api_post("draft/add", {"articles": [article]})
            media_id = result.get("media_id", "")
            return PublishResult(
                status="draft_created",
                message=f"Draft created successfully. media_id={media_id}",
                draft_id=media_id,
            )
        except Exception as e:
            return PublishResult(
                status="error",
                message=f"Failed to create draft: {e}",
            )

    def publish(self, draft_id: str) -> PublishResult:
        """Publish a draft via POST /cgi-bin/freepublish/submit."""
        if not self._access_token:
            self.authenticate()

        try:
            result = self._api_post("freepublish/submit", {"media_id": draft_id})
            publish_id = str(result.get("publish_id", ""))
            return PublishResult(
                status="publishing",
                message=f"Publish submitted. publish_id={publish_id}. "
                        f"Note: Task submitted, not yet complete.",
                publish_id=publish_id,
                draft_id=draft_id,
            )
        except Exception as e:
            return PublishResult(
                status="error",
                message=f"Failed to publish: {e}",
                draft_id=draft_id,
            )

    def get_status(self, publish_id: str) -> PublishResult:
        """Check publish status via POST /cgi-bin/freepublish/get."""
        if not self._access_token:
            self.authenticate()

        try:
            result = self._api_post("freepublish/get", {"publish_id": publish_id})
            publish_status = result.get("publish_status", -1)

            if publish_status == 0:
                article_detail = result.get("article_detail", {})
                items = article_detail.get("item", [])
                url = items[0].get("article_url", "") if items else ""
                return PublishResult(
                    status="success",
                    message="Article published successfully.",
                    publish_id=publish_id,
                    url=url,
                )
            elif publish_status == 1:
                return PublishResult(
                    status="publishing",
                    message="Still publishing, please check again later.",
                    publish_id=publish_id,
                )
            else:
                fail_idx = publish_status - 2 if publish_status > 1 else 0
                return PublishResult(
                    status="error",
                    message=f"Publish failed at article index {fail_idx}. "
                            f"Check content for policy violations.",
                    publish_id=publish_id,
                )
        except Exception as e:
            return PublishResult(
                status="error",
                message=f"Failed to get status: {e}",
                publish_id=publish_id,
            )

    def full_publish_flow(self, auto_publish: bool = False) -> PublishResult:
        """Execute the complete publish workflow."""
        print(f"\n{'='*50}")
        print(f"微信公众号发布流程")
        print(f"{'='*50}\n")

        # Step 1: Authenticate
        print("[1/6] 认证中...")
        self.authenticate()
        print("  ✅ 认证成功\n")

        # Step 2: Load metadata
        print("[2/6] 加载元数据...")
        meta = self.load_metadata()
        article_meta = meta.get("article", {})
        title = article_meta.get("title", "Untitled")
        digest = article_meta.get("digest", "")
        author = meta.get("author", {}).get("name", "")
        print(f"  标题: {title}")
        print(f"  摘要: {digest}")
        print(f"  作者: {author}\n")

        # Step 3: Load HTML
        print("[3/6] 加载 HTML 文章...")
        html = self.load_article_html()
        print(f"  HTML 长度: {len(html)} 字符\n")

        # Step 4: Upload images
        print("[4/6] 上传文章内图片到微信 CDN...")
        html = self._replace_images_in_html(html)
        print("  ✅ 图片处理完成\n")

        # Step 5: Upload cover and create draft
        print("[5/6] 上传封面并创建草稿...")
        thumb_media_id = None
        cover = self.get_cover_path(meta)
        if cover:
            try:
                thumb_media_id = self.upload_cover(cover)
                print(f"  封面: {cover.name} -> {thumb_media_id[:20]}...")
            except Exception as e:
                print(f"  Warning: 封面上传失败: {e}（将使用默认封面）")
        else:
            print("  ⚠️ metadata.yaml 未指定 medias.cover.path，跳过封面上传")

        draft_result = self.create_draft(
            title=title,
            content=html,
            metadata={
                "digest": digest,
                "author": author,
                "thumb_media_id": thumb_media_id,
            },
        )
        print(f"  {draft_result.message}\n")

        if draft_result.status == "error":
            return draft_result

        # Step 6: Publish (optional)
        if auto_publish and draft_result.draft_id:
            print("[6/6] 发布草稿...")
            pub_result = self.publish(draft_result.draft_id)
            print(f"  {pub_result.message}\n")

            self.update_metadata({
                "platform": self.platform_id,
                "action": "published",
                "draft_id": draft_result.draft_id,
                "publish_id": pub_result.publish_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            })
            return pub_result
        else:
            print("[6/6] 草稿已创建，跳过发布（需用户确认）\n")
            self.update_metadata({
                "platform": self.platform_id,
                "action": "draft_created",
                "draft_id": draft_result.draft_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            })
            return draft_result
