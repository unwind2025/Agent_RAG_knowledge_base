# 作 者 : 王和清
# 2026年 10月 28日 13时 00分 32秒
# 25875830@163.com
"""
        # node_entry            任务分发
        # node_pdf_to_md        pdf结构化解析
        # node_md_img           多模态图片理解
        # node_document_split   智能文档切片
        # node_item_name_recognition   主体识别与标签提取
        # node_bge_embedding    混合向量化
        # node_import_milvus    数据持久化
"""
from processor.import_processor.base import BaseNode
from processor.import_processor.state import ImportGraphState


class NodeEntry(BaseNode):
    """
    入口节点：任务分发
    """

    name = "node_entry"

    def process(self, state: ImportGraphState):
        return state
