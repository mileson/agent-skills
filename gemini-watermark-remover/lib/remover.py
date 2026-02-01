# 文件说明书（每次更新文件内容的时候记得更新我）
#
# ## 核心功能
# 检测并移除 Gemini (nano banana) 生成图片中的 ✦ 水印
#
# ## input（输入）
# - 图片文件路径 或 Base64 编码的图片数据
# - 可选：水印模板文件路径
#
# ## output（输出）
# - 移除水印后的图片（文件路径 或 Base64 编码）
# - JSON 格式的处理结果（适配 n8n）
#
# ## position（定位）
# 核心算法模块，位于 lib/ 目录，由 batch_processor.py 调用
#
# ## dependency（依赖）
# - PIL/Pillow 提供图像处理能力
# - NumPy 提供数值计算
# - ../assets/bg_48.png / bg_96.png 水印模板文件（相对于 Skill 根目录）

import os
import sys
import json
import base64
import argparse
from io import BytesIO
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

import numpy as np
from PIL import Image

# ============================================================================
# 配置常量
# ============================================================================

MAX_ALPHA = 0.99  # 防止除零
MIN_CONFIDENCE = 0.3  # 最小匹配置信度
SEARCH_AREA_RATIO = 0.25  # 搜索区域比例（图片右下角 25%）

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 获取 Skill 根目录（脚本在 lib/ 下，需要上一级到根目录）
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)

# 默认模板路径（现在在 assets/ 目录）
DEFAULT_TEMPLATES = {
    48: os.path.join(SKILL_ROOT, "assets", "bg_48.png"),
    96: os.path.join(SKILL_ROOT, "assets", "bg_96.png"),
}


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class WatermarkTemplate:
    """水印模板数据"""
    size: int
    image: np.ndarray
    alpha_map: np.ndarray


@dataclass
class DetectionResult:
    """水印检测结果"""
    detected: bool
    x: int = 0
    y: int = 0
    size: int = 0
    confidence: float = 0.0


@dataclass
class ProcessResult:
    """处理结果"""
    success: bool
    watermark_detected: bool
    message: str
    output_path: Optional[str] = None
    output_base64: Optional[str] = None
    detection_info: Optional[Dict[str, Any]] = None


# ============================================================================
# 水印模板处理
# ============================================================================

def load_template(path: str) -> np.ndarray:
    """加载水印模板图片"""
    img = Image.open(path).convert("RGB")
    return np.array(img, dtype=np.float32)


def calculate_alpha_map(template: np.ndarray) -> np.ndarray:
    """
    计算 alpha map

    公式: alpha = max(R, G, B) / 255.0
    """
    return np.max(template, axis=2) / 255.0


def load_templates(template_paths: Optional[Dict[int, str]] = None) -> Dict[int, WatermarkTemplate]:
    """加载所有水印模板"""
    paths = template_paths or DEFAULT_TEMPLATES
    templates = {}

    for size, path in paths.items():
        if os.path.exists(path):
            img_array = load_template(path)
            alpha_map = calculate_alpha_map(img_array)
            templates[size] = WatermarkTemplate(
                size=size,
                image=img_array,
                alpha_map=alpha_map
            )

    return templates


# ============================================================================
# 水印检测算法
# ============================================================================

def calculate_correlation(
    image: np.ndarray,
    template: np.ndarray,
    x: int,
    y: int
) -> float:
    """
    计算图像区域与模板的相关性

    使用皮尔逊相关系数
    """
    h, w = template.shape[:2]

    # 边界检查
    if y + h > image.shape[0] or x + w > image.shape[1]:
        return 0.0

    # 提取图像区域
    region = image[y:y+h, x:x+w].astype(np.float32)
    template_f = template.astype(np.float32)

    # 展平为一维数组
    region_flat = region.flatten()
    template_flat = template_f.flatten()

    # 计算相关系数
    n = len(region_flat)
    if n == 0:
        return 0.0

    mean_r = np.mean(region_flat)
    mean_t = np.mean(template_flat)

    std_r = np.std(region_flat)
    std_t = np.std(template_flat)

    if std_r < 1e-6 or std_t < 1e-6:
        return 0.0

    correlation = np.sum((region_flat - mean_r) * (template_flat - mean_t)) / (n * std_r * std_t)

    return max(0.0, correlation)


