# 作 者 : 王和清
# 2026年 10月 28日 12时 37分 19秒
# 25875830@163.com

# 读取MinerU配置
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class MineruConfig:
    base_url: str
    api_token: str


mineru_config = MineruConfig(
    base_url=os.getenv("MINERU_BASE_URL"),
    api_token=os.getenv("MINERU_API_TOKEN")
)
