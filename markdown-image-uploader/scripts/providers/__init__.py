"""Image Host Providers Package"""

# 使用绝对导入
from providers.base import BaseProvider
from providers.aliyun_oss import AliyunOSSProvider

__all__ = ['BaseProvider', 'AliyunOSSProvider']
