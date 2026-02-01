#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 水印批量移除处理器
Batch Processor for Gemini Watermark Removal

此脚本作为 Cursor Skill 的入口，负责：
1. 解析用户输入（文件或文件夹路径）
2. 区分单文件和批量处理模式
3. 调用核心去水印脚本
4. 收集和展示处理结果
5. 生成详细的处理报告
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# 配置常量
# ============================================================================

# 获取 Skill 目录
SKILL_DIR = Path(__file__).parent.resolve()
LIB_DIR = SKILL_DIR / "lib"
CORE_SCRIPT = LIB_DIR / "remover.py"

# 支持的图片格式
SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.webp']

# 进度条字符
PROGRESS_CHARS = {
    'full': '█',
    'empty': '░',
    'length': 20
}


# ============================================================================
# 数据结构
# ============================================================================

class ProcessStatus(Enum):
    """处理状态枚举"""
    SUCCESS = "success"
    NO_WATERMARK = "no_watermark"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class FileResult:
    """单个文件的处理结果"""
    input_path: str
    output_path: Optional[str] = None
    status: ProcessStatus = ProcessStatus.SKIPPED
    message: str = ""
    watermark_size: int = 0
    confidence: float = 0.0
    elapsed_time: float = 0.0


@dataclass
class BatchStats:
    """批量处理统计"""
    total: int = 0
    success: int = 0
    no_watermark: int = 0
    failed: int = 0
    skipped: int = 0
    total_time: float = 0.0
    results: List[FileResult] = field(default_factory=list)


# ============================================================================
# 工具函数
# ============================================================================

def print_header(text: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_progress(current: int, total: int, prefix: str = "处理中"):
    """
    打印进度条
    
    [████████████████████] 100% (50/50) 处理中
    """
    percentage = int(current / total * 100) if total > 0 else 0
    filled = int(PROGRESS_CHARS['length'] * current / total) if total > 0 else 0
    bar = PROGRESS_CHARS['full'] * filled + PROGRESS_CHARS['empty'] * (PROGRESS_CHARS['length'] - filled)
    
    print(f"\r[{bar}] {percentage:3d}% ({current}/{total}) {prefix}", end='', flush=True)
    
    if current == total:
        print()  # 完成后换行


def validate_path(path: str) -> Tuple[bool, str, bool]:
    """
    验证路径
    
    Returns:
        (is_valid, absolute_path, is_directory)
    """
    try:
        p = Path(path).expanduser().resolve()
        
        if not p.exists():
            return False, str(p), False
        
        return True, str(p), p.is_dir()
        
    except Exception as e:
        return False, path, False


def scan_images(directory: Path) -> List[Path]:
    """
    扫描目录中的所有图片文件
    
    Returns:
        图片文件路径列表
    """
    images = []
    
    for fmt in SUPPORTED_FORMATS:
        images.extend(directory.glob(f"*{fmt}"))
        images.extend(directory.glob(f"*{fmt.upper()}"))
    
    # 去重并排序
    images = sorted(set(images))
    
    return images


def determine_output_path(input_path: Path, output_dir: Optional[Path] = None, 
                         is_batch: bool = False) -> Path:
    """
    确定输出路径
    
    Args:
        input_path: 输入文件路径
        output_dir: 自定义输出目录（可选）
        is_batch: 是否为批量处理
        
    Returns:
        输出文件路径
    """
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / input_path.name
    else:
        if is_batch:
            # 批量处理：使用 原目录_no_watermark
            output_dir = input_path.parent / f"{input_path.parent.name}_no_watermark"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / input_path.name
        else:
            # 单文件：使用 原文件名_no_watermark
            output_path = input_path.parent / f"{input_path.stem}_no_watermark{input_path.suffix}"
    
    return output_path


# ============================================================================
# 核心处理函数
# ============================================================================

def call_core_script(input_path: Path, output_path: Path) -> Tuple[bool, Dict]:
    """
    调用核心去水印脚本
    
    Returns:
        (success, result_data)
    """
    try:
        # 构建命令
        cmd = [
            sys.executable,
            str(CORE_SCRIPT),
            "-i", str(input_path),
            "-o", str(output_path),
            "--json"
        ]
        
        # 执行命令
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60秒超时
        )
        elapsed = time.time() - start_time
        
        # 解析输出
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                data['elapsed_time'] = elapsed
                return True, data
            except json.JSONDecodeError:
                return False, {
                    'success': False,
                    'message': '解析输出失败',
                    'elapsed_time': elapsed
                }
        else:
            return False, {
                'success': False,
                'message': result.stderr or '处理失败',
                'elapsed_time': elapsed
            }
            
    except subprocess.TimeoutExpired:
        return False, {
            'success': False,
            'message': '处理超时（60秒）',
            'elapsed_time': 60.0
        }
    except Exception as e:
        return False, {
            'success': False,
            'message': f'执行错误: {str(e)}',
            'elapsed_time': 0.0
        }


