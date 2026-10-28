# 作 者 : 王和清
# 2026年 10月 28日 12时 57分 06秒
# 25875830@163.com

from processor.import_processor.base import BaseNode
from processor.import_processor.state import ImportGraphState


class NodePDFToMD(BaseNode):
    """
    PDF 转 Markdown 节点：PDF结构化解析
    """

    name = "node_pdf_to_md"

    def process(self, state: ImportGraphState):
        return state