def search_watermark(
    image: np.ndarray,
    template: WatermarkTemplate,
    search_area_ratio: float = SEARCH_AREA_RATIO
) -> DetectionResult:
    """
    在图像中搜索水印位置

    使用两阶段搜索算法：
    1. 粗搜索：大步长扫描
    2. 精细搜索：在最佳位置附近细化
    """
    img_h, img_w = image.shape[:2]
    size = template.size

    # 计算搜索区域（右下角）
    search_start_x = int(img_w * (1 - search_area_ratio))
    search_start_y = int(img_h * (1 - search_area_ratio))
    search_end_x = img_w - size
    search_end_y = img_h - size

    if search_end_x < search_start_x or search_end_y < search_start_y:
        return DetectionResult(detected=False)

    # 阶段1：粗搜索
    coarse_step = max(1, size // 8)
    best_x, best_y = 0, 0
    best_confidence = 0.0

    for y in range(search_start_y, search_end_y + 1, coarse_step):
        for x in range(search_start_x, search_end_x + 1, coarse_step):
            confidence = calculate_correlation(image, template.image, x, y)
            if confidence > best_confidence:
                best_confidence = confidence
                best_x, best_y = x, y

    if best_confidence < MIN_CONFIDENCE:
        return DetectionResult(detected=False, confidence=best_confidence)

    # 阶段2：精细搜索
    fine_range = coarse_step
    fine_start_x = max(search_start_x, best_x - fine_range)
    fine_end_x = min(search_end_x, best_x + fine_range)
    fine_start_y = max(search_start_y, best_y - fine_range)
    fine_end_y = min(search_end_y, best_y + fine_range)

    for y in range(fine_start_y, fine_end_y + 1):
        for x in range(fine_start_x, fine_end_x + 1):
            confidence = calculate_correlation(image, template.image, x, y)
            if confidence > best_confidence:
                best_confidence = confidence
                best_x, best_y = x, y

    return DetectionResult(
        detected=best_confidence >= MIN_CONFIDENCE,
        x=best_x,
        y=best_y,
        size=size,
        confidence=best_confidence
    )


def detect_watermark(
    image: np.ndarray,
    templates: Dict[int, WatermarkTemplate]
) -> DetectionResult:
    """
    检测图像中的水印

    尝试所有模板尺寸，返回最佳匹配
    """
    best_result = DetectionResult(detected=False)

    # 按尺寸降序排列（优先检测大水印）
    for size in sorted(templates.keys(), reverse=True):
        template = templates[size]
        result = search_watermark(image, template)

        if result.detected and result.confidence > best_result.confidence:
            best_result = result

    return best_result


# ============================================================================
# 水印移除算法
# ============================================================================

def remove_watermark(
    image: np.ndarray,
    detection: DetectionResult,
    template: WatermarkTemplate
) -> np.ndarray:
    """
    使用 Alpha Blending 反向公式移除水印

    公式: original = (watermarked - α × 255) / (1 - α)

    其中 α 是水印的透明度
    """
    result = image.copy().astype(np.float32)

    x, y = detection.x, detection.y
    size = detection.size
    alpha_map = template.alpha_map

    for dy in range(size):
        for dx in range(size):
            img_y = y + dy
            img_x = x + dx

            if img_y >= image.shape[0] or img_x >= image.shape[1]:
                continue

            alpha = alpha_map[dy, dx]

            if alpha < 0.001:
                continue  # 跳过完全透明的像素

            # 限制 alpha 防止除零
            effective_alpha = min(alpha, MAX_ALPHA)

            # 对每个颜色通道应用反向公式
            for c in range(3):
                watermarked = result[img_y, img_x, c]
                original = (watermarked - effective_alpha * 255) / (1.0 - effective_alpha)
                result[img_y, img_x, c] = np.clip(original, 0, 255)

    return result.astype(np.uint8)


# ============================================================================
# 图像 I/O 工具
# ============================================================================

def load_image_from_path(path: str) -> np.ndarray:
    """从文件路径加载图像"""
    img = Image.open(path).convert("RGB")
    return np.array(img)


def load_image_from_base64(data: str) -> np.ndarray:
    """从 Base64 编码加载图像"""
    # 移除可能存在的 data URL 前缀
    if "," in data:
        data = data.split(",", 1)[1]

    img_bytes = base64.b64decode(data)
    img = Image.open(BytesIO(img_bytes)).convert("RGB")
    return np.array(img)


def save_image_to_path(image: np.ndarray, path: str, quality: int = 95) -> None:
    """保存图像到文件"""
    img = Image.fromarray(image)

    ext = os.path.splitext(path)[1].lower()
    if ext in [".jpg", ".jpeg"]:
        img.save(path, "JPEG", quality=quality)
    elif ext == ".webp":
        img.save(path, "WEBP", quality=quality)
    else:
        img.save(path, "PNG")


def image_to_base64(image: np.ndarray, format: str = "PNG") -> str:
    """将图像转换为 Base64 编码"""
    img = Image.fromarray(image)
    buffer = BytesIO()

    if format.upper() == "JPEG":
        img.save(buffer, format="JPEG", quality=95)
    elif format.upper() == "WEBP":
        img.save(buffer, format="WEBP", quality=95)
    else:
        img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


# ============================================================================
# 主处理函数
# ============================================================================

def process_image(
    input_path: Optional[str] = None,
    input_base64: Optional[str] = None,
    output_path: Optional[str] = None,
    output_format: str = "PNG",
    template_paths: Optional[Dict[int, str]] = None
) -> ProcessResult:
    """
    处理图像，检测并移除水印

    Args:
        input_path: 输入图像文件路径
        input_base64: 输入图像的 Base64 编码
        output_path: 输出图像文件路径（可选）
        output_format: 输出格式 (PNG/JPEG/WEBP)
        template_paths: 自定义模板路径

    Returns:
        ProcessResult: 处理结果
    """
    try:
        # 加载输入图像
        if input_path:
            if not os.path.exists(input_path):
                return ProcessResult(
                    success=False,
                    watermark_detected=False,
                    message=f"输入文件不存在: {input_path}"
                )
            image = load_image_from_path(input_path)
        elif input_base64:
            image = load_image_from_base64(input_base64)
        else:
            return ProcessResult(
                success=False,
                watermark_detected=False,
                message="必须提供 input_path 或 input_base64"
            )

        # 加载水印模板
        templates = load_templates(template_paths)
        if not templates:
            return ProcessResult(
                success=False,
                watermark_detected=False,
                message="无法加载水印模板文件"
            )

        # 检测水印
        detection = detect_watermark(image, templates)

        if not detection.detected:
            return ProcessResult(
                success=True,
                watermark_detected=False,
                message="未检测到水印",
                output_base64=image_to_base64(image, output_format) if not output_path else None,
                detection_info={
                    "detected": False,
                    "confidence": detection.confidence
                }
            )

        # 移除水印
        template = templates[detection.size]
        result_image = remove_watermark(image, detection, template)

        # 输出结果
        result = ProcessResult(
            success=True,
            watermark_detected=True,
            message=f"成功移除 {detection.size}x{detection.size} 水印",
            detection_info={
                "detected": True,
                "x": detection.x,
                "y": detection.y,
                "size": detection.size,
                "confidence": float(detection.confidence)
            }
        )

        if output_path:
            save_image_to_path(result_image, output_path)
            result.output_path = output_path
        else:
            result.output_base64 = image_to_base64(result_image, output_format)

        return result

    except Exception as e:
        return ProcessResult(
            success=False,
            watermark_detected=False,
            message=f"处理失败: {str(e)}"
        )


# ============================================================================
# n8n 适配接口
# ============================================================================

def process_for_n8n(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    n8n 专用接口

    输入格式:
    {
        "image": "<base64_encoded_image>",  # 必需
        "output_format": "PNG",              # 可选，默认 PNG
        "return_base64": true                # 可选，默认 true
    }

    或者使用文件路径:
    {
        "input_path": "/path/to/input.png",
        "output_path": "/path/to/output.png"  # 可选
    }

    输出格式:
    {
        "success": true,
        "watermark_detected": true,
        "message": "成功移除 96x96 水印",
        "image": "<base64_encoded_result>",  # 如果 return_base64=true
        "detection": {
            "detected": true,
            "x": 100,
            "y": 200,
            "size": 96,
            "confidence": 0.85
        }
    }
    """
    # 提取参数
    input_path = input_data.get("input_path")
    input_base64 = input_data.get("image") or input_data.get("input_base64")
    output_path = input_data.get("output_path")
    output_format = input_data.get("output_format", "PNG").upper()
    return_base64 = input_data.get("return_base64", True)

    # 处理图像
    result = process_image(
        input_path=input_path,
        input_base64=input_base64,
        output_path=output_path if not return_base64 else None,
        output_format=output_format
    )

    # 构建输出
    output = {
        "success": result.success,
        "watermark_detected": result.watermark_detected,
        "message": result.message,
        "detection": result.detection_info
    }

    if return_base64 and result.output_base64:
        output["image"] = result.output_base64

    if result.output_path:
        output["output_path"] = result.output_path

    return output


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Gemini 水印移除工具 - 移除 Gemini (nano banana) 生成图片中的 ✦ 水印"
    )

    parser.add_argument(
        "-i", "--input",
        required=True,
        help="输入图像文件路径"
    )

    parser.add_argument(
        "-o", "--output",
        help="输出图像文件路径（默认: 原文件名_nowm.png）"
    )

    parser.add_argument(
        "-f", "--format",
        choices=["PNG", "JPEG", "WEBP"],
        default="PNG",
        help="输出格式（默认: PNG）"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出结果"
    )

    parser.add_argument(
        "--base64",
        action="store_true",
        help="将输出图像作为 Base64 字符串输出"
    )

    args = parser.parse_args()

    # 确定输出路径
    if args.output:
        output_path = args.output
    elif args.base64:
        output_path = None
    else:
        base, ext = os.path.splitext(args.input)
        output_path = f"{base}_nowm{ext if ext else '.png'}"

    # 处理图像
    result = process_image(
        input_path=args.input,
        output_path=output_path,
        output_format=args.format
    )

    # 输出结果
    if args.json:
        output = {
            "success": result.success,
            "watermark_detected": result.watermark_detected,
            "message": result.message,
            "detection": result.detection_info
        }
        if result.output_path:
            output["output_path"] = result.output_path
        if args.base64 and result.output_base64:
            output["image"] = result.output_base64
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        if result.success:
            if result.watermark_detected:
                print(f"✓ {result.message}")
                if result.output_path:
                    print(f"  输出文件: {result.output_path}")
                if result.detection_info:
                    d = result.detection_info
                    print(f"  位置: ({d['x']}, {d['y']}), 置信度: {d['confidence']:.2%}")
            else:
                print(f"○ {result.message}")
        else:
            print(f"✗ {result.message}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
