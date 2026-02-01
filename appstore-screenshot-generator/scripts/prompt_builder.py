#!/usr/bin/env python3
# =============================================================================
# Prompt 构建器
# =============================================================================
# 文件说明书（每次更新文件内容的时候记得更新我）
#
# ## 核心功能
# 读取 config.yaml 中的预设模板，根据应用类型和参数构建最终的生成提示词
#
# ## input（输入）
# - 应用类型（photography, fitness, productivity, social, gaming, finance）
# - 自定义参数（headline, colors, device 等）
# - 语言/地区设置
#
# ## output（输出）
# - 完整的、可直接用于 Gemini API 的提示词字符串
#
# ## position（定位）
# 作为 prompt 模板管理和变量替换的核心模块
#
# ## dependency（依赖）
# - 依赖 config.yaml 提供模板定义
# - 被 SKILL.md 工作流调用
# - 输出传递给 gemini_client.py
# =============================================================================

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


def _load_skill_env():
    """自动加载 skill 目录下的 .env 文件"""
    skill_dir = Path(__file__).parent.parent
    env_file = skill_dir / ".env"

    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    if key and key not in os.environ:
                        os.environ[key] = value


# 模块加载时自动读取 .env
_load_skill_env()


@dataclass
class PromptConfig:
    """Prompt 配置"""
    template_name: str
    headline: str
    subheadline: str = ""
    device_model: str = "iPhone 15 Pro Max"
    device_angle: str = "straight, facing forward"
    device_position: str = "center"
    frame_color: str = "titanium natural"
    background_style: str = "gradient"
    primary_color: str = "#667eea"
    secondary_color: str = "#764ba2"
    text_color: str = "white"
    text_position: str = "top center"
    width: int = 1290
    height: int = 2796
    language: str = "en"
    custom_vars: Dict[str, Any] = field(default_factory=dict)


class PromptBuilder:
    """Prompt 构建器，基于预设模板生成 AI 提示词"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化 Prompt 构建器

        Args:
            config_path: 配置文件路径，默认使用同目录下的 config.yaml
        """
        if config_path is None:
            # 默认配置文件路径
            skill_dir = Path(__file__).parent.parent
            config_path = skill_dir / "config.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.templates = self.config.get("prompt_templates", {})

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_available_templates(self) -> List[str]:
        """获取所有可用的模板名称"""
        return list(self.templates.keys())

    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """获取模板详细信息"""
        if template_name not in self.templates:
            raise ValueError(f"模板不存在: {template_name}")
        return self.templates[template_name]

    def get_headline_options(
        self,
        template_name: str,
        language: str = "en"
    ) -> List[str]:
        """
        获取模板的预设标题选项

        Args:
            template_name: 模板名称
            language: 语言代码

        Returns:
            标题列表
        """
        template = self.get_template_info(template_name)
        headline_options = template.get("headline_options", {})
        return headline_options.get(language, headline_options.get("en", []))

    def build_prompt(self, config: PromptConfig) -> str:
        """
        构建完整的生成提示词

        Args:
            config: Prompt 配置对象

        Returns:
            完整的提示词字符串
        """
        template_info = self.get_template_info(config.template_name)
        template = template_info.get("template", "")

        # 获取模板默认变量
        default_vars = template_info.get("variables", {})

        # 合并变量（配置 > 自定义 > 默认）
        variables = {
            **default_vars,
            **config.custom_vars,
            "headline_text": config.headline,
            "subheadline_text": config.subheadline,
            "device_model": config.device_model,
            "device_angle": config.device_angle,
            "device_position": config.device_position,
            "frame_color": config.frame_color,
            "background_style": config.background_style,
            "primary_color": config.primary_color,
            "secondary_color": config.secondary_color,
            "text_color": config.text_color,
            "text_position": config.text_position,
            "width": config.width,
            "height": config.height,
        }

        # 替换模板变量
        prompt = template
        for key, value in variables.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))

        return prompt.strip()

    def build_quick_prompt(
        self,
        app_type: str,
        headline: str,
        language: str = "en",
        **kwargs
    ) -> str:
        """
        快速构建提示词的便捷方法

        Args:
            app_type: 应用类型 (photography, fitness, productivity, social, gaming, finance)
            headline: 标题文案
            language: 语言
            **kwargs: 其他自定义参数

        Returns:
            完整的提示词字符串
        """
        # 应用类型到模板名称的映射
        type_mapping = {
            "photography": "photography",
            "camera": "photography",
            "photo": "photography",
            "fitness": "fitness",
            "health": "fitness",
            "workout": "fitness",
            "productivity": "productivity",
            "tool": "productivity",
            "utility": "productivity",
            "social": "social",
            "lifestyle": "social",
            "chat": "social",
            "gaming": "gaming",
            "game": "gaming",
            "finance": "finance",
            "business": "finance",
            "banking": "finance",
        }

        template_name = type_mapping.get(app_type.lower(), "base")

        config = PromptConfig(
            template_name=template_name,
            headline=headline,
            language=language,
            custom_vars=kwargs
        )

        return self.build_prompt(config)


