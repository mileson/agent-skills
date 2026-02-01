"""Aliyun OSS Provider"""

import os
import hashlib
import uuid
from pathlib import Path
from typing import Optional
from urllib.parse import quote

try:
    import alibabacloud_oss_v2 as oss
    from alibabacloud_oss_v2 import models as oss_models
    OSS_AVAILABLE = True
except ImportError:
    OSS_AVAILABLE = False

# 使用绝对导入
from providers.base import BaseProvider


class AliyunOSSProvider(BaseProvider):
    """阿里云 OSS 图床提供商"""
    
    def __init__(self, config: dict):
        if not OSS_AVAILABLE:
            raise ImportError(
                "alibabacloud-oss-v2 is not installed. "
                "Please run: pip install alibabacloud-oss-v2"
            )
        
        super().__init__(config)
        self._init_client()
    
    def validate_config(self) -> None:
        """验证配置"""
        required_fields = [
            'access_key_id',
            'access_key_secret',
            'bucket',
            'region',
            'endpoint'
        ]
        
        for field in required_fields:
            if not self.config.get(field):
                raise ValueError(f"Missing required config field: {field}")
    
    def _init_client(self) -> None:
        """初始化 OSS 客户端"""
        # ⭐ 修复：使用 StaticCredentialsProvider 而不是 Credentials 对象
        # 根据官方文档：Credentials 对象不能直接作为 credentials_provider
        # 必须使用 StaticCredentialsProvider 包装
        credentials_provider = oss.credentials.StaticCredentialsProvider(
            access_key_id=self.config['access_key_id'],
            access_key_secret=self.config['access_key_secret']
        )
        
        # 创建配置
        cfg = oss.config.load_default()
        cfg.credentials_provider = credentials_provider
        cfg.region = self.config['region']
        
        # 创建客户端
        self.client = oss.Client(cfg)
        self.bucket = self.config['bucket']
    
    def upload(self, local_path: str, target_path: str) -> str:
        """
        上传文件到阿里云 OSS
        
        Args:
            local_path: 本地文件路径
            target_path: 目标路径
        
        Returns:
            CDN URL
        """
        # 读取文件内容
        with open(local_path, 'rb') as f:
            file_data = f.read()
        
        # 处理文件名策略
        target_path = self._process_filename(local_path, target_path)
        
        # 上传文件
        request = oss_models.PutObjectRequest(
            bucket=self.bucket,
            key=target_path,
            body=file_data
        )
        
        try:
            result = self.client.put_object(request)
            
            if result.status_code == 200:
                return self.get_cdn_url(target_path)
            else:
                raise Exception(f"Upload failed with status code: {result.status_code}")
        
        except Exception as e:
            raise Exception(f"Failed to upload {local_path}: {str(e)}")
    
    def exists(self, target_path: str) -> bool:
        """检查文件是否存在"""
        try:
            request = oss_models.HeadObjectRequest(
                bucket=self.bucket,
                key=target_path
            )
            result = self.client.head_object(request)
            return result.status_code == 200
        except:
            return False
    
    def get_cdn_url(self, target_path: str) -> str:
        """
        生成 CDN URL
        
        ⚠️ 重要：对路径进行 URL 编码，确保 Markdown 中正确显示
        - safe='/' 保留路径分隔符
        - 空格会被编码为 %20
        - 中文会被编码为 %E8%BF%90%E8%A1%8C
        """
        cdn_domain = self.config.get('cdn_domain', '')
        use_ssl = self.config.get('use_ssl', True)
        protocol = 'https' if use_ssl else 'http'
        
        # URL 编码路径（保留斜杠）
        encoded_path = quote(target_path, safe='/')
        
        if cdn_domain:
            # 使用 CDN 域名
            return f"{protocol}://{cdn_domain}/{encoded_path}"
        else:
            # 使用 OSS 原始域名
            endpoint = self.config['endpoint']
            return f"{protocol}://{self.bucket}.{endpoint}/{encoded_path}"
    
    def _process_filename(self, local_path: str, target_path: str) -> str:
        """处理文件名策略"""
        strategy = self.config.get('filename_strategy', 'keep_original')
        
        if strategy == 'keep_original':
            return target_path
        
        # 获取文件扩展名
        ext = Path(local_path).suffix
        base_dir = str(Path(target_path).parent)
        
        if strategy == 'hash':
            # 使用文件内容 hash
            with open(local_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            filename = f"{file_hash}{ext}"
        
        elif strategy == 'uuid':
            # 使用随机 UUID
            filename = f"{uuid.uuid4().hex}{ext}"
        
        else:
            # 默认保持原文件名
            filename = Path(target_path).name
        
        return f"{base_dir}/{filename}"