def process_single_file(input_path: Path, output_path: Optional[Path] = None) -> FileResult:
    """
    处理单个文件
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径（可选）
        
    Returns:
        FileResult: 处理结果
    """
    # 确定输出路径
    if not output_path:
        output_path = determine_output_path(input_path, is_batch=False)
    
    # 调用核心脚本
    success, data = call_core_script(input_path, output_path)
    
    # 解析结果
    result = FileResult(
        input_path=str(input_path),
        output_path=str(output_path) if success else None,
        elapsed_time=data.get('elapsed_time', 0.0)
    )
    
    if success and data.get('success'):
        if data.get('watermark_detected'):
            result.status = ProcessStatus.SUCCESS
            result.message = data.get('message', '成功移除水印')
            
            # 提取检测信息
            detection = data.get('detection', {})
            result.watermark_size = detection.get('size', 0)
            result.confidence = detection.get('confidence', 0.0)
        else:
            result.status = ProcessStatus.NO_WATERMARK
            result.message = '未检测到水印'
    else:
        result.status = ProcessStatus.FAILED
        result.message = data.get('message', '处理失败')
    
    return result


def process_batch(input_dir: Path, output_dir: Optional[Path] = None) -> BatchStats:
    """
    批量处理文件夹
    
    Args:
        input_dir: 输入文件夹路径
        output_dir: 输出文件夹路径（可选）
        
    Returns:
        BatchStats: 批量处理统计
    """
    stats = BatchStats()
    
    # 扫描图片
    images = scan_images(input_dir)
    stats.total = len(images)
    
    if stats.total == 0:
        print(f"\n⚠️  未找到图片文件（支持格式: {', '.join(SUPPORTED_FORMATS)}）")
        return stats
    
    print(f"\n📁 找到 {stats.total} 张图片，开始处理...\n")
    
    # 确定输出目录
    if not output_dir:
        output_dir = input_dir.parent / f"{input_dir.name}_no_watermark"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 处理每个文件
    start_time = time.time()
    
    for idx, img_path in enumerate(images, 1):
        # 更新进度
        print_progress(idx - 1, stats.total, f"处理中: {img_path.name}")
        
        # 处理文件
        output_path = output_dir / img_path.name
        result = process_single_file(img_path, output_path)
        
        # 统计
        stats.results.append(result)
        
        if result.status == ProcessStatus.SUCCESS:
            stats.success += 1
        elif result.status == ProcessStatus.NO_WATERMARK:
            stats.no_watermark += 1
        elif result.status == ProcessStatus.FAILED:
            stats.failed += 1
        else:
            stats.skipped += 1
    
    # 完成进度条
    print_progress(stats.total, stats.total, "完成")
    
    stats.total_time = time.time() - start_time
    
    return stats


# ============================================================================
# 结果展示
# ============================================================================

def display_single_result(result: FileResult):
    """显示单文件处理结果"""
    print()
    
    if result.status == ProcessStatus.SUCCESS:
        print(f"✅ 成功移除 {result.watermark_size}x{result.watermark_size} 水印！")
        print(f"  输入: {Path(result.input_path).name}")
        print(f"  输出: {result.output_path}")
        print(f"  置信度: {result.confidence:.2%}")
        print(f"  耗时: {result.elapsed_time:.1f}秒")
    elif result.status == ProcessStatus.NO_WATERMARK:
        print(f"ℹ️  未检测到水印")
        print(f"  文件: {Path(result.input_path).name}")
        print(f"  说明: 图片可能不是 Gemini 生成的，或水印已被移除")
    else:
        print(f"❌ 处理失败")
        print(f"  文件: {Path(result.input_path).name}")
        print(f"  原因: {result.message}")


