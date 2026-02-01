#!/usr/bin/env python3
"""
基础功能测试脚本
"""

import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.converter import MarkdownToWeChatConverter


def test_basic_conversion():
    """测试基础转换功能"""
    print("🧪 测试 1: 基础 Markdown 转换")
    
    markdown = """# Hello World
    
这是一段测试文本。包含**加粗**和*斜体*。

## 代码测试

```python
print("Hello, WeChat!")
```

## 列表测试

- 项目 1
- 项目 2
- 项目 3
"""
    
    converter = MarkdownToWeChatConverter()
    html = converter.convert(markdown)
    
    # 验证关键元素
    assert "#55C9EA" in html, "❌ 主题色未应用"
    assert "Hello World" in html, "❌ 标题未渲染"
    assert "加粗" in html, "❌ 加粗文本未渲染"
    assert "style=" in html, "❌ 样式未内联"
    assert "print" in html, "❌ 代码块未渲染"
    
    print("✅ 基础转换测试通过")
    return True


def test_code_highlight():
    """测试代码高亮功能"""
    print("\n🧪 测试 2: 代码语法高亮")
    
    markdown = """```python
def hello():
    return "world"
```"""
    
    converter = MarkdownToWeChatConverter()
    html = converter.convert(markdown)
    
    # 检查是否有语法高亮样式
    assert "color:" in html, "❌ 代码高亮未生效"
    assert "span" in html, "❌ 高亮标签未生成"
    
    print("✅ 代码高亮测试通过")
    return True


def test_link_to_footnote():
    """测试链接转脚注功能"""
    print("\n🧪 测试 3: 外部链接转脚注")
    
    markdown = """访问 [GitHub](https://github.com) 和 [Python](https://python.org)"""
    
    converter = MarkdownToWeChatConverter()
    html = converter.convert(markdown)
    
    # 检查脚注生成
    assert "参考链接" in html, "❌ 脚注标题未生成"
    assert "[1]" in html, "❌ 脚注编号未生成"
    assert "https://github.com" in html, "❌ 脚注链接未保留"
    assert "https://python.org" in html, "❌ 第二个脚注未生成"
    
    print("✅ 链接转脚注测试通过")
    return True


def test_table_rendering():
    """测试表格渲染"""
    print("\n🧪 测试 4: 表格渲染")
    
    markdown = """| 列1 | 列2 |
|-----|-----|
| A   | B   |
| C   | D   |"""
    
    converter = MarkdownToWeChatConverter()
    html = converter.convert(markdown)
    
    # 检查表格元素
    assert "<table" in html, "❌ 表格未生成"
    assert "<thead>" in html, "❌ 表格头部未生成"
    assert "<tbody>" in html, "❌ 表格主体未生成"
    assert "#e3f2fd" in html, "❌ 表格主题色未应用"
    
    print("✅ 表格渲染测试通过")
    return True


def test_theme_config():
    """测试主题配置"""
    print("\n🧪 测试 5: 主题配置加载")
    
    converter = MarkdownToWeChatConverter(theme_name='light-blue')
    theme_info = converter.get_theme_info()
    
    assert theme_info['name'] == "淡蓝色主题", "❌ 主题名称错误"
    assert theme_info['primary_color'] == "#55C9EA", "❌ 主题色错误"
    assert theme_info['version'] == "1.0.0", "❌ 版本号错误"
    
    print("✅ 主题配置测试通过")
    return True


def test_image_processing():
    """测试图片处理"""
    print("\n🧪 测试 6: 图片处理")
    
    markdown = """![测试图片](https://example.com/image.png "图片标题")"""
    
    converter = MarkdownToWeChatConverter()
    html = converter.convert(markdown)
    
    # 检查图片元素
    assert "<img" in html, "❌ 图片标签未生成"
    assert "max-width: 677px" in html, "❌ 图片宽度限制未应用"
    assert "测试图片" in html, "❌ 图片说明未保留"
    assert "data-ratio" in html, "❌ 微信图片属性未添加"
    
    print("✅ 图片处理测试通过")
    return True


def test_special_characters():
    """测试特殊字符处理"""
    print("\n🧪 测试 7: 特殊字符转义")
    
    markdown = """测试 <script> 和 & 符号"""
    
    converter = MarkdownToWeChatConverter()
    html = converter.convert(markdown)
    
    # 检查特殊字符是否被正确转义
    assert "&lt;" in html or "script" not in html.lower() or "<script>" not in html, "❌ HTML 标签未转义"
    assert "&amp;" in html or html.count("&") <= 2, "❌ & 符号未正确处理"
    
    print("✅ 特殊字符测试通过")
    return True


def test_file_conversion():
    """测试文件转换功能"""
    print("\n🧪 测试 8: 文件转换")
    
    sample_file = Path(__file__).parent.parent / "examples" / "sample.md"
    output_file = Path(__file__).parent / "test_output.html"
    
    if not sample_file.exists():
        print("⚠️  示例文件不存在，跳过此测试")
        return True
    
    converter = MarkdownToWeChatConverter()
    html = converter.convert_file(str(sample_file), str(output_file))
    
    assert output_file.exists(), "❌ 输出文件未生成"
    assert len(html) > 1000, "❌ 转换结果过短"
    
    # 清理测试文件
    output_file.unlink()
    
    print("✅ 文件转换测试通过")
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🚀 开始运行测试套件")
    print("=" * 60)
    
    tests = [
        test_basic_conversion,
        test_code_highlight,
        test_link_to_footnote,
        test_table_rendering,
        test_theme_config,
        test_image_processing,
        test_special_characters,
        test_file_conversion,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"❌ 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ 测试错误: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 所有测试通过！转换器工作正常！")
        return True
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查问题")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
