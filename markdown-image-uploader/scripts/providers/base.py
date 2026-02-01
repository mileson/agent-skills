"""Base Provider Interface"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseProvider(ABC):
    """图床提供商基类接口"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化提供商
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.validate_config()
    
    @abstractmethod
    def validate_config(self) -> None:
        """验证配置是否完整"""
        pass
    
    @abstractmethod
    def upload(self, local_path: str, target_path: str) -> str:
        """
        上传文件到图床
        
        Args:
            local_path: 本地文件路径
            target_path: 目标路径（相对于 bucket/repo）
        
        Returns:
            CDN URL
        """
        pass
    
    @abstractmethod
    def exists(self, target_path: str) -> bool:
        """
        检查文件是否已存在
        
        Args:
            target_path: 目标路径
        
        Returns:
            是否存在
        """
        pass
    
    def get_cdn_url(self, target_path: str) -> str:
        """
        生成 CDN URL
        
        Args:
            target_path: 目标路径
        
        Returns:
            完整的 CDN URL
        """
        raise NotImplementedError("Subclass must implement get_cdn_url()")
