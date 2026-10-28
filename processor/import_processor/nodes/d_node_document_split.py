# 作 者 : 王和清
# 2026年 10月 28日 13时 05分 42秒
# 25875830@163.com

from processor.import_processor.base import BaseNode
from processor.import_processor.state import ImportGraphState


class NodeDocumentSplit(BaseNode):
    """
    文档切分节点：智能文档切片
    """

    name = "node_document_split"

    def process(self, state: ImportGraphState):
        return state