def display_batch_stats(stats: BatchStats, output_dir: Path):
    """显示批量处理统计"""
    print_header("📊 批量处理完成")
    
    print(f"\n统计信息:")
    print(f"  总文件数: {stats.total}")
    print(f"  成功处理: {stats.success} ✅")
    print(f"  未检测到水印: {stats.no_watermark} ○")
    print(f"  处理失败: {stats.failed} ❌")
    print(f"  总耗时: {stats.total_time:.1f}秒")
    print(f"  平均耗时: {stats.total_time / stats.total:.1f}秒/张" if stats.total > 0 else "")
    
    print(f"\n输出目录: {output_dir}")
    
    # 详细结果
    if stats.success > 0:
        print(f"\n✅ 成功处理的文件 ({stats.success}):")
        for result in stats.results:
            if result.status == ProcessStatus.SUCCESS:
                filename = Path(result.input_path).name
                print(f"  • {filename} → {result.watermark_size}x{result.watermark_size} (置信度: {result.confidence:.2%})")
    
    if stats.no_watermark > 0:
        print(f"\n○ 未检测到水印的文件 ({stats.no_watermark}):")
        for result in stats.results:
            if result.status == ProcessStatus.NO_WATERMARK:
                filename = Path(result.input_path).name
                print(f"  • {filename}")
    
    if stats.failed > 0:
        print(f"\n❌ 处理失败的文件 ({stats.failed}):")
        for result in stats.results:
            if result.status == ProcessStatus.FAILED:
                filename = Path(result.input_path).name
                print(f"  • {filename} - {result.message}")


# ============================================================================
# 主入口函数
# ============================================================================

def main():
    """主函数 - Cursor Skill 调用入口"""
    
    # 打印欢迎信息
    print_header("Gemini 水印批量移除工具 v1.0")
    
    # 解析命令行参数
    if len(sys.argv) < 2:
        print("\n❌ 错误: 请提供输入路径")
        print("\n使用方法:")
        print("  python batch_processor.py <input_path> [output_path]")
        print("\n示例:")
        print("  python batch_processor.py image.png")
        print("  python batch_processor.py ./images/")
        print("  python batch_processor.py image.png output.png")
        print("  python batch_processor.py ./images/ ./cleaned/")
        sys.exit(1)
    
    input_path_str = sys.argv[1]
    output_path_str = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 验证输入路径
    print(f"\n🔍 验证路径: {input_path_str}")
    is_valid, abs_path, is_dir = validate_path(input_path_str)
    
    if not is_valid:
        print(f"\n❌ 错误: 路径不存在")
        print(f"  路径: {abs_path}")
        sys.exit(1)
    
    input_path = Path(abs_path)
    output_path = Path(output_path_str).expanduser().resolve() if output_path_str else None
    
    print(f"✅ 路径有效")
    print(f"  类型: {'文件夹' if is_dir else '文件'}")
    print(f"  绝对路径: {input_path}")
    
    # 检查核心脚本
    if not CORE_SCRIPT.exists():
        print(f"\n❌ 错误: 核心脚本不存在")
        print(f"  期望路径: {CORE_SCRIPT}")
        print(f"  请确保 Skill 安装完整")
        sys.exit(1)
    
    # 处理
    try:
        if is_dir:
            # 批量处理
            stats = process_batch(input_path, output_path)
            
            # 显示结果
            output_dir = output_path or input_path.parent / f"{input_path.name}_no_watermark"
            display_batch_stats(stats, output_dir)
            
            # 返回状态码
            sys.exit(0 if stats.failed == 0 else 1)
            
        else:
            # 单文件处理
            print(f"\n🚀 开始处理...")
            result = process_single_file(input_path, output_path)
            
            # 显示结果
            display_single_result(result)
            
            # 返回状态码
            sys.exit(0 if result.status in [ProcessStatus.SUCCESS, ProcessStatus.NO_WATERMARK] else 1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