# =============================================================================
# 预设的快捷 Prompt 生成函数
# =============================================================================

def photography_prompt(
    headline: str = "Capture Perfect Moments",
    language: str = "en"
) -> str:
    """生成摄影类应用的 Prompt"""
    builder = PromptBuilder()
    return builder.build_quick_prompt("photography", headline, language)


def fitness_prompt(
    headline: str = "Transform Your Body",
    language: str = "en"
) -> str:
    """生成健身类应用的 Prompt"""
    builder = PromptBuilder()
    return builder.build_quick_prompt("fitness", headline, language)


def productivity_prompt(
    headline: str = "Simplify Your Day",
    language: str = "en"
) -> str:
    """生成生产力类应用的 Prompt"""
    builder = PromptBuilder()
    return builder.build_quick_prompt("productivity", headline, language)


def social_prompt(
    headline: str = "Connect Authentically",
    language: str = "en"
) -> str:
    """生成社交类应用的 Prompt"""
    builder = PromptBuilder()
    return builder.build_quick_prompt("social", headline, language)


def gaming_prompt(
    headline: str = "Epic Adventure Awaits",
    language: str = "en"
) -> str:
    """生成游戏类应用的 Prompt"""
    builder = PromptBuilder()
    return builder.build_quick_prompt("gaming", headline, language)


def finance_prompt(
    headline: str = "Your Money, Simplified",
    language: str = "en"
) -> str:
    """生成金融类应用的 Prompt"""
    builder = PromptBuilder()
    return builder.build_quick_prompt("finance", headline, language)


# =============================================================================
# PoseCam 专用 Prompt 生成
# =============================================================================

def posecam_prompt(
    headline: str = "Pose Like a Pro",
    feature: str = "pose guidance",
    language: str = "en"
) -> str:
    """
    为 PoseCam 应用生成专属 Prompt

    Args:
        headline: 标题文案
        feature: 突出的功能特性
        language: 语言

    Returns:
        完整的提示词
    """
    # 基于 photography 模板，但添加 PoseCam 特定元素
    builder = PromptBuilder()

    config = PromptConfig(
        template_name="photography",
        headline=headline,
        language=language,
        custom_vars={
            "app_specific_elements": f"""
            [POSECAM SPECIFIC]
            - Feature highlight: {feature}
            - Include subtle pose silhouette guides in background
            - Show pose reference overlay on device screen
            - Add elegant pose guide lines as decorative elements
            """,
        }
    )

    base_prompt = builder.build_prompt(config)

    # 添加 PoseCam 特定指令
    posecam_additions = f"""

    [POSECAM BRAND ELEMENTS]
    - The app helps users take better photos with AI pose guidance
    - Highlight the {feature} feature visible on screen
    - Include subtle human silhouette pose guides as background decoration
    - Maintain elegant, professional photography aesthetic
    - The overall feel should be: creative, helpful, professional
    """

    return base_prompt + posecam_additions


# =============================================================================
# 命令行入口
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prompt 构建器")
    parser.add_argument(
        "--type", "-t",
        choices=["photography", "fitness", "productivity", "social", "gaming", "finance", "base"],
        default="base",
        help="应用类型"
    )
    parser.add_argument("--headline", "-h", default="Your App Name", help="标题文案")
    parser.add_argument("--language", "-l", default="en", help="语言")
    parser.add_argument("--list", action="store_true", help="列出所有可用模板")
    parser.add_argument("--headlines", action="store_true", help="列出模板的预设标题")

    args = parser.parse_args()

    builder = PromptBuilder()

    if args.list:
        print("可用模板:")
        for name in builder.get_available_templates():
            info = builder.get_template_info(name)
            print(f"  - {name}: {info.get('description', '')}")
    elif args.headlines:
        print(f"模板 '{args.type}' 的预设标题 ({args.language}):")
        for headline in builder.get_headline_options(args.type, args.language):
            print(f"  - {headline}")
    else:
        prompt = builder.build_quick_prompt(args.type, args.headline, args.language)
        print("生成的 Prompt:")
        print("-" * 60)
        print(prompt)
