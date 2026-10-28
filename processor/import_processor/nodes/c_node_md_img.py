# 作 者 : 王和清
# 2026年 10月 28日 13时 05分 30秒
# 25875830@163.com

from processor.import_processor.base import BaseNode
from processor.import_processor.state import ImportGraphState


class NodeMDImg(BaseNode):
    """
    MarkDown图片处理节点：多模态图片理解
    """

    name = "node_md_img"

    def process(self, state: ImportGraphState):
        return state
