"""Main Uploader - 主上传器"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 使用绝对导入（避免相对导入问题）
from path_resolver import PathResolver
from providers import AliyunOSSProvider


class MarkdownImageUploader:
    """Markdown 图床上传器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化上传器
        
        Args:
            config_path: 配置文件路径（默认使用 config/image_hosts.yaml）
        """
        if config_path is None:
            # 默认配置路径
            skill_dir = Path(__file__).parent.parent
            config_path = skill_dir / 'config' / 'image_hosts.yaml'
        
        self.config = self._load_config(config_path)
        self.provider = self._init_provider()
    
    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_path}\n"
                f"Please create config/my_hosts.yaml and fill in your credentials."
            )
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def _init_provider(self):
        """初始化图床提供商"""
        active_provider = self.config.get('active_provider', 'aliyun_oss')
        
        if active_provider == 'aliyun_oss':
            provider_config = self.config.get('aliyun_oss', {})
            return AliyunOSSProvider(provider_config)
        
        else:
            raise ValueError(f"Unsupported provider: {active_provider}")
    
    def process_markdown(
        self,
        markdown_path: str,
        output_path: Optional[str] = None,
        article_name: Optional[str] = None
    ) -> Tuple[str, Dict]:
        """
        处理 Markdown 文件，上传图片并替换路径
        
        Args:
            markdown_path: Markdown 文件路径
            output_path: 输出文件路径（可选）
            article_name: 文章名称（可选，用于路径归类）
        
        Returns:
            (处理后的 Markdown 内容, 统计信息)
        """
        # 读取 Markdown
        markdown_file = Path(markdown_path)
        if not markdown_file.exists():
            raise FileNotFoundError(f"Markdown file not found: {markdown_path}")
        
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 创建路径解析器
        resolver = PathResolver(content, str(markdown_file))
        
        # 提取文章名称
        if article_name is None:
            article_name = resolver.extract_article_name()
        
        # 提取图片
        images = resolver.extract_images()
        
        stats = {
            'total': len(images),
            'uploaded': 0,
            'skipped': 0,
            'failed': 0,
            'mappings': []
        }
        
        if not images:
            print("⚠️  No images found in Markdown (looking for Medias/images/ or images/ paths)")
            return content, stats
        
        print(f"🔍 Found {len(images)} images to process")
        
        # 处理每张图片
        for full_match, alt_text, image_path in images:
            try:
                # 解析本地路径
                local_path = resolver.resolve_local_path(image_path)
                
                if local_path is None:
                    print(f"⚠️  Skipped (file not found): {image_path}")
                    stats['skipped'] += 1
                    continue
                
                # 生成目标路径
                provider_config = self.config.get(self.config['active_provider'], {})
                base_path = provider_config.get('base_path', 'markdown-images')
                path_strategy = provider_config.get('path_strategy', 'article_name')
                
                target_path = resolver.generate_target_path(
                    image_path,
                    article_name,
                    base_path,
                    path_strategy
                )
                
                # 检查冲突策略
                conflict_strategy = provider_config.get('conflict_strategy', 'skip')
                
                if conflict_strategy == 'skip' and self.provider.exists(target_path):
                    cdn_url = self.provider.get_cdn_url(target_path)
                    print(f"⏭️  Skipped (already exists): {image_path}")
                    content = resolver.replace_path(image_path, cdn_url)
                    stats['skipped'] += 1
                    stats['mappings'].append({
                        'local': image_path,
                        'cdn': cdn_url,
                        'status': 'skipped'
                    })
                    continue
                
                # 上传图片
                print(f"📤 Uploading: {local_path.name} → {target_path}")
                cdn_url = self.provider.upload(str(local_path), target_path)
                
                # 替换路径
                content = resolver.replace_path(image_path, cdn_url)
                
                stats['uploaded'] += 1
                stats['mappings'].append({
                    'local': image_path,
                    'cdn': cdn_url,
                    'status': 'uploaded'
                })
                
                print(f"✅ Success: {cdn_url}")
            
            except Exception as e:
                print(f"❌ Failed to upload {image_path}: {str(e)}")
                stats['failed'] += 1
        
        # 保存输出
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n💾 Saved to: {output_path}")
        
        # 打印统计
        print(f"\n📊 Summary:")
        print(f"  Total: {stats['total']}")
        print(f"  Uploaded: {stats['uploaded']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"  Failed: {stats['failed']}")
        
        # 输出结构化 JSON（供 AI 读取）
        print("\n" + "="*50)
        print("📋 JSON Output (for AI):")
        print(json.dumps({
            "status": "success" if stats['failed'] == 0 else "partial",
            "total_images": stats['total'],
            "uploaded": stats['uploaded'],
            "skipped": stats['skipped'],
            "failed": stats['failed'],
            "output_file": str(output_path) if output_path else None,
            "mappings": stats['mappings']
        }, ensure_ascii=False, indent=2))
        print("="*50)
        
        return content, stats
