from typing import List


class Node:
    """
    定义单元格对象的类
    """
    def __init__(self, text: str, colspan: List[int], rowspan: List[int], up_pointer: List, down_pointer: List,
                 left_pointer: List, right_pointer: List, node_type: str, visited=False, merge_method=None):
        self.text = text
        self.colspan = colspan
        self.rowspan = rowspan
        # 结点的类型，key/value
        self.node_type = node_type
        # 标记结点是否被合并过
        self.visited = visited
        # 当前此结点所隶属的子表集合
        self.set_of_affiliation = set()
        # 当前结点合并的方式，是vertical（垂直方向合并）还是horizontal（水平方向合并）
        self.merge_method = merge_method
        # 当前结点上方的指针列表
        self.up_pointer = up_pointer
        # 当前结点下方的指针列表
        self.down_pointer = down_pointer
        # 当前结点左方的指针列表
        self.left_pointer = left_pointer
        # 当前结点右方的指针列表
        self.right_pointer = right_pointer
