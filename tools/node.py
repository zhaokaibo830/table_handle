from typing import List
class Node:
    """
    定义N叉树的节点
    """

    def __init__(self, context:str, colspan:List[int], rowspan:List[int], up_pointer:List, down_pointer:List,
                 left_pointer:List, right_pointer:List):
        self.context = context
        self.colspan = colspan
        self.rowspan = rowspan

        self.up_pointer=up_pointer
        self.down_pointer=down_pointer
        self.left_pointer=left_pointer
        self.right_pointer=right_pointer
