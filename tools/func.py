from typing import List
from tools.node import Node
from typing import List, Set
import numpy as np
from typing import List, Set, Dict

def cmp_node(node1: Node, node2: Node):
    if node1.rowspan[0] < node2.rowspan[0]:
        return -1
    elif node1.rowspan[0] > node2.rowspan[0]:
        return 1
    else:
        if node1.colspan[0] < node2.colspan[0]:
            return -1
        else:
            return 1

def cmp_dict(node1: Dict, node2: Dict):
    if node1["rowspan"][0] < node2["rowspan"][0]:
        return -1
    elif node1["rowspan"][0] > node2["rowspan"][0]:
        return 1
    else:
        if node1["colspan"][0] < node2["colspan"][0]:
            return -1
        else:
            return 1

def language_judgement(table: List) -> str:
    """
    判断输入的表格是中文还是英文
    :param table:
    :return:
    """
    for cell in table:
        str_text = cell['text']
        for char in str_text:
            if "\u4e00" <= char <= "\u9fff":
                return "Chinese"
    return "English"


def is_rectangle(i_segmented_table: Set[Node]):
    left_index, right_index = list(i_segmented_table)[0].colspan[0], list(i_segmented_table)[0].colspan[1]
    up_index, down_index = list(i_segmented_table)[0].rowspan[0], list(i_segmented_table)[0].rowspan[1]
    for cell in list(i_segmented_table):
        left_index, right_index = min(left_index, cell.colspan[0]), max(right_index, cell.colspan[1])
        up_index, down_index = min(up_index, cell.rowspan[0]), max(down_index, cell.rowspan[1])
    array_2d = np.zeros((down_index - up_index + 1, right_index - left_index + 1), dtype=np.uint8)
    for cell in list(i_segmented_table):
        array_2d[cell.rowspan[0] - up_index:cell.rowspan[1] - up_index + 1,
        cell.colspan[0] - left_index:cell.colspan[1] - left_index + 1] = 1
    for i in range(array_2d.shape[0]):
        for j in range(array_2d.shape[1]):
            if array_2d[i, j] == 0:
                return False
    return True


def sub_table_adjust(segmented_table: List[Set[Node]], all_table_node: List[Node]):
    while True:
        tag = True
        for i_segmented_table in segmented_table:
            if not is_rectangle(i_segmented_table):
                while not is_rectangle(i_segmented_table):
                    print("----------------打印不是矩形的子表----------------")
                    for j_cell in list(i_segmented_table):
                        print(j_cell.text, end="#")
                    print()
                    tag = False
                    left_index, right_index = list(i_segmented_table)[0].colspan[0], list(i_segmented_table)[0].colspan[1]
                    up_index, down_index = list(i_segmented_table)[0].rowspan[0], list(i_segmented_table)[0].rowspan[1]
                    for cell in list(i_segmented_table):
                        left_index, right_index = min(left_index, cell.colspan[0]), max(right_index, cell.colspan[1])
                        up_index, down_index = min(up_index, cell.rowspan[0]), max(down_index, cell.rowspan[1])
                    array_2d = np.zeros((down_index - up_index + 1, right_index - left_index + 1), dtype=np.uint8)
                    for cell in list(i_segmented_table):
                        array_2d[cell.rowspan[0] - up_index:cell.rowspan[1] - up_index + 1,
                        cell.colspan[0] - left_index:cell.colspan[1] - left_index + 1] = 1
                    print(array_2d)
                    for i in range(array_2d.shape[0]):
                        tag_temp = False
                        for j in range(array_2d.shape[1]):
                            if array_2d[i, j] == 0:
                                print("i,j:",i,j)
                                tag_temp = True
                                row, column = i + up_index, j + left_index
                                print("row,column:",row,column)
                                for cell in all_table_node:

                                    if cell.colspan[0] <= column <= cell.colspan[1] and cell.rowspan[0] <= row <= \
                                            cell.rowspan[1]:
                                        print("cell.text:",cell.text)
                                        for i_cell_set_of_affiliation in cell.set_of_affiliation:
                                            if i_cell_set_of_affiliation is not cell:
                                                i_cell_set_of_affiliation.set_of_affiliation.discard(cell)
                                        for cell_i_segmented_table in list(i_segmented_table):
                                            cell_i_segmented_table.set_of_affiliation.add(cell)
                                        cell.set_of_affiliation = set()
                                        cell.set_of_affiliation.update(list(i_segmented_table)[0].set_of_affiliation)
                                        i_segmented_table.add(cell)
                                        break
                                break
                        if tag_temp:
                            break

                segmented_table = []
                for cell_node in all_table_node:
                    if all((cell_node not in segment_i) for segment_i in segmented_table):
                        segmented_table.append(cell_node.set_of_affiliation)
                break
            pass
        if tag:
            break
    return segmented_table


if __name__ == '__main__':
    from tools.preprocess import any_format_to_json
    from tools.table_seg import table_seg
    gt_table, propositions = any_format_to_json(r"E:\code\table_handle\tools\11.xlsx")

    segmented_table, all_table_node, rows_head = table_seg(gt_table)
    for i_segmented_table in segmented_table:
        for j_cell in list(i_segmented_table):
            print(j_cell.text, end="#")
        print()
    print("---------调整后-------------")
    segmented_table = sub_table_adjust(segmented_table, all_table_node)
    for i_segmented_table in segmented_table:
        for j_cell in list(i_segmented_table):
            print(j_cell.text, end="#")
        print()

    # print(language_judgement([
    #     {"text": "frvefcvecs"},
    #     {"text": "    你1234e123     "}
    # ]))
