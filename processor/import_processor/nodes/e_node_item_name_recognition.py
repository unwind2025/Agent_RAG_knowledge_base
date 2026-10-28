# 作 者 : 王和清
# 2026年 10月 28日 13时 06分 03秒
# 25875830@163.com

from processor.import_processor.base import BaseNode
from processor.import_processor.state import ImportGraphState


class NodeItemNameRecognition(BaseNode):
    """
    主体识别节点：主体识别与标签提取
    """

    name = "node_item_name_recognition"

    def process(self, state: ImportGraphState):
        return state
