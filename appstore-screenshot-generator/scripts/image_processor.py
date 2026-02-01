#!/usr/bin/env python3
# =============================================================================
# 图像处理器
# =============================================================================
# 文件说明书（每次更新文件内容的时候记得更新我）
#
# ## 核心功能
# 处理输入截图和输出图像，包括格式转换、尺寸调整、多尺寸生成
#
# ## input（输入）
# - 原始截图（来自 XcodeBuildMCP）
# - 生成的商店图
# - 尺寸规格配置
#
# ## output（输出）
# - 处理后的图像文件
# - 多尺寸变体
# - 图像元数据
#
# ## position（定位）
# 作为图像后处理的工具模块
#
# ## dependency（依赖）
# - 依赖 config.yaml 提供尺寸规格
# - 依赖 PIL/Pillow 进行图像处理
# - 被 SKILL.md 工作流调用
# =============================================================================

import os
import yaml
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("警告: Pillow 未安装，部分图像处理功能不可用")
    print("安装命令: pip install Pillow")


@dataclass
class ImageInfo:
    """图像信息"""
    path: str
    width: int
    height: int
    format: str
    size_bytes: int


@dataclass
class ProcessResult:
    """处理结果"""
    success: bool
    output_path: Optional[str] = None
    output_paths: Optional[List[str]] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ImageProcessor:
    """图像处理器"""

    # App Store 截图尺寸规格
    SCREENSHOT_SIZES = {
        "iphone_67": {"width": 1290, "height": 2796, "name": "iPhone 6.7 inch"},
        "iphone_65": {"width": 1284, "height": 2778, "name": "iPhone 6.5 inch"},
        "iphone_55": {"width": 1242, "height": 2208, "name": "iPhone 5.5 inch"},
        "ipad_129": {"width": 2048, "height": 2732, "name": "iPad Pro 12.9 inch"},
        "ipad_11": {"width": 1668, "height": 2388, "name": "iPad Pro 11 inch"},
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化图像处理器

        Args:
            config_path: 配置文件路径
        """
        self.config = {}
        if config_path:
            self.config = self._load_config(config_path)

        # 从配置加载尺寸（如果有）
        if "screenshot_sizes" in self.config:
            for key, value in self.config["screenshot_sizes"].items():
                self.SCREENSHOT_SIZES[key] = value

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        path = Path(config_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def get_image_info(self, image_path: Union[str, Path]) -> ImageInfo:
        """
        获取图像信息

        Args:
            image_path: 图像路径

        Returns:
            ImageInfo 对象
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"图像不存在: {path}")

        if not HAS_PIL:
            # 没有 PIL 时返回基本信息
            stat = path.stat()
            return ImageInfo(
                path=str(path),
                width=0,
                height=0,
                format=path.suffix.upper().lstrip("."),
                size_bytes=stat.st_size
            )

        with Image.open(path) as img:
            return ImageInfo(
                path=str(path),
                width=img.width,
                height=img.height,
                format=img.format or path.suffix.upper().lstrip("."),
                size_bytes=path.stat().st_size
            )

    def resize_image(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        width: int,
        height: int,
        maintain_aspect: bool = True
    ) -> ProcessResult:
        """
        调整图像尺寸

        Args:
            input_path: 输入图像路径
            output_path: 输出图像路径
            width: 目标宽度
            height: 目标高度
            maintain_aspect: 是否保持宽高比

        Returns:
            ProcessResult 对象
        """
        if not HAS_PIL:
            return ProcessResult(
                success=False,
                error_message="Pillow 未安装，无法调整尺寸"
            )

        try:
            input_path = Path(input_path)
            output_path = Path(output_path)

            with Image.open(input_path) as img:
                if maintain_aspect:
                    # 保持宽高比，使用 thumbnail
                    img.thumbnail((width, height), Image.Resampling.LANCZOS)
                else:
                    # 强制调整到指定尺寸
                    img = img.resize((width, height), Image.Resampling.LANCZOS)

                # 确保输出目录存在
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # 保存
                img.save(output_path, quality=95)

            return ProcessResult(
                success=True,
                output_path=str(output_path),
                metadata={"width": width, "height": height}
            )

        except Exception as e:
            return ProcessResult(
                success=False,
                error_message=f"调整尺寸失败: {str(e)}"
            )

    def generate_all_sizes(
        self,
        input_path: Union[str, Path],
        output_dir: Union[str, Path],
        base_name: str = "screenshot",
        sizes: Optional[List[str]] = None
    ) -> ProcessResult:
        """
        生成所有 App Store 需要的尺寸

        Args:
            input_path: 输入图像路径
            output_dir: 输出目录
            base_name: 输出文件基础名称
            sizes: 要生成的尺寸列表，默认生成所有

        Returns:
            ProcessResult 对象，包含所有输出路径
        """
        if not HAS_PIL:
            return ProcessResult(
                success=False,
                error_message="Pillow 未安装，无法生成多尺寸"
            )

        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        target_sizes = sizes or list(self.SCREENSHOT_SIZES.keys())
        output_paths = []
        errors = []

        for size_key in target_sizes:
            if size_key not in self.SCREENSHOT_SIZES:
                errors.append(f"未知尺寸: {size_key}")
                continue

            size_info = self.SCREENSHOT_SIZES[size_key]
            output_path = output_dir / f"{base_name}_{size_key}.png"

            result = self.resize_image(
                input_path,
                output_path,
                size_info["width"],
                size_info["height"],
                maintain_aspect=False  # App Store 需要精确尺寸
            )

            if result.success:
                output_paths.append(str(output_path))
            else:
                errors.append(f"{size_key}: {result.error_message}")

        if output_paths:
            return ProcessResult(
                success=True,
                output_paths=output_paths,
                metadata={
                    "generated_count": len(output_paths),
                    "errors": errors if errors else None
                }
            )
        else:
            return ProcessResult(
                success=False,
                error_message=f"所有尺寸生成失败: {'; '.join(errors)}"
            )

    def convert_format(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        format: str = "PNG",
        quality: int = 95
    ) -> ProcessResult:
        """
        转换图像格式

        Args:
            input_path: 输入路径
            output_path: 输出路径
            format: 目标格式 (PNG, JPEG, WEBP)
            quality: 质量 (1-100)

        Returns:
            ProcessResult 对象
        """
        if not HAS_PIL:
            return ProcessResult(
                success=False,
                error_message="Pillow 未安装，无法转换格式"
            )

        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with Image.open(input_path) as img:
                # PNG 不支持 quality 参数
                if format.upper() == "PNG":
                    img.save(output_path, format=format)
                else:
                    img.save(output_path, format=format, quality=quality)

            return ProcessResult(
                success=True,
                output_path=str(output_path)
            )

        except Exception as e:
            return ProcessResult(
                success=False,
                error_message=f"格式转换失败: {str(e)}"
            )

    def image_to_base64(self, image_path: Union[str, Path]) -> str:
        """
        将图像转换为 Base64 编码

        Args:
            image_path: 图像路径

        Returns:
            Base64 编码字符串
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"图像不存在: {path}")

        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def base64_to_image(
        self,
        base64_data: str,
        output_path: Union[str, Path]
    ) -> ProcessResult:
        """
        将 Base64 数据保存为图像

        Args:
            base64_data: Base64 编码数据
            output_path: 输出路径

        Returns:
            ProcessResult 对象
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            image_data = base64.b64decode(base64_data)
            output_path.write_bytes(image_data)

            return ProcessResult(
                success=True,
                output_path=str(output_path)
            )

        except Exception as e:
            return ProcessResult(
                success=False,
                error_message=f"Base64 转换失败: {str(e)}"
            )

    def organize_by_locale(
        self,
        image_paths: List[str],
        output_dir: Union[str, Path],
        locales: List[str]
    ) -> ProcessResult:
        """
        按语言区域组织图片

        Args:
            image_paths: 图片路径列表
            output_dir: 输出目录
            locales: 语言区域列表

        Returns:
            ProcessResult 对象
        """
        import shutil

        output_dir = Path(output_dir)
        organized_paths = []

        try:
            for locale in locales:
                locale_dir = output_dir / locale
                locale_dir.mkdir(parents=True, exist_ok=True)

                for img_path in image_paths:
                    src = Path(img_path)
                    dst = locale_dir / src.name
                    shutil.copy2(src, dst)
                    organized_paths.append(str(dst))

            return ProcessResult(
                success=True,
                output_paths=organized_paths,
                metadata={"locales": locales, "files_per_locale": len(image_paths)}
            )

        except Exception as e:
            return ProcessResult(
                success=False,
                error_message=f"组织文件失败: {str(e)}"
            )


