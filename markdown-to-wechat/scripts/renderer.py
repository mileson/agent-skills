"""
自定义 Mistune 渲染器，专门为微信公众号优化
"""

import mistune
from mistune.util import escape
from typing import Optional, List, Dict, Any
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


class WeChatRenderer(mistune.HTMLRenderer):
    """微信公众号专用 HTML 渲染器"""
    
    def __init__(self, theme_config: Dict[str, Any]):
        super().__init__()
        self.theme = theme_config
        self._custom_footnotes: List[Dict[str, str]] = []
        self.heading_ids = set()
        
        # 标题自动编号计数器
        self.h2_counter = 0
        self.h3_counter = 0
        self.h4_counter = 0
        
        # 颜色快捷访问
        self.c = theme_config['colors']
        # 排版快捷访问
        self.t = theme_config['typography']
        # 间距快捷访问
        self.s = theme_config['spacing']
    
    def heading(self, text: str, level: int, **attrs) -> str:
        """渲染标题，支持自动编号和渐变条装饰
        
        自动编号逻辑：
        - H1：不编号（标题页）
        - H2：递增编号 1, 2, 3...
        - H3：层级编号 1.1, 1.2, 2.1...
        - H4：层级编号 1.1.1, 1.1.2, 2.1.1...
        - 编号是新生成的，不从原标题内容中提取
        - 原标题文字完整保留
        """
        font_size_key = f'font_size_h{min(level, 4)}'
        font_size = self.t.get(font_size_key, self.t['font_size_base'])
        
        # 自动生成编号（不从标题内容中提取，标题文字完整保留）
        auto_number = None
        if level == 2:
            self.h2_counter += 1
            self.h3_counter = 0  # 新 H2 时重置 H3/H4 计数
            self.h4_counter = 0
            auto_number = f"{self.h2_counter}"
        elif level == 3:
            self.h3_counter += 1
            self.h4_counter = 0  # 新 H3 时重置 H4 计数
            if self.h2_counter > 0:
                auto_number = f"{self.h2_counter}.{self.h3_counter}"
            else:
                auto_number = f"{self.h3_counter}"
        elif level == 4:
            self.h4_counter += 1
            if self.h2_counter > 0 and self.h3_counter > 0:
                auto_number = f"{self.h2_counter}.{self.h3_counter}.{self.h4_counter}"
            elif self.h3_counter > 0:
                auto_number = f"{self.h3_counter}.{self.h4_counter}"
            else:
                auto_number = f"{self.h4_counter}"
        
        # 构建带样式的序号 + 原始标题文字
        if auto_number:
            if level == 2:
                # H2 序号增大 50%，添加斜体
                number_font_size = int(font_size * 1.5)
                number_style = (
                    f"color: {self.c.get('heading_number_color', self.c['primary'])}; "
                    f"margin-right: 8px; "
                    f"font-size: {number_font_size}px; "
                    f"font-style: italic; "
                )
            else:
                # H3+ 序号和标题字号一致，添加斜体
                number_style = (
                    f"color: {self.c.get('heading_number_color', self.c['primary'])}; "
                    f"margin-right: 8px; "
                    f"font-style: italic; "
                )
            styled_text = f'<span style="{number_style}">{auto_number}</span>{text}'
        else:
            styled_text = text
        
        border_radius = self.theme.get('border_radius', {}).get('medium', 8)
        
        if level == 1:
            # H1：居中显示，蓝色斜杠装饰，不显示序号
            # 使用 <p> + <span> 而非 <h1>，确保微信兼容
            title_only = text
            
            # 蓝色斜杠颜色
            slash_color = self.c.get('primary', '#1E6FBA')
            
            # P 标签样式
            p_style = (
                f"margin: 20px; "
                f"max-width: 100%; "
                f"min-height: 1em; "
                f"white-space: pre-wrap; "
                f"color: #000; "
                f"text-align: center; "
                f"line-height: 1.5; "
                f"box-sizing: border-box !important; "
                f"word-wrap: break-word !important; "
            )
            
            # 外层 span 样式
            outer_span_style = (
                f"max-width: 100%; "
                f"color: rgb(62, 62, 62); "
                f"line-height: 25.6px; "
                f"min-height: 1em; "
                f"box-sizing: border-box !important; "
                f"word-wrap: break-word !important; "
            )
            
            # 中层 span 样式
            mid_span_style = (
                f"max-width: 100%; "
                f"font-size: {font_size}px; "
                f"box-sizing: border-box !important; "
                f"word-wrap: break-word !important; "
            )
            
            # 内层 span 样式
            inner_span_style = (
                f"max-width: 100%; "
                f"color: rgb(62, 62, 62); "
                f"box-sizing: border-box !important; "
                f"word-wrap: break-word !important; "
                f"font-family: PingfangSC-Ultralight, sans-serif; "
            )
            
            # 斜杠样式 - 单个字符时增大 30%，否则增大 20%
            if len(title_only) == 1:
                slash_font_size = int(font_size * 1.3)
            else:
                slash_font_size = int(font_size * 1.2)
            slash_style = f"color: {slash_color}; font-size: {slash_font_size}px;"
            
            # 构建 HTML
            h1_html = f'<p style="{p_style}"><span style="{outer_span_style}"><span style="{mid_span_style}"><span style="{inner_span_style}"><strong style="{slash_style}">/ </strong>{title_only}<strong style="{slash_style}"> /</strong></span></span></span></p>\n'
            
            return h1_html
            
        elif level == 2:
            # H2：渐变条装饰（左深右浅，圆角）
            h2_style = (
                f"color: {self.c['text_primary']}; "
                f"font-size: {font_size}px; "
                f"line-height: {self.t['line_height_heading']}; "
                f"font-weight: bold; "
                f"letter-spacing: {self.t['letter_spacing_heading']}px; "
                f"margin: {self.s['element_margin'] * 1.5}px 0 8px 0; "  # 减小底部间距
            )
            
            # 渐变条样式（左深右浅）
            bar_color_start = self.c.get('heading_bar_start', '#0D9488')  # 深青色
            bar_color_end = self.c.get('heading_bar_end', '#5EEAD4')      # 浅青色
            
            bar_style = (
                f"height: 4px; "
                f"background: linear-gradient(to right, {bar_color_start}, {bar_color_end}); "
                f"border-radius: {border_radius}px; "
                f"margin: 8px 0 {self.s['element_margin']}px 0; "
            )
            
            # 返回标题 + 渐变条（使用 section 而非 div，微信兼容性更好）
            return f'<h{level} style="{h2_style}">{styled_text}</h{level}><section style="{bar_style}"></section>\n'
            
        elif level >= 3:
            # H3-H6：渐变条装饰（和 H2 一样，但高度递减）
            heading_style = (
                f"color: {self.c['text_primary']}; "
                f"font-size: {font_size}px; "
                f"line-height: {self.t['line_height_heading']}; "
                f"font-weight: bold; "
                f"letter-spacing: {self.t['letter_spacing_heading']}px; "
                f"margin: {self.s['element_margin']}px 0 8px 0; "
            )
            
            # 渐变条样式（左深右浅，两侧圆角）
            bar_color_start = self.c.get('heading_bar_start', '#0D9488')
            bar_color_end = self.c.get('heading_bar_end', '#5EEAD4')
            
            # 根据级别设置条的高度和宽度
            bar_heights = {
                3: 3,  # H3: 3px
                4: 2,  # H4: 2px
                5: 2,  # H5: 2px
                6: 1,  # H6: 1px
            }
            bar_widths = {
                3: 80,  # H3: 80px
                4: 60,  # H4: 60px
                5: 50,  # H5: 50px
                6: 40,  # H6: 40px
            }
            bar_height = bar_heights.get(level, 2)
            bar_width = bar_widths.get(level, 60)
            
            bar_style = (
                f"height: {bar_height}px; "
                f"width: {bar_width}px; "  # 固定宽度
                f"background: linear-gradient(to right, {bar_color_start}, {bar_color_end}); "
                f"border-radius: {border_radius}px; "
                f"margin: 8px 0 {self.s['element_margin']}px 0; "
            )
            
            # 返回标题 + 渐变条（使用 section 而非 div，微信兼容性更好）
            return f'<h{level} style="{heading_style}">{styled_text}</h{level}><section style="{bar_style}"></section>\n'
    
    def paragraph(self, text: str) -> str:
        """渲染段落，优化阅读体验"""
        style = (
            f"color: {self.c['text_primary']}; "
            f"font-family: {self.t['font_family']}; "
            f"font-size: {self.t['font_size_base']}px; "
            f"line-height: {self.t['line_height']}; "
            f"letter-spacing: {self.t['letter_spacing']}px; "
            f"margin: {self.t['paragraph_spacing']}px 0; "
            f"text-align: justify; "  # 两端对齐
            f"text-indent: {self.t['text_indent']}px; "
        )
        
        return f'<p style="{style}">{text}</p>\n'
    
    def block_code(self, code: str, info: Optional[str] = None) -> str:
        """渲染代码块，优化复制体验 - 使用 pre+code 标准组合"""
        lang = info.split()[0] if info else 'text'
        
        # 获取圆角配置
        border_radius = self.theme.get('border_radius', {}).get('code_block', 8)
        
        # pre 标签样式（外层容器）
        pre_style = (
            f"background-color: {self.c['bg_code']}; "
            f"border: 1px solid {self.c.get('code_border', '#E1E3E6')}; "
            f"border-radius: {border_radius}px; "
            f"padding: 16px; "
            f"margin: {self.s['element_margin']}px 0; "
            f"overflow-x: auto; "
            f"box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); "
            f"white-space: pre; "  # pre 标签核心：保留所有空格和换行
        )
        
        # code 标签样式（内层文本）
        code_style = (
            f"font-family: {self.t['font_family_code']}; "
            f"font-size: 13px; "
            f"line-height: 1.6; "
            f"color: {self.c['text_primary']}; "
        )
        
        # ✨ 微信公众号兼容方案：使用 HTML 实体保护引号
        # 微信编辑器会将直引号 " 转换为智能引号 ""
        # 使用 &quot; 实体可以防止这种转换
        code_content = code.rstrip('\n')
        
        # 🧹 移除 AppleScript 续行符 ¬，保留正常换行
        # 这样复制代码时不会带上特殊字符，可直接粘贴使用
        code_content = code_content.replace('¬', '')
        
        code_escaped = (code_content
                       .replace('&', '&amp;')      # 必须先转义 &
                       .replace('<', '&lt;')       # 转义 <
                       .replace('>', '&gt;')       # 转义 >
                       .replace('"', '&quot;'))    # 转义引号，防止微信转换
        # 注意：单引号 ' 保持原样，通常不会被微信修改
        
        # 使用 <pre><code> 标准组合
        # pre 标签确保浏览器和微信都能正确保留换行和空格
        # 使用 &quot; 防止微信编辑器将引号转换为智能引号
        return f'<pre style="{pre_style}"><code style="{code_style}">{code_escaped}</code></pre>\n'
    
    def codespan(self, text: str) -> str:
        """渲染行内代码"""
        style = (
            f"font-family: {self.t['font_family_code']}; "
            f"font-size: {self.t['font_size_code']}px; "
            f"color: {self.c['accent']}; "
            f"background-color: {self.c['bg_code']}; "
            f"padding: 2px 6px; "
            f"border-radius: 3px; "
        )
        
        return f'<code style="{style}">{escape(text)}</code>'
    
    def link(self, text: str, url: str, title: Optional[str] = None) -> str:
        """处理链接，外部链接转脚注或新窗口打开"""
        if self.theme['wechat_optimization']['link_to_footnote'] and url.startswith('http'):
            # 外部链接转脚注
            index = len(self._custom_footnotes) + 1
            self._custom_footnotes.append({
                'text': text,
                'url': url,
                'title': title or ''
            })
            
            link_style = f"color: {self.c['text_link']}; text-decoration: none;"
            sup_style = f"color: {self.c['primary']}; font-size: 0.8em;"
            
            return f'<span style="{link_style}">{text}<sup style="{sup_style}">[{index}]</sup></span>'
        else:
            # 链接保持原样
            link_style = f"color: {self.c['text_link']}; text-decoration: underline;"
            title_attr = f' title="{escape(title)}"' if title else ''
            
            # 外部链接在新窗口打开
            if url.startswith('http'):
                target_attr = ' target="_blank" rel="noopener noreferrer"'
            else:
                target_attr = ''
            
            return f'<a href="{escape(url)}"{title_attr}{target_attr} style="{link_style}">{text}</a>'
    
    def image(self, alt: str, url: str, title: Optional[str] = None) -> str:
        """处理图片，适配微信尺寸，优雅圆角"""
        max_width = self.theme['wechat_optimization']['max_image_width']
        border_radius = self.theme.get('border_radius', {}).get('image', 12)
        
        img_style = (
            f"max-width: {max_width}px; "
            f"width: 100%; "
            f"height: auto; "
            f"display: block; "
            f"margin: {self.s['element_margin']}px auto; "
            f"border-radius: {border_radius}px; "
            f"box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); "
        )
        
        # 图片说明样式
        caption_style = (
            f"text-align: center; "
            f"color: {self.c['text_secondary']}; "
            f"font-size: {self.t['font_size_small']}px; "
            f"margin-top: 8px; "
        )
        
        title_attr = f' title="{escape(title)}"' if title else ''
        alt_attr = f' alt="{escape(alt)}"' if alt else ''
        
        img_html = f'<img src="{escape(url)}"{alt_attr}{title_attr} style="{img_style}" />'
        
        # 如果有 alt 文本，添加图片说明
        if alt:
            return f'<figure style="margin: {self.s['element_margin']}px 0;">{img_html}<figcaption style="{caption_style}">{escape(alt)}</figcaption></figure>\n'
        
        return f'{img_html}\n'
    
    def block_quote(self, text: str) -> str:
        """渲染引用块，使用 linear-gradient 背景高亮"""
        import re

        # 移除内部段落标签的闭合标签，但保留换行信息
        text = text.replace('</p>', '<br/>')
        text = re.sub(r'<p[^>]*>', '', text)
        text = text.strip()

        # 高亮颜色（绿色系）
        highlight_bg = self.c.get('highlight_color', '#FF9800')

        # 外层容器样式
        container_style = (
            f"box-sizing: border-box; "
            f"margin-left: 35px; "
            f"margin-right: 35px; "
            f"padding: 10px; "
            f"color: #2b3835; "
            f"text-align: center; "
            f"box-sizing: border-box; "
            f"font-size: 18px; "
            f"font-family: PingfangSC-LIGHT, sans-serif; "
        )

        # Span 样式 - 使用 linear-gradient 实现高亮效果
        span_style = (
            f"background: linear-gradient(to bottom, rgb(255, 255, 254) 60%, rgba(255, 152, 0, 0.49) 40%); "
        )

        # 保留换行，将 <br/> 转换为实际换行的 HTML 结构
        # 使用 <p> 标签包裹每个段落，并应用高亮样式
        parts = text.split('<br/>')
        result_parts = []
        for part in parts:
            part = part.strip()
            if part:
                # 检查是否包含图片（公式）或斜体（注）
                if '<img' in part or '<em>' in part:
                    # 公式和注：单独成行，不应用高亮背景
                    p_style = (
                        f"box-sizing: border-box; "
                        f"margin-left: 35px; "
                        f"margin-right: 35px; "
                        f"padding: 10px; "
                        f"text-align: center; "
                        f"font-size: 18px; "
                        f"font-family: PingfangSC-LIGHT, sans-serif; "
                    )
                    result_parts.append(f'<p style="{p_style}">{part}</p>')
                else:
                    # 普通文字：应用高亮背景
                    result_parts.append(f'<p style="{container_style}"><span style="{span_style}">{part}</span></p>')

        return '\n'.join(result_parts) + '\n'
    
    def list(self, text: str, ordered: bool, **attrs) -> str:
        """渲染列表，蓝色序号/圆点"""
        tag = 'ol' if ordered else 'ul'
        list_style = "decimal" if ordered else "disc"
        
        # 使用主题色作为列表标记颜色
        list_marker_color = self.c.get('list_marker_color', self.c['primary'])
        
        style = (
            f"padding-left: {self.s['list_indent']}px; "
            f"margin: {self.s['element_margin']}px 0; "
            f"list-style-type: {list_style}; "
            f"color: {list_marker_color}; "  # 列表标记颜色（数字/圆点）
        )
        
        return f'<{tag} style="{style}">{text}</{tag}>\n'
    
    def list_item(self, text: str, **attrs) -> str:
        """渲染列表项，任务列表使用自定义 checkbox 样式"""
        import re
        
        # 检测任务列表标记
        is_task_list = False
        is_checked = False
        
        # 检测特殊标记
        if '{{TASK_CHECKED}}' in text:
            is_task_list = True
            is_checked = True
            # 移除标记
            text = text.replace('{{TASK_CHECKED}}', '').strip()
        elif '{{TASK_UNCHECKED}}' in text:
            is_task_list = True
            is_checked = False
            # 移除标记
            text = text.replace('{{TASK_UNCHECKED}}', '').strip()
        
        # 渲染任务列表
        if is_task_list:
            if is_checked:
                # 已勾选：绿色背景 + 白色 ✓
                checkbox = '<span style="display: inline-block; width: 16px; height: 16px; background: #10B981; border: 1.5px solid #10B981; border-radius: 3px; margin-right: 8px; vertical-align: middle; color: #fff; font-size: 12px; line-height: 14px; text-align: center; font-weight: bold;">✓</span>'
            else:
                # 未勾选：灰色边框方框
                checkbox = '<span style="display: inline-block; width: 16px; height: 16px; border: 1.5px solid #D1D5DB; background: #fff; border-radius: 3px; margin-right: 8px; vertical-align: middle;"></span>'
            
            # 列表项样式（任务列表不显示列表标记）
            li_style = (
                f"font-size: {self.t['font_size_base']}px; "
                f"line-height: {self.t['line_height']}; "
                f"margin: 6px 0; "
                f"list-style: none; "
            )
            
            # 将文字内容用 span 包裹，设置为深色
            text_style = f"color: {self.c['text_primary']};"
            wrapped_text = f'<span style="{text_style}">{checkbox}{text}</span>'
            
            return f'<li style="{li_style}">{wrapped_text}</li>\n'
        else:
            # 普通列表项
            li_style = (
                f"font-size: {self.t['font_size_base']}px; "
                f"line-height: {self.t['line_height']}; "
                f"margin: 6px 0; "
            )
            
            # 将文字内容用 span 包裹，设置为深色
            text_style = f"color: {self.c['text_primary']};"
            wrapped_text = f'<span style="{text_style}">{text}</span>'
            
            return f'<li style="{li_style}">{wrapped_text}</li>\n'
    
    def strong(self, text: str) -> str:
        """加粗文本 - 淡橙色背景高亮效果（类似划线重点）"""
        import re
        
        # 检测是否为 "数字. 文字" 格式（模拟有序列表）
        match = re.match(r'^(\d+\.\s+)(.+)$', text)
        
        if match:
            # 序号部分设置为蓝色，文字部分保持黑色
            number = match.group(1)  # "1. "
            content = match.group(2)  # "优先选择iOS平台"
            
            number_style = f"color: {self.c.get('list_marker_color', self.c['primary'])}; font-weight: bold;"
            content_style = (
                f"font-weight: bold; "
                f"color: {self.c['text_primary']}; "
                f"background: linear-gradient(to bottom, transparent 60%, {self.c.get('highlight_bg', '#FFF3E0')} 60%); "
                f"padding: 2px 4px; "
                f"border-radius: 2px; "
            )
            
            return f'<strong style="{number_style}">{number}</strong><strong style="{content_style}">{content}</strong>'
        else:
            # 普通加粗文本
            style = (
                f"font-weight: bold; "
                f"color: {self.c['text_primary']}; "
                f"background: linear-gradient(to bottom, transparent 60%, {self.c.get('highlight_bg', '#FFF3E0')} 60%); "
                f"padding: 2px 4px; "
                f"border-radius: 2px; "
            )
            return f'<strong style="{style}">{text}</strong>'
    
    def emphasis(self, text: str) -> str:
        """斜体文本"""
        style = f"font-style: italic; color: {self.c['text_primary']};"
        return f'<em style="{style}">{text}</em>'
    
    def strikethrough(self, text: str) -> str:
        """删除线文本 - 灰色实线删除线"""
        style = (
            f"text-decoration: line-through solid #828e9f; "
            f"text-decoration-thickness: 2px; "
            f"color: #828e9f; "
        )
        return f'<span style="{style}">{text}</span>'
    
    def table(self, text: str) -> str:
        """渲染表格，简约风格，细边框"""
        border_radius = self.theme.get('border_radius', {}).get('table', 6)
        
        table_style = (
            f"width: 100%; "
            f"border-collapse: separate; "
            f"border-spacing: 0; "
            f"margin: {self.s['element_margin']}px 0; "
            f"font-size: {self.t['font_size_base']}px; "
            f"border: 0.5px solid {self.c.get('table_border', '#E5E7EB')}; "  # 更细的外边框
            f"border-radius: {border_radius}px; "
            f"overflow: hidden; "
        )
        
        return f'<table style="{table_style}">{text}</table>\n'
    
    def table_head(self, text: str) -> str:
        """表格头部"""
        return f'<thead>{text}</thead>'
    
    def table_body(self, text: str) -> str:
        """表格主体"""
        return f'<tbody>{text}</tbody>'
    
    def table_row(self, text: str) -> str:
        """表格行"""
        return f'<tr>{text}</tr>\n'
    
    def table_cell(self, text: str, align: Optional[str] = None, head: bool = False) -> str:
        """表格单元格，简约淡灰风格，细边框"""
        tag = 'th' if head else 'td'
        
        # 基础样式 - 细边框
        cell_style = (
            f"padding: {self.s['table_cell_padding']}px {self.s['table_cell_padding'] + 4}px; "
            f"border: 0.5px solid {self.c.get('table_border', '#E5E7EB')}; "  # 更细的边框
            f"text-align: {align or 'left'}; "
            f"color: {self.c['text_primary']}; "
        )
        
        # 表头：灰色背景
        if head:
            cell_style += (
                f"font-weight: 500; "
                f"background-color: {self.c.get('table_header_bg', '#F3F4F6')}; "  # 灰色表头
            )
        else:
            # 内容单元格：白色背景
            cell_style += (
                f"background-color: #ffffff; "  # 白色背景
            )
        
        return f'<{tag} style="{cell_style}">{text}</{tag}>'
    
    def thematic_break(self) -> str:
        """水平分隔线，细灰线"""
        style = (
            f"border: none; "
            f"border-top: 1px solid {self.c.get('divider_color', '#E5E7EB')}; "  # 细线（1px）
            f"margin: {self.s['section_margin']}px 0; "
        )
        
        return f'<hr style="{style}" />\n'
    
    def generate_footnotes(self) -> str:
        """生成脚注区域"""
        if not self._custom_footnotes:
            return ''
        
        section_style = (
            f"margin-top: {self.s['section_margin'] + 8}px; "
            f"padding-top: {self.s['element_margin'] + 4}px; "
            f"border-top: 1px solid {self.c['border_light']}; "
        )
        
        title_style = (
            f"color: {self.c['text_secondary']}; "
            f"font-size: {self.t['font_size_small']}px; "
            f"font-weight: bold; "
            f"margin-bottom: {self.s['element_margin'] // 2}px; "
        )
        
        footnote_html = f'<section style="{section_style}">\n'
        footnote_html += f'<h4 style="{title_style}">📎 参考链接</h4>\n'
        
        for i, note in enumerate(self._custom_footnotes, 1):
            item_style = (
                f"color: {self.c['text_secondary']}; "
                f"font-size: {self.t['font_size_footnote']}px; "
                f"line-height: 1.6; "
                f"margin: 6px 0; "
                f"word-break: break-all; "
            )
            
            index_style = f"color: {self.c['primary']}; font-weight: bold;"
            link_style = f"color: {self.c['text_link']};"
            
            footnote_html += (
                f'<p style="{item_style}">'
                f'<span style="{index_style}">[{i}]</span> '
                f'{escape(note["text"])}: '
                f'<span style="{link_style}">{escape(note["url"])}</span>'
                f'</p>\n'
            )
        
        footnote_html += '</section>\n'
        return footnote_html
