# 作 者 : 王和清
# 2026年 10月 28日 11时 58分 40秒
# 25875830@163.com
"""
    主图 (main_graph.py)
        - 构建完整的导入工作流图
        - 定义节点执行顺序和条件路由
        - 提供便捷的测试入口
"""

import json

from langgraph.constants import END
from langgraph.graph import StateGraph

from processor.import_processor.base import setup_logging
from processor.import_processor.nodes.a_node_entry import NodeEntry
from processor.import_processor.nodes.b_node_pdf_to_md import NodePDFToMD
from processor.import_processor.nodes.c_node_md_img import NodeMDImg
from processor.import_processor.nodes.d_node_document_split import NodeDocumentSplit
from processor.import_processor.nodes.e_node_item_name_recognition import NodeItemNameRecognition
from processor.import_processor.nodes.f_node_bge_embedding import NodeBGEEmbedding
from processor.import_processor.nodes.g_node_import_milvus import NodeImportMilvus
from processor.import_processor.state import ImportGraphState


class KBImportWorkflow:
    """知识库导入工作流"""

    def __init__(self, config=None):
        """
        初始化工作流
        """
        self.__compiled_graph = None

    """ 
    @property 是 Python 内置装饰器，把一个方法伪装成属性，调用的时候不用加 ()，像读变量一样，但内部走函数逻辑。
    ----------------------------------------------------------------
        class User:
            def __init__(self, first_name, last_name):
                self.first_name = first_name
                self.last_name = last_name
        
            @property
            def full_name(self):
                return f"{self.first_name} {self.last_name}"
        
        u = User("zhang", "san")
        print(u.full_name)   # ✅ 直接 .full_name，不是 full_name()
    ----------------------------------------------------------------
        # u.full_name = "xxx"  # 默认只读，直接赋值会报错
        不加 @property 就得写 u.full_name()；加了之后写法和访问成员变量一样。
    """

    @property
    def graph(self):
        """懒加载：只在第一次使用时编译图"""
        if self.__compiled_graph is None:  # 单例
            self.__compiled_graph = self.build_graph()  # 创建图
        return self.__compiled_graph

    """
    # @staticmethod：不需要 self、也不需要 cls 的方法，就是个挂在类名下的普通函数，
    # 用来放 "和这个类相关但不需要它的数据" 的工具逻辑。
    """

    @staticmethod  # 工具方法
    def route_after_entry(state: ImportGraphState) -> str:
        """
        入口节点后的条件路由函数
        :param state: 当前状态
        :return: 下一个节点名称
        """
        if state.get("is_pdf_read_enabled"):
            return "node_pdf_to_md"  # pdf → 走 b 节点
        elif state.get("is_md_read_enabled"):
            return "node_md_img"  # md → 走 c 节点
        else:
            return END

    def build_graph(self):  # 实例方法
        """
        创建图结构
        :return: 编译后的图
        """
        # 1. 初始化LangGraph状态图
        graph = StateGraph(ImportGraphState)

        # 2. 注册节点到工作流
        graph.add_node("a_node_entry", NodeEntry())
        graph.add_node("b_node_pdf_to_md", NodePDFToMD())
        graph.add_node("c_node_md_img", NodeMDImg())
        graph.add_node("d_node_document_split", NodeDocumentSplit())
        graph.add_node("e_node_item_name_recognition", NodeItemNameRecognition())
        graph.add_node("f_node_bge_embedding", NodeBGEEmbedding())
        graph.add_node("g_node_import_milvus", NodeImportMilvus())

        # 3. 设置入口节点
        graph.set_entry_point("a_node_entry")

        # 4. 注册条件边
        graph.add_conditional_edges(
            "a_node_entry",  # 条件边的起始节点
            self.route_after_entry,
            path_map={
                # key：路由函数的返回值，value:节点的名字
                "node_md_img": "c_node_md_img",  # pdf → 走 b 节点
                "node_pdf_to_md": "b_node_pdf_to_md",  # md  → 走 c 节点
                END: END  # END → 走 END 节点
            }
        )

        # 5. 注册顺序边
        graph.add_edge("b_node_pdf_to_md", "c_node_md_img")
        graph.add_edge("c_node_md_img", "d_node_document_split")
        graph.add_edge("d_node_document_split", "e_node_item_name_recognition")
        graph.add_edge("e_node_item_name_recognition", "f_node_bge_embedding")
        graph.add_edge("f_node_bge_embedding", "g_node_import_milvus")
        graph.add_edge("g_node_import_milvus", END)

        # 6. 编译工作流
        return graph.compile()

    def run(self, state: ImportGraphState, stream: bool = False):  # 开关参数，默认非流式（普通执行）
        """
        统一执行入口，支持切换invoke/stream
        :param state: 初始状态
        :param stream: 是否流式输出
        :return: 执行结果
        """
        if stream:
            # 控制流式输出时，每一步吐出来的是什么内容。"values" = 每一步吐出的都是当时的 state（状态）快照。
            return self.graph.stream(state, stream_mode="values")

        else:
            return self.graph.invoke(state)

    """  
    stream_mode=""
                模式	        每一步吐出的内容	                用途
                "values"	当前完整的 state（所有节点数据） 	看每一步状态变化 ✅最常用
                "updates"	只吐这个节点刚更新的那一部分（增量）	只看谁改了什么
                "messages"	只吐 LLM 产生的消息	            聊天 / 打字机效果                
    """


if __name__ == "__main__":
    # 启用日志
    setup_logging()

    # 定义初始状态
    init_state = {"import_file_path": r"D:\3.30\H3C.pdf"}
    workflow = KBImportWorkflow()

# 方式1：实例化后使用（推荐方式，可复用）
for event in workflow.run(init_state, stream=True):
    print(f"state: {event}")

# 方式2：非流式执行
final_state = workflow.run(init_state, stream=False)
print(json.dumps(final_state, ensure_ascii=False, indent=4))
# ensure_ascii=False：输出的中文等非 ASCII 字符保持原样
# indent=4：json.dump的一个参数，让输出的 JSON 缩进 4 个空格、换行排列（格式化），而不是挤成一行。

# 打印编译后的图结构
workflow.graph.get_graph().print_ascii()
