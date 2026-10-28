# 作 者 : 王和清
# 2026年 10月 28日 13时 06分 14秒
# 25875830@163.com

from processor.import_processor.base import BaseNode
from processor.import_processor.state import ImportGraphState


class NodeBGEEmbedding(BaseNode):
    """
    混合向量化节点：使用 BGE-M3 模型将文本转换为向量
    """

    name = "node_bge_embedding"

    def process(self, state: ImportGraphState):
        return state
