#!/usr/bin/env python3
# =============================================================================
# Gemini API 客户端
# =============================================================================
# 文件说明书（每次更新文件内容的时候记得更新我）
#
# ## 核心功能
# 封装 Gemini API 调用，支持直接调用和 Cloudflare AI Gateway 代理
#
# ## input（输入）
# - 图片数据（Base64 编码或文件路径）
# - Prompt 文本
# - 配置参数（API key、模型选择等）
#
# ## output（输出）
# - 生成的图片数据（Base64 或保存到文件）
# - API 响应元数据
#
# ## position（定位）
# 作为与 Gemini API 交互的唯一入口，封装所有网络请求逻辑
#
# ## dependency（依赖）
# - 依赖 config.yaml 提供 API 配置
# - 被 SKILL.md 工作流调用
# =============================================================================

import os
import base64
import json
import time
import requests
from pathlib import Path
from typing import Optional, Union, Dict, Any
from dataclasses import dataclass


def _load_skill_env():
    """自动加载 skill 目录下的 .env 文件"""
    skill_dir = Path(__file__).parent.parent
    env_file = skill_dir / ".env"

    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith("#"):
                    continue
                # 解析 KEY=VALUE
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    # 只设置未定义的环境变量
                    if key and key not in os.environ:
                        os.environ[key] = value


# 模块加载时自动读取 .env
_load_skill_env()


