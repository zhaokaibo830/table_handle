import json
import random
from tools.kv_clf import kv_clf
from tools.node import Node
from typing import List, Set
from collections import Counter
from tools.create_cross_list import create_cross_list


def have_next_level_head(i_node: Node, direct: str):
    if direct == 'right':
        all_right_node: List[Node] = i_node.right_pointer[i_node.rowspan[0]:i_node.rowspan[1] + 1]
        if len(set(all_right_node)) == 1:
            return False
        if all_right_node[0].rowspan[0] != i_node.rowspan[0] or all_right_node[-1].rowspan[1] != i_node.rowspan[1]:
            return False
        return True
    elif direct == 'down':
        all_down_node: List[Node] = i_node.down_pointer[i_node.colspan[0]:i_node.colspan[1] + 1]
        if len(set(all_down_node)) == 1:
            return False
        if all_down_node[0].colspan[0] != i_node.colspan[0] or all_down_node[-1].colspan[1] != i_node.colspan[1]:
            return False
        return True


async def is_simple_table(simple_table: List, language):
    if len(simple_table) == 1:
        amended_table = []
        simple_table[0]["node_type"] = "value"
        amended_table.append({
            "text": simple_table[0]["text"],
            "colspan": simple_table[0]["colspan"][:],
            "rowspan": simple_table[0]["rowspan"][:],
            "node_type": "value"
        })
        unified_table = []
        unified_table.append({
            "text": simple_table[0]["text"],
            "colspan": [1, 1],
            "rowspan": [1, 1],
            "node_type": "value"
        })
        return amended_table, unified_table, False

    left_index, right_index = simple_table[0]["colspan"][0], simple_table[0]["colspan"][1]
    up_index, down_index = simple_table[0]["rowspan"][0], simple_table[0]["rowspan"][1]
    for cell in simple_table:
        left_index, right_index = min(left_index, cell["colspan"][0]), max(right_index, cell["colspan"][1])
        up_index, down_index = min(up_index, cell["rowspan"][0]), max(down_index, cell["rowspan"][1])
    one_level_head = None
    for i, cell in enumerate(simple_table):
        if cell["rowspan"] == [up_index, down_index] and cell["colspan"][0] == left_index:
            if Counter([i_node["colspan"][0] == cell["colspan"][1] + 1 for i_node in simple_table])[True] > 1:
                one_level_head = cell
                one_level_head["node_type"] = "key"
                del simple_table[i]
            break
        if cell["colspan"] == [left_index, right_index] and cell["rowspan"][0] == up_index:
            if Counter([i_node["rowspan"][0] == cell["rowspan"][1] + 1 for i_node in simple_table])[True] > 1:
                one_level_head = cell
                one_level_head["node_type"] = "key"
                del simple_table[i]
            break
    # print("one_level_head:",one_level_head)

    left_index = simple_table[0]["colspan"][0]
    up_index = simple_table[0]["rowspan"][0]
    for cell in simple_table:
        left_index = min(left_index, cell["colspan"][0])
        up_index = min(up_index, cell["rowspan"][0])
    # print("left_index:",left_index)
    # print("up_index:",up_index)
    for cell in simple_table:
        cell["colspan"][0] -= left_index - 1
        cell["rowspan"][0] -= up_index - 1
        cell["colspan"][1] -= left_index - 1
        cell["rowspan"][1] -= up_index - 1
    # print("-----------simple_table-----------------")
    # print(simple_table)
    all_table_node, row_column_head, rows_head, columns_head = create_cross_list(simple_table)
    # print("-----------all_table_node-----------------")
    # for cell in all_table_node:
    #     print("text:", cell.text, end="#")
    #     print("colspan:", cell.colspan, end="#")
    #     print("rowspan:", cell.rowspan, end="#")
    #     print("node_type:", cell.node_type)
    #     print("up_pointer", cell.up_pointer)
    #     print("down_pointer", cell.down_pointer)
    #     print("left_pointer", cell.left_pointer)
    #     print("right_pointer", cell.right_pointer)
    # 根据表格结构判断表头是否在左边
    left_is_head = True
    left_node: Set[Node] = set()
    left_all_head_node: Set[Node] = set()
    for i, i_row_head in enumerate(rows_head):
        left_node.add(i_row_head.right_pointer[i + 1])
        left_all_head_node.add(i_row_head.right_pointer[i + 1])
    left_node_list = list(left_node)
    if not left_node_list[0].right_pointer[left_node_list[0].rowspan[0]]:
        left_is_head = False
    # print("------------left_node-----------------")
    # for i_left_node in left_node:
    #     print(i_left_node.text)
    while True:
        # print("__________")
        # for _ in left_all_head_node:
        #     print(_.text)
        left_node_list = list(left_node)
        if all([i_left_node.colspan[1] == left_node_list[0].colspan[1] for i_left_node in left_node_list]):
            if not left_node_list[0].right_pointer[left_node_list[0].rowspan[0]]:
                left_is_head = False
                break
            if all([have_next_level_head(i_left_node, "right") for i_left_node in left_node]):
                left_node_temp: Set[Node] = set()
                for i_left_node in left_node:
                    left_node_temp.update(
                        set(i_left_node.right_pointer[i_left_node.rowspan[0]:i_left_node.rowspan[1] + 1]))
                left_node = left_node_temp
                left_all_head_node.update(left_node)
            else:
                up_index_list = [i_left_node.rowspan[0] for i_left_node in left_node_list]
                down_index_list = [i_left_node.rowspan[1] for i_left_node in left_node_list]
                for cell_node in all_table_node:
                    if cell_node not in left_all_head_node:
                        if cell_node.rowspan[0] not in up_index_list or cell_node.rowspan[1] not in down_index_list:
                            left_is_head = False
                            break
                break
        else:
            min_left_node = min(list(left_node), key=lambda obj: obj.colspan[1])
            if have_next_level_head(min_left_node, "right"):
                left_node.update(
                    set(min_left_node.right_pointer[min_left_node.rowspan[0]:min_left_node.rowspan[1] + 1]))
                left_node.discard(min_left_node)
                left_all_head_node.update(left_node)
            else:
                left_is_head = False
                break

    # print("left_is_head", left_is_head)
    # 根据表格结构判断表头是否在上边
    up_is_head = True
    up_node: Set[Node] = set()
    up_all_head_node: Set[Node] = set()
    for i, i_col_head in enumerate(columns_head):
        up_node.add(i_col_head.down_pointer[i + 1])
        up_all_head_node.add(i_col_head.down_pointer[i + 1])
    up_node_list = list(up_node)
    if not up_node_list[0].down_pointer[up_node_list[0].colspan[0]]:
        up_is_head = False
    # print("------------up_node-----------------")
    # for i_up_node in up_node:
    # print(i_up_node.text)
    while True:
        # print("__________")
        # for _ in up_all_head_node:
        #     print(_.text)
        up_node_list = list(up_node)
        if all([i_up_node.rowspan[1] == up_node_list[0].rowspan[1] for i_up_node in up_node_list]):
            if not up_node_list[0].down_pointer[up_node_list[0].colspan[0]]:
                up_is_head = False
                break
            if all([have_next_level_head(i_up_node, "down") for i_up_node in up_node]):
                up_node_temp: Set[Node] = set()
                for i_up_node in up_node:
                    up_node_temp.update(
                        set(i_up_node.down_pointer[i_up_node.colspan[0]:i_up_node.colspan[1] + 1]))
                up_node = up_node_temp
                up_all_head_node.update(up_node)
            else:
                up_index_list = [i_up_node.colspan[0] for i_up_node in up_node_list]
                down_index_list = [i_up_node.colspan[1] for i_up_node in up_node_list]
                for cell_node in all_table_node:
                    if cell_node not in up_all_head_node:
                        if cell_node.colspan[0] not in up_index_list or cell_node.colspan[1] not in down_index_list:
                            up_is_head = False
                            break
                break
        else:
            min_up_node = min(list(up_node), key=lambda obj: obj.rowspan[1])
            if have_next_level_head(min_up_node, "down"):
                up_node.update(
                    set(min_up_node.down_pointer[min_up_node.colspan[0]:min_up_node.colspan[1] + 1]))
                up_node.discard(min_up_node)
                up_all_head_node.update(up_node)
            else:
                up_is_head = False
                break

    # print("up_is_head", up_is_head)

    if left_is_head and not up_is_head:
        head_nodes = left_all_head_node
    elif not left_is_head and up_is_head:
        head_nodes = up_all_head_node
        pass
    elif left_is_head and up_is_head:
        temp_table_dict = \
            (await kv_clf({"cells": simple_table}, coarse_grained_degree=1, fine_grained_degree=0, checkpoint=[0, 0],
               language=language))[-1]
        # print("temp_table_dict:",temp_table_dict)
        for i_node in all_table_node:
            for j_cell in temp_table_dict["cells"]:
                # print(j_cell)
                if i_node.colspan == j_cell["colspan"] and i_node.rowspan == j_cell["rowspan"]:
                    i_node.node_type = j_cell["node_type"]
        left_node: Set[Node] = set()
        for i, i_row_head in enumerate(rows_head):
            left_node.add(i_row_head.right_pointer[i + 1])
        up_node: Set[Node] = set()
        for i, i_col_head in enumerate(columns_head):
            up_node.add(i_col_head.down_pointer[i + 1])
        if Counter(i_left_node.node_type for i_left_node in left_node)["key"] > \
                Counter(i_up_node.node_type for i_up_node in up_node)["key"]:
            up_is_head = False
            head_nodes = left_node
        else:
            left_is_head = False
            head_nodes = up_node
    else:
        head_nodes = []
    for cell_node in all_table_node:
        if cell_node in head_nodes:
            cell_node.node_type = "key"
        else:
            cell_node.node_type = "value"

    amended_table = []
    if one_level_head:
        amended_table.append(one_level_head)
    for cell_node in all_table_node:
        amended_table.append({
            "text": cell_node.text,
            "colspan": [cell_node.colspan[0] + left_index - 1, cell_node.colspan[1] + left_index - 1],
            "rowspan": [cell_node.rowspan[0] + up_index - 1, cell_node.rowspan[1] + up_index - 1],
            "node_type": cell_node.node_type
        })

    unified_table = []
    right_index = all_table_node[0].colspan[1]
    down_index = all_table_node[0].colspan[1]
    for cell in all_table_node:
        right_index = max(right_index, cell.colspan[1])
        down_index = max(down_index, cell.rowspan[1])
    if left_is_head and not up_is_head:
        if one_level_head:
            unified_table.append({
                "text": one_level_head["text"],
                "colspan": [1, 1],
                "rowspan": [1, down_index],
                "node_type": "key"
            })
            for cell_node in all_table_node:
                unified_table.append({
                    "text": cell_node.text,
                    "colspan": [cell_node.colspan[0] + 1, cell_node.colspan[1] + 1],
                    "rowspan": [cell_node.rowspan[0], cell_node.rowspan[1]],
                    "node_type": cell_node.node_type
                })
        else:
            for cell_node in all_table_node:
                unified_table.append({
                    "text": cell_node.text,
                    "colspan": [cell_node.colspan[0], cell_node.colspan[1]],
                    "rowspan": [cell_node.rowspan[0], cell_node.rowspan[1]],
                    "node_type": cell_node.node_type
                })
        for cell in unified_table:
            cell["colspan"], cell["rowspan"] = cell["rowspan"], cell["colspan"]
    elif not left_is_head and up_is_head:
        if one_level_head:
            unified_table.append({
                "text": one_level_head["text"],
                "colspan": [1, right_index],
                "rowspan": [1, 1],
                "node_type": "key"
            })
            for cell_node in all_table_node:
                unified_table.append({
                    "text": cell_node.text,
                    "colspan": [cell_node.colspan[0], cell_node.colspan[1]],
                    "rowspan": [cell_node.rowspan[0] + 1, cell_node.rowspan[1] + 1],
                    "node_type": cell_node.node_type
                })
        else:
            for cell_node in all_table_node:
                unified_table.append({
                    "text": cell_node.text,
                    "colspan": [cell_node.colspan[0], cell_node.colspan[1]],
                    "rowspan": [cell_node.rowspan[0], cell_node.rowspan[1]],
                    "node_type": cell_node.node_type
                })
    else:
        for cell in amended_table:
            unified_table.append({
                "text": cell["text"],
                "colspan": cell["colspan"],
                "rowspan": cell["rowspan"],
                "node_type": cell["node_type"]
            })

    if left_is_head or up_is_head:
        have_table_head = True
    else:
        have_table_head = False

    return amended_table, unified_table, have_table_head

if __name__ == "__main__":
    from tools.preprocess import excel_to_json
    from tools.func import language_judgement
    table_dict = excel_to_json("1.xlsx")
    print(table_dict)
    language = language_judgement(table_dict["cells"])
    whole_table_amended_table, whole_table_unified_table, whole_table_have_table_head = is_simple_table(
        table_dict["cells"], language)
    print(whole_table_amended_table)
