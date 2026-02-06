#!/usr/bin/env python3
# ============================================================
# 文件说明书 (File Manual)
# ============================================================
# 核心功能 (Core Function)
# 知乎发布器占位（Phase 2），当前仅提示未实现。
#
# 定位 (Position)
# content-publisher 的知乎平台实现占位。
#
# 维护规则 (Maintenance Rules)
# 1. 每次修改代码逻辑后，必须检查并更新上述信息。
# 2. 禁止修改或删除本【维护规则】章节的内容。
# ============================================================

from pathlib import Path
from .base import PlatformPublisher, PublishResult


class ZhihuPublisher(PlatformPublisher):
    """Zhihu publisher - Phase 2 placeholder."""

    platform_id = "zhihu"
    platform_name = "知乎"

    def authenticate(self) -> bool:
        raise NotImplementedError("知乎发布功能开发中（Phase 2）")

    def upload_image(self, image_path: Path) -> str:
        raise NotImplementedError("知乎发布功能开发中（Phase 2）")

    def create_draft(self, title: str, content: str, metadata: dict) -> PublishResult:
        return PublishResult(status="error", message="知乎发布功能开发中（Phase 2）")

    def publish(self, draft_id: str) -> PublishResult:
        return PublishResult(status="error", message="知乎发布功能开发中（Phase 2）")

    def get_status(self, publish_id: str) -> PublishResult:
        return PublishResult(status="error", message="知乎发布功能开发中（Phase 2）")