@dataclass
class GenerationResult:
    """图像生成结果"""
    success: bool
    image_data: Optional[bytes] = None
    image_path: Optional[str] = None
    text_response: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class GeminiClient:
    """Gemini API 客户端，支持图像生成和编辑"""

    # 默认配置
    DEFAULT_MODEL = "gemini-2.5-flash-image"
    DEFAULT_TIMEOUT = 60000
    DEFAULT_MAX_RETRIES = 3

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        cloudflare_account_id: Optional[str] = None,
        cloudflare_gateway_id: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES
    ):
        """
        初始化 Gemini 客户端

        Args:
            api_key: Gemini API Key，默认从环境变量 GEMINI_API_KEY 读取
            model: 使用的模型，默认 gemini-2.5-flash-image
            cloudflare_account_id: Cloudflare 账户 ID（可选）
            cloudflare_gateway_id: Cloudflare Gateway ID（可选）
            timeout: 请求超时时间（毫秒）
            max_retries: 最大重试次数
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY 未设置，请在环境变量或参数中提供")

        self.model = model or os.environ.get("GEMINI_MODEL", self.DEFAULT_MODEL)
        self.timeout = timeout / 1000  # 转换为秒
        self.max_retries = max_retries

        # Cloudflare AI Gateway 配置
        self.cloudflare_account_id = cloudflare_account_id or os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        self.cloudflare_gateway_id = cloudflare_gateway_id or os.environ.get("CLOUDFLARE_GATEWAY_ID")
        self.use_cloudflare = bool(self.cloudflare_account_id and self.cloudflare_gateway_id)

        # 构建 API 基础 URL
        self.base_url = self._build_base_url()

    def _build_base_url(self) -> str:
        """构建 API 基础 URL"""
        if self.use_cloudflare:
            return (
                f"https://gateway.ai.cloudflare.com/v1/"
                f"{self.cloudflare_account_id}/{self.cloudflare_gateway_id}/"
                f"google-ai-studio/v1beta"
            )
        return "https://generativelanguage.googleapis.com/v1beta"

    def _encode_image(self, image_source: Union[str, bytes, Path]) -> tuple[str, str]:
        """
        编码图片为 Base64

        Args:
            image_source: 图片路径、URL 或字节数据

        Returns:
            (base64_data, mime_type)
        """
        if isinstance(image_source, bytes):
            # 已经是字节数据
            data = base64.b64encode(image_source).decode("utf-8")
            mime_type = "image/png"  # 默认
            return data, mime_type

        if isinstance(image_source, (str, Path)):
            path = Path(image_source)
            if path.exists():
                # 从文件读取
                with open(path, "rb") as f:
                    data = base64.b64encode(f.read()).decode("utf-8")

                # 根据扩展名确定 MIME 类型
                ext = path.suffix.lower()
                mime_types = {
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".webp": "image/webp",
                    ".gif": "image/gif"
                }
                mime_type = mime_types.get(ext, "image/png")
                return data, mime_type

            # 检查是否是 Base64 字符串
            if isinstance(image_source, str) and len(image_source) > 100:
                try:
                    base64.b64decode(image_source)
                    return image_source, "image/png"
                except Exception:
                    pass

        raise ValueError(f"无法处理的图片来源: {type(image_source)}")

    def generate_image(
        self,
        prompt: str,
        input_image: Optional[Union[str, bytes, Path]] = None,
        output_path: Optional[Union[str, Path]] = None,
        aspect_ratio: str = "9:16"
    ) -> GenerationResult:
        """
        生成或编辑图像

        Args:
            prompt: 生成提示词
            input_image: 输入图片（用于图生图）
            output_path: 输出路径（如果指定则保存到文件）
            aspect_ratio: 宽高比

        Returns:
            GenerationResult 对象
        """
        # 构建请求内容
        parts = []

        # 如果有输入图片，先添加图片
        if input_image:
            image_data, mime_type = self._encode_image(input_image)
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_data
                }
            })

        # 添加文本提示
        parts.append({"text": prompt})

        # 构建请求体
        request_body = {
            "contents": [{
                "parts": parts
            }],
            "generationConfig": {
                "responseModalities": ["IMAGE", "TEXT"]
            }
        }

        # 发送请求
        url = f"{self.base_url}/models/{self.model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=request_body,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return self._parse_response(response.json(), output_path)

                elif response.status_code == 429:
                    # 速率限制，等待后重试
                    wait_time = 2 ** attempt
                    print(f"速率限制，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue

                else:
                    error_msg = f"API 错误 {response.status_code}: {response.text}"
                    if attempt == self.max_retries - 1:
                        return GenerationResult(
                            success=False,
                            error_message=error_msg
                        )

            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    return GenerationResult(
                        success=False,
                        error_message="请求超时"
                    )

            except Exception as e:
                if attempt == self.max_retries - 1:
                    return GenerationResult(
                        success=False,
                        error_message=f"请求异常: {str(e)}"
                    )

        return GenerationResult(
            success=False,
            error_message="达到最大重试次数"
        )

    def _parse_response(
        self,
        response_data: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None
    ) -> GenerationResult:
        """解析 API 响应"""
        try:
            candidates = response_data.get("candidates", [])
            if not candidates:
                return GenerationResult(
                    success=False,
                    error_message="API 返回空结果"
                )

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])

            image_data = None
            text_response = None

            for part in parts:
                if "text" in part:
                    text_response = part["text"]
                elif "inlineData" in part:
                    inline_data = part["inlineData"]
                    image_data = base64.b64decode(inline_data["data"])

            if image_data:
                # 如果指定了输出路径，保存文件
                if output_path:
                    output_path = Path(output_path)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(image_data)

                return GenerationResult(
                    success=True,
                    image_data=image_data,
                    image_path=str(output_path) if output_path else None,
                    text_response=text_response,
                    metadata={"candidates": len(candidates)}
                )

            return GenerationResult(
                success=False,
                text_response=text_response,
                error_message="API 未返回图像数据"
            )

        except Exception as e:
            return GenerationResult(
                success=False,
                error_message=f"解析响应失败: {str(e)}"
            )


# =============================================================================
# 便捷函数
# =============================================================================

def generate_appstore_screenshot(
    screenshot_path: str,
    prompt: str,
    output_path: Optional[str] = None
) -> GenerationResult:
    """
    生成 App Store 商店图的便捷函数

    Args:
        screenshot_path: iOS 模拟器截图路径
        prompt: 生成提示词
        output_path: 输出路径

    Returns:
        GenerationResult 对象
    """
    client = GeminiClient()
    return client.generate_image(
        prompt=prompt,
        input_image=screenshot_path,
        output_path=output_path
    )


# =============================================================================
# 命令行入口
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gemini 图像生成客户端")
    parser.add_argument("--prompt", "-p", required=True, help="生成提示词")
    parser.add_argument("--input", "-i", help="输入图片路径")
    parser.add_argument("--output", "-o", help="输出图片路径")
    parser.add_argument("--model", "-m", help="模型名称")

    args = parser.parse_args()

    client = GeminiClient(model=args.model)
    result = client.generate_image(
        prompt=args.prompt,
        input_image=args.input,
        output_path=args.output
    )

    if result.success:
        print(f"✅ 图像生成成功")
        if result.image_path:
            print(f"   保存到: {result.image_path}")
        if result.text_response:
            print(f"   AI 响应: {result.text_response}")
    else:
        print(f"❌ 图像生成失败: {result.error_message}")
