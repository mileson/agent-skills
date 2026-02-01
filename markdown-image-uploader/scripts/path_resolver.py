"""Path Resolver - 路径解析器"""

import re
from pathlib import Path
from typing import List, Tuple, Optional
import unicodedata


class PathResolver:
    """Markdown 图片路径解析器"""
    
    # 匹配 Markdown 图片语法：![alt](path)
    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    
    # 支持的路径格式
    SUPPORTED_PATHS = [
        'Medias/images/',
        'images/',  # 兼容格式
    ]
    
    def __init__(self, markdown_content: str, markdown_path: Optional[str] = None):
        """
        初始化路径解析器
        
        Args:
            markdown_content: Markdown 内容
            markdown_path: Markdown 文件路径（用于解析相对路径）
        """
        self.content = markdown_content
        self.markdown_path = markdown_path
        self.markdown_dir = Path(markdown_path).parent if markdown_path else Path.cwd()
    
    def extract_images(self) -> List[Tuple[str, str, str]]:
        """
        提取所有符合格式的图片
        
        Returns:
            List of (full_match, alt_text, image_path)
        """
        images = []
        
        for match in self.IMAGE_PATTERN.finditer(self.content):
            full_match = match.group(0)
            alt_text = match.group(1)
            image_path = match.group(2)
            
            # 跳过网络图片
            if image_path.startswith(('http://', 'https://')):
                continue
            
            # 检查是否符合支持的路径格式
            if self._is_supported_path(image_path):
                images.append((full_match, alt_text, image_path))
        
        return images
    
    def _is_supported_path(self, path: str) -> bool:
        """检查路径是否符合支持的格式"""
        for supported in self.SUPPORTED_PATHS:
            if supported in path:
                return True
        return False
    
    def resolve_local_path(self, image_path: str) -> Optional[Path]:
        """
        解析为绝对本地路径
        
        Args:
            image_path: Markdown 中的图片路径
        
        Returns:
            绝对路径 Path 对象，如果文件不存在则返回 None
        """
        # 移除前导 ./
        image_path = image_path.lstrip('./')

        # URL 解码（处理 %20 等编码字符）
        from urllib.parse import unquote
        image_path = unquote(image_path)
        
        # 尝试相对于 Markdown 文件目录
        abs_path = self.markdown_dir / image_path
        if abs_path.exists():
            return abs_path
        
        # 尝试相对于当前工作目录
        abs_path = Path.cwd() / image_path
        if abs_path.exists():
            return abs_path
        
        return None
    
    def generate_target_path(
        self,
        image_path: str,
        article_name: str,
        base_path: str = 'markdown-images',
        path_strategy: str = 'article_name'
    ) -> str:
        """
        生成目标路径
        
        Args:
            image_path: 原始图片路径
            article_name: 文章名称
            base_path: 基础路径前缀
            path_strategy: 路径组织策略（article_name, date_based, flat）
        
        Returns:
            目标路径（如：markdown-images/article-name/image.png）
        """
        filename = Path(image_path).name
        
        if path_strategy == 'article_name':
            # 按文章名称归类
            article_slug = self._slugify(article_name)
            return f"{base_path}/{article_slug}/{filename}"
        
        elif path_strategy == 'date_based':
            # 按日期归类
            from datetime import datetime
            now = datetime.now()
            return f"{base_path}/{now.year}/{now.month:02d}/{now.day:02d}/{filename}"
        
        else:  # flat
            # 平铺
            return f"{base_path}/{filename}"
    
    def _slugify(self, text: str) -> str:
        """
        将文本转换为 URL 友好的 slug
        
        Args:
            text: 原始文本（如："一键在Mac任意文件夹启动Claude Code"）
        
        Returns:
            slug（如："yi-jian-zai-mac-ren-yi-wen-jian-jia-qi-dong-claude-code"）
        """
        # 转为小写
        text = text.lower()
        
        # 移除特殊字符，保留中文、字母、数字、空格
        text = re.sub(r'[^\w\s-]', '', text, flags=re.UNICODE)
        
        # 空格和下划线转为连字符
        text = re.sub(r'[\s_]+', '-', text)
        
        # 移除多余的连字符
        text = re.sub(r'-+', '-', text)
        
        # 移除首尾连字符
        text = text.strip('-')
        
        return text or 'untitled'
    
    def extract_article_name(self) -> str:
        """
        从 Markdown 提取文章名称
        
        Returns:
            文章名称（优先 H1 标题，其次文件名）
        """
        # 提取 H1 标题
        h1_match = re.search(r'^#\s+(.+)$', self.content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()
        
        # 使用文件名（去除后缀）
        if self.markdown_path:
            return Path(self.markdown_path).stem
        
        return 'untitled'
    
    def replace_path(self, old_path: str, new_url: str) -> str:
        """
        替换 Markdown 中的图片路径
        
        Args:
            old_path: 原始路径
            new_url: 新的 CDN URL
        
        Returns:
            替换后的 Markdown 内容
        """
        # 转义特殊字符
        old_path_escaped = re.escape(old_path)
        
        # 替换路径（保留 alt 文本）
        pattern = rf'(!\[[^\]]*\])\({old_path_escaped}\)'
        replacement = rf'\1({new_url})'
        
        self.content = re.sub(pattern, replacement, self.content)
        return self.content
