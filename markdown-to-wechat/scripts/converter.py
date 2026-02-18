"""
主转换器：Markdown -> 微信公众号 HTML
"""

import mistune
import yaml
import re
from pathlib import Path
from typing import Optional
from premailer import transform
from .renderer import WeChatRenderer
from .wechat_compat import WeChatCompatProcessor
from .math_renderer import preprocess_markdown_with_formulas, MathRenderer


class MarkdownToWeChatConverter:
    """Markdown 转微信公众号格式转换器"""
    
    def __init__(self, theme_name: str = 'light-blue', math_service: str = MathRenderer.SERVICE_ZHIHU):
        """
        初始化转换器

        Args:
            theme_name: 主题名称，默认为 'light-blue'
            math_service: 数学公式渲染服务（'zhihu' 支持中文，'codecogs' 对中文支持差）
        """
        self.theme_name = theme_name
        self.theme_config = self._load_theme(theme_name)
        self.author_config = self._load_author_config()
        self.math_service = math_service
        self.renderer = WeChatRenderer(self.theme_config)
        
        # 配置 mistune 插件
        plugins = []
        features = self.theme_config.get('features', {})
        
        if features.get('enable_strikethrough', True):
            plugins.append('strikethrough')
        if features.get('enable_tables', True):
            plugins.append('table')
        # 注意：我们不使用 mistune 的 task_lists 插件，
        # 因为它生成的 checkbox 在微信中不支持
        # 我们在渲染后手动处理任务列表
        if features.get('enable_footnotes', False):
            plugins.append('footnotes')
        
        # 创建 markdown 解析器
        self.markdown = mistune.create_markdown(
            renderer=self.renderer,
            plugins=plugins
        )
        
        # 微信兼容处理器
        self.compat_processor = WeChatCompatProcessor(self.theme_config)
    
    def _load_theme(self, theme_name: str) -> dict:
        """
        加载主题配置
        
        Args:
            theme_name: 主题名称
            
        Returns:
            主题配置字典
        """
        # 获取当前文件的父目录的父目录（skill 根目录）
        skill_root = Path(__file__).parent.parent
        theme_path = skill_root / 'templates' / theme_name / 'theme.yaml'
        
        if not theme_path.exists():
            raise FileNotFoundError(f"主题配置文件不存在: {theme_path}")
        
        with open(theme_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def _load_author_config(self) -> dict:
        """
        加载作者配置
        
        Returns:
            作者配置字典
        """
        skill_root = Path(__file__).parent.parent
        author_config_path = skill_root / 'templates' / 'author_config.yaml'
        
        if not author_config_path.exists():
            # 如果配置文件不存在，返回默认配置
            return {
                'author': {'name': '作者', 'avatar_url': ''},
                'reading_time': {'enabled': False},
                'header_style': {'enabled': False}
            }
        
        with open(author_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def _count_words(self, markdown_text: str) -> int:
        """
        统计 Markdown 文本的字数（中文按字计，英文按词计）
        
        Args:
            markdown_text: Markdown 文本
            
        Returns:
            字数
        """
        # 移除 Markdown 标记
        text = re.sub(r'```[\s\S]*?```', '', markdown_text)  # 删除代码块
        text = re.sub(r'`[^`]+`', '', text)  # 删除行内代码
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # 删除图片
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)  # 删除链接
        text = re.sub(r'[#*_~\[\]()>-]', '', text)  # 删除 Markdown 符号
        
        # 统计中文字符数
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        
        # 统计英文单词数（以空格分隔）
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        
        # 总字数 = 中文字符 + 英文单词
        total_words = chinese_chars + english_words
        
        return total_words
    
    def _calculate_reading_time(self, word_count: int) -> dict:
        """
        根据字数计算阅读时间
        
        Args:
            word_count: 字数
            
        Returns:
            {'normal': 正常阅读分钟数, 'fast': 快速阅读分钟数}
        """
        reading_config = self.author_config.get('reading_time', {})
        normal_speed = reading_config.get('normal_speed', 300)  # 默认 300 字/分钟
        fast_speed = reading_config.get('fast_speed', 600)  # 默认 600 字/分钟
        
        normal_time = max(1, round(word_count / normal_speed))  # 至少1分钟
        fast_time = max(1, round(word_count / fast_speed))  # 至少1分钟
        
        return {
            'normal': normal_time,
            'fast': fast_time
        }
    
    def _generate_article_header(self, word_count: int) -> str:
        """
        生成文章头部 HTML（作者信息 + 阅读时间）
        
        Args:
            word_count: 文章字数
            
        Returns:
            文章头部 HTML
        """
        header_config = self.author_config.get('header_style', {})
        
        # 如果未启用文章头部，返回空字符串
        if not header_config.get('enabled', True):
            return ''
        
        author = self.author_config.get('author', {})
        reading_config = self.author_config.get('reading_time', {})
        
        # 计算阅读时间
        reading_time = self._calculate_reading_time(word_count)
        
        # 作者信息
        author_name = author.get('name', '作者')
        avatar_url = author.get('avatar_url', '')
        avatar_size = header_config.get('avatar_size', 80)
        avatar_radius = header_config.get('avatar_radius', 40)
        
        # 阅读时间样式
        card_bg = header_config.get('card_bg', '#F0F9FF')
        card_border = header_config.get('card_border', '#7DD3FC')
        card_text_color = header_config.get('card_text_color', '#0284C7')
        card_number_color = header_config.get('card_number_color', '#0369A1')
        divider_color = header_config.get('divider_color', '#E5E7EB')
        
        # 阅读时间文本
        label_normal = reading_config.get('label_normal', '读完需要')
        label_fast = reading_config.get('label_fast', '速读仅需')
        unit = reading_config.get('unit', '分钟')
        
        # 🎨 微信公众号预览宽度适配方案（微信预览容器宽度为 375px）
        # 使用 max-width: 340px 确保在微信预览中左右内容都能完整显示
        # 参考开源项目 doocs/md 和 lyricat/wechat-format 的最佳实践
        label_attr = 'label="Markdown to WeChat Converter"'
        header_html = f'''
<section {label_attr} style="box-sizing: border-box; margin: 16px auto 20px auto; max-width: 340px; width: 90%;"><section {label_attr} style="box-sizing: border-box; padding: 12px; overflow: hidden;"><section {label_attr} style="box-sizing: border-box; display: table; width: 100%; table-layout: fixed;"><section {label_attr} style="display: table-cell; width: 45%; vertical-align: middle; text-align: center; border-right: 1px solid #E0E0E0; padding-right: 8px;"><section style="box-sizing: border-box;"><section {label_attr} style="margin: 0 auto; box-sizing: border-box;"><section style="box-sizing: border-box; width: 60px; height: 60px; display: inline-block; overflow: hidden; border-radius: 50%; background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);"><img src="{avatar_url}" style="width: 100%; height: 100%; object-fit: cover; object-position: center; display: block;" /></section><p style="margin: 6px 0 0 0;"><span style="font-size: 13px; color: #333333; line-height: 1.5; font-family: PingfangSC-LIGHT,sans-serif;">{author_name}</span></p></section></section></section><section {label_attr} style="display: table-cell; width: 55%; vertical-align: middle; text-align: center; padding-left: 8px;"><section style="box-sizing: border-box; border: 1px solid #E5E7EB; padding: 8px 6px; width: 100%; max-width: 115px; border-radius: 6px; margin: 0 auto; background: #FFFFFF;"><p style="margin: 0; color: #0D9488; font-size: 12px;">读完需要</p><section style="font-size: 28px; color: #333333; line-height: 32px; font-weight: 600;">{reading_time['normal']}</section><span style="color: #0D9488; font-size: 12px;">分钟</span><p style="font-size: 10px; color: #999999; padding-top: 3px; margin: 0;">速读仅需 {reading_time['fast']} 分钟</p></section></section></section></section></section>
'''
        
        return header_html
    
    def convert(self, markdown_text: str) -> str:
        """
        转换 Markdown 文本为微信公众号 HTML

        Args:
            markdown_text: Markdown 文本

        Returns:
            微信公众号格式的 HTML
        """
        # 0. 统计字数（在处理前统计原始 Markdown）
        word_count = self._count_words(markdown_text)

        # 1. 预处理数学公式（必须在其他处理之前）
        markdown_text, formula_count = preprocess_markdown_with_formulas(
            markdown_text,
            service=self.math_service
        )
        if formula_count > 0:
            print(f"📐 已转换 {formula_count} 个数学公式为图片")

        # 2. 预处理：转换任务列表语法（标题编号由 renderer 自动生成）
        markdown_text = self._preprocess_task_lists(markdown_text)

        # 3. 生成文章头部
        article_header = self._generate_article_header(word_count)

        # 4. 解析 Markdown -> HTML
        html_content = self.markdown(markdown_text)

        # 5. 添加脚注（如果有外部链接）
        footnotes = self.renderer.generate_footnotes()
        html_content += footnotes

        # 6. 包装完整 HTML 文档（插入文章头部）
        full_html = self._wrap_html(article_header + html_content)

        # 7. CSS 内联优化（premailer 进一步处理）
        try:
            # premailer 可以处理一些遗漏的外部样式
            inlined_html = transform(
                full_html,
                strip_important=False,
                keep_style_tags=False,
                remove_classes=True
            )
        except Exception as e:
            # 如果 premailer 失败，使用原始 HTML
            print(f"警告: premailer 处理失败: {e}")
            inlined_html = full_html
        
        # 7. 微信兼容性处理
        final_html = self.compat_processor.process(inlined_html)
        
        return final_html
    
    def _add_heading_numbers(self, text: str) -> str:
        """
        为标题添加自动编号：## 标题 → 1 标题，### 标题 → 1.1 标题

        注意：如果标题已经包含数字序号（如 1.、1、1）、（1）等），则跳过添加

        Args:
            text: 原始 Markdown 文本

        Returns:
            添加编号后的文本
        """
        lines = text.split('\n')
        result = []

        # 计数器：[h1_count, h2_count, h3_count, h4_count, h5_count, h6_count]
        counters = [0, 0, 0, 0, 0, 0]

        # 检测标题是否已包含数字序号的正则表达式
        # 匹配格式：1. 或 1、或 1）或 (1) 或 纯数字+空格（仅限 1-3 位数字，避免误匹配如 "2000+"）
        has_number_pattern = re.compile(
            r'^(\d{1,3}\.\s+|[\（\(]\d+[\）\)]\s*|\d+[\、\）]\s*|\d{1,3}\s+(?!\S*[+\-\*\/]))'
        )

        for line in lines:
            # 匹配标题行
            match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if match:
                hashes = match.group(1)
                title_text = match.group(2)
                level = len(hashes)

                # H1 不编号，只编号 H2-H6
                if level == 1:
                    result.append(line)
                    # 重置所有计数器
                    counters = [0, 0, 0, 0, 0, 0]
                elif level >= 2:
                    # 检查标题是否已包含数字序号
                    if has_number_pattern.match(title_text):
                        # 已有序号，不添加，但需要更新计数器
                        # 尝试从标题中提取数字来更新计数器
                        num_match = re.match(r'^(\d+)', title_text)
                        if num_match:
                            counters[level - 1] = int(num_match.group(1))
                        else:
                            counters[level - 1] += 1

                        # 重置更深层级的计数器
                        for i in range(level, 6):
                            counters[i] = 0

                        result.append(line)
                    else:
                        # 无序号，添加编号
                        counters[level - 1] += 1

                        # 重置更深层级的计数器
                        for i in range(level, 6):
                            counters[i] = 0

                        # 生成编号
                        if level == 2:
                            # H2: 1, 2, 3...
                            number = str(counters[1])
                        else:
                            # H3+: 1.1, 1.2, 2.1, 2.2...
                            parent_numbers = [str(counters[i]) for i in range(1, level) if counters[i] > 0]
                            number = '.'.join(parent_numbers)

                        # 添加编号到标题
                        new_line = f'{hashes} {number} {title_text}'
                        result.append(new_line)
                else:
                    result.append(line)
            else:
                result.append(line)

        return '\n'.join(result)
    
    def _preprocess_task_lists(self, text: str) -> str:
        """
        预处理任务列表：将 [ ] 和 [x] 替换为特殊标记，稍后渲染为自定义 checkbox
        
        Args:
            text: 原始 Markdown 文本
            
        Returns:
            处理后的文本
        """
        lines = text.split('\n')
        result = []
        
        for line in lines:
            # 匹配任务列表项：- [ ] 或 - [x]
            match = re.match(r'^(\s*)[-*+]\s+\[([xX ])\]\s+(.*)', line)
            
            if match:
                indent = match.group(1)
                status = match.group(2)
                content = match.group(3)
                
                # 使用特殊标记（稍后在 list_item 中渲染为自定义 checkbox）
                if status.lower() == 'x':
                    marker = '{{TASK_CHECKED}}'
                else:
                    marker = '{{TASK_UNCHECKED}}'
                
                # 重构列表项
                new_line = f'{indent}- {marker} {content}'
                result.append(new_line)
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def _wrap_html(self, content: str) -> str:
        """
        包装完整 HTML 结构
        
        Args:
            content: HTML 内容
            
        Returns:
            完整的 HTML 文档
        """
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>微信公众号文章</title>
</head>
<body style="margin: 0; padding: 8px; background-color: #ffffff; font-family: {self.theme_config['typography']['font_family']};">
    <article style="max-width: 90%; margin: 0 auto;">
        {content}
    </article>
</body>
</html>'''
    
    def convert_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        从文件转换 Markdown
        
        Args:
            input_path: 输入的 Markdown 文件路径
            output_path: 输出的 HTML 文件路径（可选）
            
        Returns:
            转换后的 HTML 内容
        """
        # 读取文件
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
        
        # 转换
        html_content = self.convert(markdown_text)
        
        # 保存到文件（如果指定了输出路径）
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return html_content
    
    def get_theme_info(self) -> dict:
        """
        获取主题信息
        
        Returns:
            主题配置信息
        """
        return {
            'name': self.theme_config.get('name', self.theme_name),
            'description': self.theme_config.get('description', ''),
            'version': self.theme_config.get('version', '1.0.0'),
            'primary_color': self.theme_config['colors']['primary'],
        }
