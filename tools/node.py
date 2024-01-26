from typing import List


class Node:
    """
    定义N叉树的节点
    """

    def __init__(self, context: str, colspan: List[int], rowspan: List[int], up_pointer: List, down_pointer: List,
                 left_pointer: List, right_pointer: List, node_type: str, visited=False, merge_method=None):
        self.context = context
        self.colspan = colspan
        self.rowspan = rowspan
        self.node_type = node_type
        self.visited = visited
        self.set_of_affiliation = set()

        self.merge_method = merge_method

        self.up_pointer = up_pointer
        self.down_pointer = down_pointer
        self.left_pointer = left_pointer
        self.right_pointer = right_pointer