# =============================================================================
# 便捷函数
# =============================================================================

def prepare_screenshot(
    screenshot_path: str,
    output_dir: str = "./appstore_screenshots"
) -> ProcessResult:
    """
    准备 App Store 截图（生成所有需要的尺寸）

    Args:
        screenshot_path: 原始截图路径
        output_dir: 输出目录

    Returns:
        ProcessResult 对象
    """
    processor = ImageProcessor()
    return processor.generate_all_sizes(screenshot_path, output_dir)


# =============================================================================
# 命令行入口
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="图像处理器")
    parser.add_argument("input", help="输入图像路径")
    parser.add_argument("--output", "-o", help="输出路径/目录")
    parser.add_argument(
        "--action",
        "-a",
        choices=["info", "resize", "all-sizes", "convert", "base64"],
        default="info",
        help="操作类型"
    )
    parser.add_argument("--width", "-w", type=int, help="目标宽度")
    parser.add_argument("--height", "-H", type=int, help="目标高度")
    parser.add_argument("--format", "-f", default="PNG", help="输出格式")

    args = parser.parse_args()

    processor = ImageProcessor()

    if args.action == "info":
        info = processor.get_image_info(args.input)
        print(f"路径: {info.path}")
        print(f"尺寸: {info.width}x{info.height}")
        print(f"格式: {info.format}")
        print(f"大小: {info.size_bytes / 1024:.1f} KB")

    elif args.action == "resize":
        if not args.output or not args.width or not args.height:
            print("错误: resize 需要 --output, --width, --height 参数")
        else:
            result = processor.resize_image(
                args.input, args.output, args.width, args.height
            )
            if result.success:
                print(f"✅ 调整完成: {result.output_path}")
            else:
                print(f"❌ 失败: {result.error_message}")

    elif args.action == "all-sizes":
        output_dir = args.output or "./appstore_screenshots"
        result = processor.generate_all_sizes(args.input, output_dir)
        if result.success:
            print(f"✅ 生成了 {len(result.output_paths)} 个尺寸:")
            for path in result.output_paths:
                print(f"   - {path}")
        else:
            print(f"❌ 失败: {result.error_message}")

    elif args.action == "convert":
        if not args.output:
            print("错误: convert 需要 --output 参数")
        else:
            result = processor.convert_format(args.input, args.output, args.format)
            if result.success:
                print(f"✅ 转换完成: {result.output_path}")
            else:
                print(f"❌ 失败: {result.error_message}")

    elif args.action == "base64":
        b64 = processor.image_to_base64(args.input)
        print(f"Base64 编码 (前100字符): {b64[:100]}...")
        print(f"总长度: {len(b64)} 字符")
