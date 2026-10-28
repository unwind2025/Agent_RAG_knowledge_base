# 作 者 : 王和清
# 2026年 10月 28日 13时 06分 25秒
# 25875830@163.com


from processor.import_processor.base import BaseNode
from processor.import_processor.state import ImportGraphState


class NodeImportMilvus(BaseNode):
    """
    导入向量库节点：数据持久化
    """

    name = "node_import_milvus"

    def process(self, state: ImportGraphState):
        return state
