from .node import Node
from typing import List


def is_align(node1: Node, node2: Node):
    node1_colspan = node1.colspan
    node2_colspan = node2.colspan
    node1_rowspan = node1.rowspan
    node2_rowspan = node2.rowspan
    if node1_colspan[0] == node2_colspan[0] and node1_colspan[1] == node2_colspan[1] and node1_rowspan[1] + 1 == \
            node2_rowspan[0]:
        return True
    if node1_rowspan[0] == node2_rowspan[0] and node1_rowspan[1] == node2_rowspan[1] and node1_colspan[1] + 1 == \
            node2_colspan[0]:
        return True
    return False

def merge_node(node1: Node, node2: Node):
    node1_colspan = node1.colspan
    node2_colspan = node2.colspan
    node1_rowspan = node1.rowspan
    node2_rowspan = node2.rowspan
    node1_text = node1.text
    node2_text = node2.text
    if node1_colspan[0] == node2_colspan[0] and node1_colspan[1] == node2_colspan[1]:
        merged_colspan = node1_colspan
        merged_rowspan = [node1_rowspan[0], node2_rowspan[1]]
        merged_text = node1_text + "的值是" + node2_text
        return merged_colspan, merged_rowspan, merged_text
    if node1_rowspan[0] == node2_rowspan[0] and node1_rowspan[1] == node2_rowspan[1]:
        merged_rowspan = node1_rowspan
        merged_colspan = [node1_colspan[0], node2_colspan[1]]
        merged_text = node1_text + "的值是" + node2_text
        return merged_colspan, merged_rowspan, merged_text


def get_key_value(node1: Node, node2: Node):
    node1_colspan = node1.colspan
    node2_colspan = node2.colspan
    node1_rowspan = node1.rowspan
    node2_rowspan = node2.rowspan
    if node1_colspan[0] == node2_colspan[0] and node1_colspan[1] == node2_colspan[1]:
        if node1_rowspan[1] < node2_rowspan[0]:
            return node1, node2
        else:
            return node2, node1
    if node1_rowspan[0] == node2_rowspan[0] and node1_rowspan[1] == node2_rowspan[1]:
        if node1_colspan[1] < node2_colspan[0]:
            return node1, node2
        else:
            return node2, node1
