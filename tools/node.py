class Node:
    """
    定义N叉树的节点
    """

    def __init__(self, context=None, children=None, colspan=None, rowspan=None):
        self.context = context
        self.children = children
        self.colspan = colspan
        self.rowspan = rowspan
