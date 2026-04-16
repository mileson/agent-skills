"""Main Uploader - 主上传器"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

# 使用绝对导入（避免相对导入问题）
from path_resolver import PathResolver
from providers import AliyunOSSProvider

PLACEHOLDER_PREFIXES = (
    '你的',
    'your-',
    'replace-me',
    'example-',
)

REQUIRED_ALIYUN_FIELDS = (
    'access_key_id',
    'access_key_secret',
    'bucket',
    'region',
    'endpoint',
)


class MarkdownImageUploader:
    """Markdown 图床上传器"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化上传器

        Args:
            config_path: 配置文件路径（默认优先使用 config/my_hosts.yaml，其次 config/image_hosts.yaml）
        """
        resolved_path = self._resolve_config_path(config_path)
        self.config_path = resolved_path
        self.config = self._load_config(resolved_path)
        self.provider = self._init_provider()

    def _resolve_config_path(self, config_path: Optional[str]) -> Path:
        """解析默认配置路径。"""
        if config_path is not None:
            return Path(config_path)

        skill_dir = Path(__file__).parent.parent
        my_hosts = skill_dir / 'config' / 'my_hosts.yaml'
        image_hosts = skill_dir / 'config' / 'image_hosts.yaml'
        return my_hosts if my_hosts.exists() else image_hosts

    def _load_config(self, config_path: Path) -> dict:
        """加载配置文件并自动合并本地 secrets-vault 中的敏感字段。"""
        if not config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_path}\n"
                "Please create config/my_hosts.yaml or configure the aliyun_oss namespace in secrets-vault."
            )

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

        config = self._merge_secrets_vault(config)
        return config

    def _merge_secrets_vault(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """若配置文件中的敏感字段为空/模板值，则尝试从 secrets-vault 注入。"""
        provider = config.setdefault('aliyun_oss', {})
        missing_sensitive = [
            field for field in ('access_key_id', 'access_key_secret')
            if self._is_placeholder(provider.get(field))
        ]

        if not missing_sensitive:
            return config

        vault_data = self._read_secret_namespace('aliyun_oss')
        if not isinstance(vault_data, dict):
            return config

        for field in REQUIRED_ALIYUN_FIELDS:
            if self._is_placeholder(provider.get(field)) and vault_data.get(field):
                provider[field] = vault_data[field]

        return config

    def _read_secret_namespace(self, namespace: str) -> Optional[Dict[str, Any]]:
        """读取 secrets-vault 中的命名空间。"""
        candidates = [
            Path(__file__).resolve().parents[2] / 'secrets-vault' / 'scripts' / 'get_secret.py',
            Path.home() / '.cursor' / 'skills' / 'secrets-vault' / 'scripts' / 'get_secret.py',
            Path.home() / '.claude' / 'skills' / 'secrets-vault' / 'scripts' / 'get_secret.py',
        ]

        for script in candidates:
            if not script.exists():
                continue
            result = subprocess.run(
                ['python3', str(script), namespace],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                continue
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                continue
        return None

    @staticmethod
    def _is_placeholder(value: Any) -> bool:
        if value is None:
            return True
        if not isinstance(value, str):
            return False
        text = value.strip()
        if not text:
            return True
        lowered = text.lower()
        return lowered.startswith(PLACEHOLDER_PREFIXES)

    def _init_provider(self):
        """初始化图床提供商"""
        active_provider = self.config.get('active_provider', 'aliyun_oss')

        if active_provider == 'aliyun_oss':
            provider_config = self.config.get('aliyun_oss', {})
            return AliyunOSSProvider(provider_config)

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
        markdown_file = Path(markdown_path)
        if not markdown_file.exists():
            raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        resolver = PathResolver(content, str(markdown_file))

        if article_name is None:
            article_name = resolver.extract_article_name()

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

        for full_match, alt_text, image_path in images:
            try:
                local_path = resolver.resolve_local_path(image_path)

                if local_path is None:
                    print(f"⚠️  Skipped (file not found): {image_path}")
                    stats['skipped'] += 1
                    continue

                provider_config = self.config.get(self.config['active_provider'], {})
                base_path = provider_config.get('base_path', 'markdown-images')
                path_strategy = provider_config.get('path_strategy', 'article_name')

                target_path = resolver.generate_target_path(
                    image_path,
                    article_name,
                    base_path,
                    path_strategy
                )

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

                print(f"📤 Uploading: {local_path.name} → {target_path}")
                cdn_url = self.provider.upload(str(local_path), target_path)

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

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n💾 Saved to: {output_path}")

        print(f"\n📊 Summary:")
        print(f"  Total: {stats['total']}")
        print(f"  Uploaded: {stats['uploaded']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"  Failed: {stats['failed']}")

        print("\n" + "=" * 50)
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
        print("=" * 50)

        return content, stats
