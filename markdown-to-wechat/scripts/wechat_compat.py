"""
微信公众号兼容性处理器
"""

from bs4 import BeautifulSoup
from typing import Dict, Any


class WeChatCompatProcessor:
    """微信公众号兼容性处理器"""
    
    def __init__(self, theme_config: Dict[str, Any]):
        """
        初始化处理器
        
        Args:
            theme_config: 主题配置
        """
        self.config = theme_config.get('wechat_optimization', {})
    
    def process(self, html: str) -> str:
        """
        处理 HTML 使其兼容微信公众号
        
        Args:
            html: 原始 HTML
            
        Returns:
            处理后的 HTML
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. 移除不支持的标签
        if self.config.get('strip_javascript', True):
            self._remove_unsupported_tags(soup)
        
        # 2. 处理图片
        self._process_images(soup)
        
        # 3. 修复列表嵌套
        if self.config.get('fix_list_nesting', True):
            self._fix_list_nesting(soup)
        
        # 4. 移除 CSS 类（如果配置要求）
        if self.config.get('remove_classes', True):
            self._remove_classes(soup)
        
        # 5. 处理 SVG（如果有）
        self._process_svg(soup)
        
        # 6. 保护代码块中的引号（防止微信编辑器转换为智能引号）
        self._protect_code_quotes(soup)
        
        # 7. 提取内容（去掉外层包装）
        content = self._extract_content(soup)
        
        # 8. 后处理：将自闭合标签转换为非自闭合标签（微信兼容性）
        # 将 <br/> 改为 <br>，将 <br /> 改为 <br>
        content = content.replace('<br/>', '<br>').replace('<br />', '<br>')
        
        # 9. 后处理：修复头像 section 的格式（微信编辑器需要精确格式）
        import re
        
        # 步骤1：查找头像 section（包含 border-radius: 100% 和 background-image）
        def fix_avatar_section(match):
            section_tag = match.group(0)
            
            # 步骤2：将单引号改为双引号（微信要求）
            if section_tag.startswith("<section style='"):
                section_tag = section_tag.replace("<section style='", '<section style="', 1)
                # 找到 style 属性的结束位置（倒数第二个单引号）
                # 从后往前找，跳过 class="" 之后的内容
                parts = section_tag.rsplit("'", 1)
                if len(parts) == 2:
                    section_tag = parts[0] + '"' + parts[1]
            
            # 步骤3：将 url("...") 或 url(&quot;...&quot;) 转换为 url(...) - 完全移除引号
            # 微信编辑器需要这种格式
            # 处理 url(&quot;...&quot;) 格式
            pattern_url1 = r'background-image:\s*url\(&quot;([^&]*)&quot;\)'
            section_tag = re.sub(pattern_url1, r'background-image: url(\1)', section_tag)
            
            # 处理 url("...") 格式
            pattern_url2 = r'background-image:\s*url\("([^"]*)"\)'
            section_tag = re.sub(pattern_url2, r'background-image: url(\1)', section_tag)
            
            # 步骤4：将 URL 中的 & 转换为 &amp;（HTML 实体编码）
            # 查找 url(...) 并替换其中的 &
            def encode_url_ampersand(m):
                url_with_bg = m.group(0)
                # 只替换 URL 部分的 &，不替换已经是 &amp; 的部分
                url_with_bg = url_with_bg.replace('&', '&amp;')
                url_with_bg = url_with_bg.replace('&amp;amp;', '&amp;')  # 避免重复编码
                return url_with_bg
            
            pattern_url_encode = r'background-image:\s*url\([^)]*\)'
            section_tag = re.sub(pattern_url_encode, encode_url_ampersand, section_tag)
            
            # 步骤5：调整 background-image 的位置（放在最后）
            # 提取 background-image 属性
            bg_image_match = re.search(r'background-image:\s*url\([^)]*\);', section_tag)
            if bg_image_match:
                bg_image = bg_image_match.group(0)
                # 移除原位置的 background-image
                section_tag = section_tag.replace(bg_image, '')
                # 在 background-repeat 之后插入 background-image
                section_tag = section_tag.replace('background-repeat: no-repeat;', f'background-repeat: no-repeat; {bg_image}')
            
            # 步骤6：确保有 class="" 属性
            if 'class=' not in section_tag:
                section_tag = section_tag[:-1] + ' class="">'
            
            return section_tag
        
        # 查找并修复头像 section
        pattern = r'<section[^>]*border-radius:\s*100%[^>]*background-image[^>]*>'
        content = re.sub(pattern, fix_avatar_section, content)
        
        return content
    
    def _process_task_lists(self, soup: BeautifulSoup) -> None:
        """
        处理任务列表：将 checkbox 替换为 Unicode 字符
        mistune 的 task_lists 插件生成的是 <input type="checkbox">
        但微信不支持，我们用 ✅ 和 ☐ 替代
        """
        # 查找所有 task-list-item 类的 li 元素
        task_items = soup.find_all('li', class_='task-list-item')
        
        for item in task_items:
            # 查找其中的 checkbox
            checkbox = item.find('input', class_='task-list-item-checkbox')
            
            if checkbox:
                # 检查是否已完成
                is_checked = checkbox.has_attr('checked')
                
                # 替换为 Unicode 字符
                icon = soup.new_string('✅ ' if is_checked else '☐ ')
                
                # 移除 checkbox，插入图标
                checkbox.replace_with(icon)
    
    def _protect_code_quotes(self, soup: BeautifulSoup) -> None:
        """
        保护代码块中的引号，防止微信编辑器转换为智能引号
        
        微信编辑器会将直引号 " 转换为智能引号 ""
        这会导致代码（如 AppleScript）语法错误
        
        解决方案：将代码块中的 " 转换为 HTML 实体 &quot;
        
        Args:
            soup: BeautifulSoup 对象
        """
        # 查找所有 <pre><code> 组合（代码块）
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if code and code.string:
                # 将代码内容中的引号转换为 HTML 实体
                original_text = code.string
                protected_text = original_text.replace('"', '&quot;')
                
                # 替换代码内容
                code.string.replace_with(protected_text)
        
        # 也处理单独的 <code> 标签（行内代码）
        for code in soup.find_all('code'):
            # 跳过已经处理过的（在 pre 内的）
            if code.parent and code.parent.name == 'pre':
                continue
            
            if code.string:
                original_text = code.string
                protected_text = original_text.replace('"', '&quot;')
                code.string.replace_with(protected_text)
    
    def _remove_unsupported_tags(self, soup: BeautifulSoup) -> None:
        """
        移除微信不支持的标签
        
        Args:
            soup: BeautifulSoup 对象
        """
        # 微信不支持的标签列表
        unsupported = [
            'script',   # JavaScript
            'style',    # 外部样式（我们已经内联）
            'iframe',   # 嵌入框架
            'form',     # 表单
            'input',    # 输入框
            'button',   # 按钮
            'select',   # 下拉框
            'textarea', # 文本域
            'video',    # 视频（微信有特殊处理）
            'audio',    # 音频（微信有特殊处理）
        ]
        
        for tag_name in unsupported:
            for tag in soup.find_all(tag_name):
                tag.decompose()
    
    def _process_images(self, soup: BeautifulSoup) -> None:
        """
        处理图片属性，确保兼容微信
        
        Args:
            soup: BeautifulSoup 对象
        """
        max_width = self.config.get('max_image_width', 677)
        
        for img in soup.find_all('img'):
            # 移除 width 和 height 属性（使用内联样式控制）
            if 'width' in img.attrs:
                del img.attrs['width']
            if 'height' in img.attrs:
                del img.attrs['height']
            
            # 确保有 style 属性
            if 'style' not in img.attrs or not img.attrs['style']:
                img.attrs['style'] = f'max-width: {max_width}px; width: 100%; height: auto; display: block;'
            
            # 添加 data-* 属性用于微信图片处理
            if 'data-ratio' not in img.attrs:
                img.attrs['data-ratio'] = '1'
            if 'data-w' not in img.attrs:
                img.attrs['data-w'] = str(max_width)
    
    def _fix_list_nesting(self, soup: BeautifulSoup) -> None:
        """
        修复列表嵌套结构（微信特殊要求）
        
        微信要求嵌套列表不能直接在 li 内，需要移到 li 后面
        
        Args:
            soup: BeautifulSoup 对象
        """
        # 处理所有 li 标签
        for li in soup.find_all('li'):
            # 查找直接子元素中的列表
            nested_lists = []
            for child in li.children:
                if child.name in ['ul', 'ol']:
                    nested_lists.append(child)
            
            # 将嵌套列表移到 li 后面
            for nested_list in nested_lists:
                nested_list.extract()
                li.insert_after(nested_list)
    
    def _remove_classes(self, soup: BeautifulSoup) -> None:
        """
        移除所有 CSS 类名
        
        Args:
            soup: BeautifulSoup 对象
        """
        for tag in soup.find_all(class_=True):
            del tag.attrs['class']
    
    def _process_svg(self, soup: BeautifulSoup) -> None:
        """
        处理 SVG 兼容性
        
        Args:
            soup: BeautifulSoup 对象
        """
        for svg in soup.find_all('svg'):
            # 如果 SVG 没有被 p 标签包裹，添加一个
            if svg.parent and svg.parent.name not in ['p', 'div', 'section']:
                p = soup.new_tag('p')
                svg.wrap(p)
            
            # 添加空白文本节点帮助微信渲染
            if svg.string is None or not svg.string.strip():
                svg.append(soup.new_string(' '))
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        提取正文内容
        
        Args:
            soup: BeautifulSoup 对象
            
        Returns:
            处理后的 HTML 字符串
        """
        # 使用 decode() 而非 str() 来保持原始引号格式
        # formatter=None 保持原始的 HTML 实体编码和引号格式
        # 尝试提取 article 标签内容
        article = soup.find('article')
        if article:
            return article.decode(formatter=None)
        
        # 否则提取 body 内容
        body = soup.find('body')
        if body:
            return body.decode(formatter=None)
        
        # 如果都没有，返回整个文档
        return soup.decode(formatter=None)
