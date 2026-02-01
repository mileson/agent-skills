"""
数学公式渲染模块 - 将 LaTeX 公式转换为图片 URL
用于微信公众号发布（不支持原生 LaTeX）
"""

import re
import urllib.parse
from typing import Tuple, List


class MathRenderer:
    """LaTeX 公式转图片渲染器"""

    # 公式服务提供商
    SERVICE_CODECOGS = "codecogs"
    SERVICE_ZHIHU = "zhihu"

    def __init__(self, service: str = SERVICE_CODECOGS):
        """
        初始化数学公式渲染器

        Args:
            service: 图片服务提供商
                - codecogs: CodeCogs (默认，稳定)
                - zhihu: 知乎图床 (中文支持好)
        """
        self.service = service
        self._processed_formulas = []  # 记录已处理的公式，避免重复处理

    def _get_codecogs_url(self, latex: str, display: bool = False) -> str:
        """
        使用 CodeCogs 服务生成公式图片 URL

        注意：CodeCogs 对中文支持不好，建议使用知乎服务

        Args:
            latex: LaTeX 公式（已去除 $$ 包裹）
            display: 是否为块级公式（影响大小）

        Returns:
            图片 URL
        """
        # 确保反斜杠正确处理
        latex = latex.replace('\\', '\\\\')

        # URL 编码（保留一些 LaTeX 特殊字符）
        encoded = urllib.parse.quote(latex, safe='\\{}$&#')

        # 构建图片 URL
        # 使用 \large 或 \LARGE 控制字体大小
        size = r"\LARGE" if display else r"\large"

        return f"https://latex.codecogs.com/png.latex?{size}%20{encoded}"

    def _get_jina_ai_url(self, latex: str, display: bool = False) -> str:
        """
        使用 Jina AI 的 LaTeX 渲染服务
        对中文支持良好，使用 MathJax 渲染

        Args:
            latex: LaTeX 公式（已去除 $$ 包裹）
            display: 是否为块级公式

        Returns:
            图片 URL
        """
        # 移除可能的 $$ 包裹
        latex = latex.strip().strip('$').strip()

        # 使用 SVG 格式，支持中文
        # URL 编码
        encoded = urllib.parse.quote(latex, safe='')

        if display:
            # 块级公式：使用独立的 SVG
            return f"https://latex.codecogs.com/svg.latex?\\LARGE%20{encoded}"
        else:
            # 行内公式
            return f"https://latex.codecogs.com/svg.latex?\\large%20{encoded}"

    def _get_zhihu_url(self, latex: str, display: bool = False) -> str:
        """
        使用知乎公式服务生成图片 URL
        知乎使用 MathJax，对中文支持良好

        Args:
            latex: LaTeX 公式（已去除 $$ 包裹）
            display: 是否为块级公式

        Returns:
            图片 URL
        """
        # 不需要转义反斜杠，知乎服务会正确处理
        # URL 编码
        encoded = urllib.parse.quote(latex, safe='')

        # 知乎公式 API
        return f"https://www.zhihu.com/equation?tex={encoded}"

    def get_formula_url(self, latex: str, display: bool = False) -> str:
        """
        获取公式图片 URL

        Args:
            latex: LaTeX 公式（可能包含 $$ 或 $ 包裹）
            display: 是否为块级公式（独立一行）

        Returns:
            公式图片 URL
        """
        # 移除 $ 和 $$ 包裹
        clean_latex = latex.strip().strip('$').strip()

        if self.service == self.SERVICE_CODECOGS:
            return self._get_codecogs_url(clean_latex, display)
        else:  # 默认使用知乎（支持中文）
            return self._get_zhihu_url(clean_latex, display)

    def render_inline_formula(self, latex: str) -> str:
        """
        渲染行内公式为 HTML <img> 标签

        Args:
            latex: LaTeX 公式（不含 $ 包裹）

        Returns:
            HTML img 标签
        """
        url = self.get_formula_url(latex, display=False)

        # 行内公式样式 - 垂直对齐并调整大小
        style = (
            "display: inline-block; "
            "vertical-align: middle; "
            "max-height: 1.5em; "
            "margin: 0 2px;"
        )

        # 添加特殊标记防止重复处理
        marker = f"_FORMULA_{len(self._processed_formulas)}_"
        self._processed_formulas.append(latex)

        return f'<img src="{url}" alt="{latex}" style="{style}" />{marker}'

    def render_block_formula(self, latex: str) -> str:
        """
        渲染块级公式为 HTML（图片居中）

        Args:
            latex: LaTeX 公式（不含 $$ 包裹）

        Returns:
            完整的 HTML 结构
        """
        url = self.get_formula_url(latex, display=True)

        # 块级公式容器样式
        container_style = (
            "text-align: center; "
            "margin: 18px 0; "
            "padding: 12px; "
            "background-color: #F7F8FA; "
            "border-radius: 8px; "
        )

        # 图片样式
        img_style = (
            "max-width: 100%; "
            "height: auto; "
            "display: block; "
            "margin: 0 auto; "
        )

        # 添加特殊标记防止重复处理
        marker = f"_FORMULA_{len(self._processed_formulas)}_"
        self._processed_formulas.append(latex)

        img_tag = f'<img src="{url}" alt="{latex}" style="{img_style}" />'
        return f'<p style="{container_style}">{img_tag}</p>\n{marker}'

    def convert_markdown_formulas(self, markdown: str) -> Tuple[str, int]:
        """
        将 Markdown 中的 LaTeX 公式转换为 HTML 图片标签

        处理两种格式：
        1. 块级公式：$$...$$ 独立一行
        2. 行内公式：$...$ 嵌入文本中

        策略：
        - 先提取所有公式标记位置
        - 从后往前替换，避免位置偏移

        Args:
            markdown: 原始 Markdown 文本

        Returns:
            (转换后的文本, 转换的公式数量)
        """
        result = markdown
        count = 0

        # 第一步：处理块级公式 $$...$$
        # 使用非贪婪匹配，支持跨行
        block_matches = list(re.finditer(r'\$\$([^\$]+?)\$\$', result, re.DOTALL))

        # 从后往前替换，避免位置偏移
        for match in reversed(block_matches):
            latex = match.group(1).strip()
            full_match = match.group(0)

            # 替换为 HTML
            replacement = self.render_block_formula(latex)
            result = result[:match.start()] + replacement + result[match.end():]
            count += 1

        # 第二步：处理行内公式 $...$
        # 匹配不包含换行的 $...$，避免误匹配美元符号
        # 使用更精确的模式：确保 $ 后面紧跟非空白字符
        inline_matches = list(re.finditer(r'\$([^\$\n]+?)\$', result))

        # 从后往前替换
        for match in reversed(inline_matches):
            latex = match.group(1).strip()

            # 跳过过短的匹配（避免误匹配价格等）
            if len(latex) <= 1 and latex[0] in '0123456789.,':
                continue

            # 跳过纯数字（可能是价格）
            if re.match(r'^[\d.,]+$', latex):
                continue

            full_match = match.group(0)
            replacement = self.render_inline_formula(latex)
            result = result[:match.start()] + replacement + result[match.end():]
            count += 1

        # 第三步：清理标记
        result = result.replace(f"_FORMULA_{len(self._processed_formulas)}_", "")
        result = re.sub(r'_FORMULA_\d+_', '', result)

        return result, count


def preprocess_markdown_with_formulas(
    markdown: str,
    service: str = MathRenderer.SERVICE_CODECOGS
) -> Tuple[str, int]:
    """
    预处理 Markdown，将 LaTeX 公式转换为图片标签

    这是主入口函数，在 Markdown 解析前调用

    Args:
        markdown: 原始 Markdown 文本
        service: 公式渲染服务

    Returns:
        (处理后的 Markdown, 转换的公式数量)
    """
    renderer = MathRenderer(service=service)
    return renderer.convert_markdown_formulas(markdown)


if __name__ == "__main__":
    # 测试用例
    test_md = """
# 数学公式测试

这是一个行内公式 $E=mc^2$ 的例子。

块级公式：

$$\\text{剩余分娩日龄占比} = 1 - \\frac{\\text{期初日期} - \\text{配种日期}}{\\text{妊娠天数}}$$

$$\\text{剩余死亡头数} = \\text{能繁母猪存栏} \\times \\text{剩余分娩死亡率}$$
"""

    result, count = preprocess_markdown_with_formulas(test_md)
    print(f"转换了 {count} 个公式")
    print(result)
