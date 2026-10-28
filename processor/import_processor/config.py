"""
导入流程配置管理模块

集中管理所有配置项，支持环境变量覆盖
"""

import os
from dataclasses import dataclass, field
from typing import Set, Optional

from dotenv import load_dotenv

load_dotenv()

"""
from dataclasses import dataclass
@dataclass
等价于：
class ImportConfig:
    def __init__(self, batch_size: int, timeout: int):  # 构造方法
        self.batch_size = batch_size
        self.timeout = timeout

    def __repr__(self):  # 打印对象时清晰看到字段
        return f"ImportConfig(batch_size={self.batch_size}, timeout={self.timeout})"

    def __eq__(self, other):  # 直接用 == 对比两个实例的字段值（按值比较，不是内存地址）
        if not isinstance(other, ImportConfig):
            return False
        return self.batch_size == other.batch_size and self.timeout == other.timeout
****************************************************************************************    
    @dataclass(
    init=True,       # 默认True：自动生成 __init__
    repr=True,       # 默认True：自动生成 __repr__
    eq=True,         # 默认True：自动生成 __eq__
    order=False,     # 默认False：是否生成比较方法(< > <= >=)
    frozen=False,    # 默认False；True=冻结，实例不可修改（只读配置，很适合Config！）
    kw_only=False,   # 3.10+，True代表实例化时只能用关键字传参
)    
"""


@dataclass
class ImportConfig:
    """导入流程配置"""

    # ==================== 文档处理配置 ====================
    max_content_length: int = 2000  # 切片最大长度
    img_content_length: int = 200  # 图片上下文最大长度
    min_content_length: int = 500  # 合并短内容的最小长度
    overlap_sentences: int = 1  # 句子级切分时的重叠句数
    item_name_chunk_k: int = 3  # 商品名识别时使用的切片数量
    item_name_chunk_size: int = 2500  # 商品名识别时使用的切片内容长度

    image_extensions: Set[str] = field(
        default_factory=lambda: {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    )

    # ==================== LLM 配置 ====================
    openai_api_base: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_BASE", "")
    )
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    vl_model: str = field(
        default_factory=lambda: os.getenv("VL_MODEL", "")
    )
    item_model: str = field(
        default_factory=lambda: os.getenv("ITEM_MODEL", "")
    )
    default_model: str = field(
        default_factory=lambda: os.getenv("MODEL", "")
    )

    # ==================== Milvus 配置 ====================
    milvus_url: str = field(
        default_factory=lambda: os.getenv("MILVUS_URL", "")
    )
    chunks_collection: str = field(
        default_factory=lambda: os.getenv("CHUNKS_COLLECTION", "")
    )
    item_name_collection: str = field(
        default_factory=lambda: os.getenv("ITEM_NAME_COLLECTION", "")
    )
    entity_name_collection: str = field(
        default_factory=lambda: os.getenv("ENTITY_NAME_COLLECTION", "")
    )

    # ==================== MinIO 配置 ====================
    minio_endpoint: str = field(
        default_factory=lambda: os.getenv("MINIO_ENDPOINT", "")
    )
    minio_access_key: str = field(
        default_factory=lambda: os.getenv("MINIO_ACCESS_KEY", "")
    )
    minio_secret_key: str = field(
        default_factory=lambda: os.getenv("MINIO_SECRET_KEY", "")
    )
    minio_bucket: str = field(
        default_factory=lambda: os.getenv("MINIO_BUCKET_NAME", "")
    )
    minio_secure: bool = False

    # ==================== 向量配置 ====================
    embedding_dim: int = field(
        default_factory=lambda: int(os.getenv("EMBEDDING_DIM", "1024"))
    )
    embedding_batch_size: int = 8

    # ==================== 速率限制 ====================
    requests_per_minute: int = 15  # 图片总结 API 速率限制

    @classmethod
    def from_env(cls) -> "ImportConfig":
        """从环境变量加载配置"""
        return cls()

    # http://192.168.200.130:9000/
    def get_minio_base_url(self):
        base_protocol = "https://" if self.minio_secure else "http://"
        return base_protocol + f"{self.minio_endpoint}"


# ==================== 全局单例 ====================
_config: Optional[ImportConfig] = None


def get_config() -> ImportConfig:
    """获取配置单例"""
    global _config
    if _config is None:
        _config = ImportConfig.from_env()
    return _config
