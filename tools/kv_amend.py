import json
import random

from tools.node import Node
from typing import List, Set
from collections import Counter

def create_cross_list(table:List):
    all_table_node: List[Node] = []
    table_rows, table_columns = 0, 0

    # 计算表格的行数和列数

    all_cells = table
    for cell in all_cells:
        left_index, right_index = cell['colspan'][0], cell['colspan'][1]
        up_index, down_index = cell['rowspan'][0], cell['rowspan'][1]
        table_columns = right_index if table_columns < right_index else table_columns
        table_rows = down_index if table_rows < down_index else table_rows

    # 把表格中的每个单元格转换成Node类对象
    all_cells = table
    for cell in all_cells:
        created_node = Node(text=cell['text'], colspan=cell['colspan'], rowspan=cell['rowspan'],
                            up_pointer=[None] * (table_columns + 1),
                            down_pointer=[None] * (table_columns + 1),
                            left_pointer=[None] * (table_rows + 1),
                            right_pointer=[None] * (table_rows + 1),
                            node_type=cell['node_type'])

        created_node.set_of_affiliation.add(created_node)
        all_table_node.append(created_node)

    # print("table_rows:", table_rows)
    # print("table_columns:", table_columns)

    # 构建十字双向链表
    row_column_head = Node(text="", colspan=[0, 0], rowspan=[0, 0], up_pointer=[None], down_pointer=[None],
                           left_pointer=[None], right_pointer=[None],
                           node_type="row_column_head")  # 复杂表格构成的双向十字链表的以行列进行索引的头指针
    pre = row_column_head
    rows_head = []  # 复杂表格构成的双向十字链表的以行进行索引的头指针列表
    for i in range(table_rows):
        row_head_i = Node(text="", colspan=[0, 0], rowspan=[i + 1, i + 1], up_pointer=[None] * (table_columns + 1),
                          down_pointer=[None] * (table_columns + 1),
                          left_pointer=[None] * (table_rows + 1), right_pointer=[None] * (table_rows + 1),
                          node_type='rows_head')
        row_head_i.up_pointer[0] = pre
        rows_head.append(row_head_i)
        pre.down_pointer[0] = row_head_i
        pre = row_head_i
    pre = row_column_head
    columns_head = []  # 复杂表格构成的双向十字链表的以列进行索引的头指针列表
    for i in range(table_columns):
        column_head_i = Node(text="", colspan=[i + 1, i + 1], rowspan=[0, 0],
                             up_pointer=[None] * (table_columns + 1),
                             down_pointer=[None] * (table_columns + 1),
                             left_pointer=[None] * (table_rows + 1), right_pointer=[None] * (table_rows + 1),
                             node_type="columns_head")
        column_head_i.left_pointer[0] = pre
        columns_head.append(column_head_i)
        pre.right_pointer[0] = column_head_i
        pre = column_head_i

    # 把每一个单元格插入到十字双向链表
    # print("正在把每一个单元格插入到十字双向链表：")
    for cell_node in all_table_node:
        # print("正在插入节点：", cell_node.text)
        # print("列：", cell_node.colspan)
        # print("行：", cell_node.rowspan)
        # print("cell_node.left_pointer:", cell_node.left_pointer)
        # print("cell_node.right_pointer:", cell_node.right_pointer)
        # print("cell_node.up_pointer:", cell_node.up_pointer)
        # print("cell_node.down_pointer:", cell_node.down_pointer)
        left_index, right_index = cell_node.colspan[0], cell_node.colspan[1]
        up_index, down_index = cell_node.rowspan[0], cell_node.rowspan[1]

        # 插入到水平双向链表
        all_left_pre: Set[Node] = set(rows_head[up_index - 1:down_index])
        tag = True
        while tag:
            tag = False
            all_pre_temp: Set[Node] = set()
            for i_pre in all_left_pre:
                i_pre_all_right_node: List[Node] = i_pre.right_pointer[
                                                   max(i_pre.rowspan[0], up_index): min(i_pre.rowspan[1],
                                                                                        down_index) + 1]
                for j_right_node in i_pre_all_right_node:
                    if not j_right_node:
                        all_pre_temp.add(i_pre)
                    else:
                        if j_right_node.colspan[1] < left_index:
                            all_pre_temp.add(j_right_node)
                            # tag = True
            all_pre_temp_temp: List[Node] = list(all_pre_temp)[:]
            for i, i_all_pre_temp_temp in enumerate(all_pre_temp_temp):
                for j, j_all_pre_temp_temp in enumerate(all_pre_temp_temp):
                    if i == j:
                        continue
                    i_all_pre_temp_temp_up_index, i_all_pre_temp_temp_down_index = max(i_all_pre_temp_temp.rowspan[0],
                                                                                       up_index), min(
                        i_all_pre_temp_temp.rowspan[1], down_index)
                    j_all_pre_temp_temp_up_index, j_all_pre_temp_temp_down_index = max(j_all_pre_temp_temp.rowspan[0],
                                                                                       up_index), min(
                        j_all_pre_temp_temp.rowspan[1], down_index)
                    if i_all_pre_temp_temp_up_index >= j_all_pre_temp_temp_up_index and i_all_pre_temp_temp_down_index <= j_all_pre_temp_temp_down_index:
                        if i_all_pre_temp_temp.colspan[1] < j_all_pre_temp_temp.colspan[0]:
                            all_pre_temp.discard(i_all_pre_temp_temp)
                        else:
                            all_pre_temp.discard(j_all_pre_temp_temp)
                        continue
            for i_all_pre_temp in all_pre_temp:
                if i_all_pre_temp not in all_left_pre:
                    tag = True
            if tag:
                all_left_pre = all_pre_temp
        all_right_next: Set[Node] = set()
        for j_pre in all_left_pre:
            all_right_next.update(j_pre.right_pointer[up_index: down_index + 1])
        for j_pre in all_left_pre:
            j_pre_up_index, j_pre_down_index = max(j_pre.rowspan[0], up_index), min(j_pre.rowspan[1], down_index)
            # print("j_pre_up_index, j_pre_down_index：",j_pre_up_index, j_pre_down_index)
            for k in range(j_pre_up_index, j_pre_down_index + 1):
                # print("k:",k)
                if j_pre.right_pointer[k] not in all_left_pre:
                    cell_node.left_pointer[k] = j_pre
                    j_pre.right_pointer[k] = cell_node
        for j_next in all_right_next:
            if j_next:
                j_next_up_index, j_next_down_index = (max(j_next.rowspan[0], up_index),
                                                      min(j_next.rowspan[1], down_index))
                for k in range(j_next_up_index, j_next_down_index + 1):
                    if j_next.left_pointer[k] not in all_right_next:
                        cell_node.right_pointer[k] = j_next
                        j_next.left_pointer[k] = cell_node

        # 插入到垂直双向链表
        all_up_pre: Set[Node] = set(columns_head[left_index - 1: right_index])
        tag = True
        while tag:
            tag = False
            all_pre_temp: Set[Node] = set()
            for i_pre in all_up_pre:
                i_pre_all_down_node: List[Node] = i_pre.down_pointer[
                                                  max(i_pre.colspan[0], left_index): min(i_pre.colspan[1],
                                                                                         right_index) + 1]
                for j_down_node in i_pre_all_down_node:
                    if not j_down_node:
                        all_pre_temp.add(i_pre)
                    else:
                        all_pre_temp.add(j_down_node)
            all_pre_temp_temp: List[Node] = list(all_pre_temp)[:]
            for i, i_all_pre_temp_temp in enumerate(all_pre_temp_temp):
                for j, j_all_pre_temp_temp in enumerate(all_pre_temp_temp):
                    if i == j:
                        continue
                    i_all_pre_temp_temp_left_index, i_all_pre_temp_temp_right_index = max(
                        i_all_pre_temp_temp.colspan[0],
                        left_index), min(
                        i_all_pre_temp_temp.colspan[1], right_index)
                    j_all_pre_temp_temp_left_index, j_all_pre_temp_temp_right_index = max(
                        j_all_pre_temp_temp.colspan[0],
                        left_index), min(
                        j_all_pre_temp_temp.colspan[1], right_index)
                    if i_all_pre_temp_temp_left_index >= j_all_pre_temp_temp_left_index and i_all_pre_temp_temp_right_index <= j_all_pre_temp_temp_right_index:
                        if i_all_pre_temp_temp.rowspan[1] < j_all_pre_temp_temp.rowspan[0]:
                            all_pre_temp.discard(i_all_pre_temp_temp)
                        else:
                            all_pre_temp.discard(j_all_pre_temp_temp)
                        continue
            for i_all_pre_temp in all_pre_temp:
                if i_all_pre_temp not in all_up_pre:
                    tag = True
            if tag:
                all_up_pre = all_pre_temp

        all_down_next: Set[Node] = set()
        for j_pre in all_up_pre:
            all_down_next.update(j_pre.down_pointer[left_index: right_index + 1])

        for j_pre in all_up_pre:
            j_pre_left_index, j_pre_right_index = max(j_pre.colspan[0], left_index), min(j_pre.colspan[1], right_index)
            for k in range(j_pre_left_index, j_pre_right_index + 1):
                if j_pre.down_pointer[k] not in all_up_pre:
                    cell_node.up_pointer[k] = j_pre
                    j_pre.down_pointer[k] = cell_node

        for j_next in all_down_next:
            if j_next:
                j_next_left_index, j_next_right_index = (max(j_next.colspan[0], left_index),
                                                         min(j_next.colspan[1], right_index))
                for k in range(j_next_left_index, j_next_right_index + 1):
                    if j_next.left_pointer[k] not in all_down_next:
                        cell_node.down_pointer[k] = j_next
                        j_next.up_pointer[k] = cell_node
    # print("构建完十字双向链表")
    return all_table_node,row_column_head,rows_head,columns_head


def have_next_level_head(i_node:Node, direct:str):
    if direct == 'right':
        all_right_node:List[Node]=i_node.right_pointer[i_node.rowspan[0]:i_node.rowspan[1]+1]
        if len(set(all_right_node))==1:
            return False
        if all_right_node[0].rowspan[0]!=i_node.rowspan[0] or all_right_node[-1].rowspan[1]!=i_node.rowspan[1]:
            return False
        return True
    elif direct == 'down':
        all_down_node: List[Node] = i_node.down_pointer[i_node.colspan[0]:i_node.colspan[1] + 1]
        if len(set(all_down_node)) == 1:
            return False
        if all_down_node[0].colspan[0] != i_node.colspan[0] or all_down_node[-1].colspan[1] != i_node.colspan[1]:
            return False
        return True


def kv_amend(simple_table: List):
    left_index, right_index = simple_table[0]["colspan"][0], simple_table[0]["colspan"][1]
    up_index, down_index = simple_table[0]["rowspan"][0], simple_table[0]["rowspan"][1]
    for cell in simple_table:
        left_index, right_index = min(left_index, cell["colspan"][0]), max(right_index, cell["colspan"][1])
        up_index, down_index = min(up_index, cell["rowspan"][0]), max(down_index, cell["rowspan"][1])
    one_level_head = None
    for i, cell in enumerate(simple_table):
        if cell["rowspan"] == [up_index, down_index] and cell["colspan"][0] == left_index:
            one_level_head = cell
            one_level_head["node_type"]="key"
            del simple_table[i]
            break
        if cell["colspan"] == [left_index, right_index] and cell["rowspan"][0] == up_index:
            one_level_head = cell
            one_level_head["node_type"] = "key"
            del simple_table[i]
            break

    left_index = simple_table[0]["colspan"][0]
    up_index = simple_table[0]["rowspan"][0]
    for cell in simple_table:
        left_index = min(left_index, cell["colspan"][0])
        up_index = min(up_index, cell["rowspan"][0])
    for cell in simple_table:
        cell["colspan"][0] -= left_index
        cell["rowspan"][0] -= up_index
        cell["colspan"][0] -= left_index
        cell["rowspan"][0] -= up_index
    all_table_node, row_column_head, rows_head, columns_head=create_cross_list(simple_table)

    # 根据表格结构判断表头是否在左边
    left_is_head=True
    left_node:Set[Node]=set()
    left_all_head_node:Set[Node]=set()
    for i,i_row_head in enumerate(rows_head):
        left_node.add(i_row_head.right_pointer[i+1])
        left_all_head_node.add(i_row_head.right_pointer[i+1])
    left_node_list = list(left_node)
    if not left_node_list[0].right_pointer[left_node_list[0].rowspan[0]]:
        left_is_head = False
    while True:
        if all([i_left_node.colspan[1]==list(left_node)[0].colspan[1] for i_left_node in left_node]):
            if not left_node_list[0].right_pointer[left_node_list[0].rowspan[0]]:
                left_is_head = False
                break
            if all([have_next_level_head(i_left_node,"right") for i_left_node in left_node]):
                for i_left_node in left_node:
                    left_node_temp: Set[Node] = set()
                    left_node_temp.update(set(i_left_node.right_pointer[i_left_node.rowspan[0]:i_left_node.rowspan[1]+1]))
                    left_node=left_node_temp
                    left_all_head_node.update(left_node)
            else:
                up_index_list=[i_left_node.rowspan[0] for i_left_node in left_node]
                down_index_list=[i_left_node.rowspan[1] for i_left_node in left_node]
                left_node_temp: Set[Node] = set()
                for i_left_node in left_node:
                    left_node_temp.update(set(i_left_node.right_pointer[i_left_node.rowspan[0]:i_left_node.rowspan[1]+1]))
                left_node:Set[Node]=set()
                for i_left_node_temp in left_node_temp:
                    if i_left_node_temp:
                        left_node.add(i_left_node_temp)
                if left_node:
                    left_is_head = False
                while left_node:
                    random_element:Node=random.choice(list(left_node))
                    if random_element.rowspan[0] not in up_index_list or random_element.rowspan[1] not in down_index_list:
                        left_is_head = False
                        break
                    for i_random_element_right_node in set(random_element.right_pointer[random_element.rowspan[0]:random_element.rowspan[1] + 1]):
                        if i_random_element_right_node:
                            left_node.add(i_random_element_right_node)
                    left_node.discard(random_element)
                left_is_head=True
        else:
            min_left_node = min(list(left_node), key=lambda obj: obj.colspan[1])
            if have_next_level_head(min_left_node,"right"):
                left_node.update(set(min_left_node.right_pointer[min_left_node.rowspan[0]:min_left_node.rowspan[1]+1]))
                left_node.discard(min_left_node)
                left_all_head_node.update(left_node)
            else:
                left_is_head = False

    # 根据表格结构判断表头是否在上边
    up_is_head = True
    up_node: Set[Node] = set()
    up_all_head_node: Set[Node] = set()
    for i, i_row_head in enumerate(rows_head):
        up_node.add(i_row_head.down_pointer[i + 1])
        up_all_head_node.add(i_row_head.down_pointer[i + 1])
    up_node_list = list(up_node)
    if not up_node_list[0].down_pointer[up_node_list[0].colspan[0]]:
        up_is_head = False
    while True:
        if all([i_up_node.rowspan[1] == list(up_node)[0].rowspan[1] for i_up_node in up_node]):
            if not up_node_list[0].down_pointer[up_node_list[0].colspan[0]]:
                up_is_head = False
                break
            if all([have_next_level_head(i_up_node, "down") for i_up_node in up_node]):
                for i_up_node in up_node:
                    up_node_temp: Set[Node] = set()
                    up_node_temp.update(
                        set(i_up_node.down_pointer[i_up_node.colspan[0]:i_up_node.colspan[1] + 1]))
                    up_node = up_node_temp
                    up_all_head_node.update(up_node)
            else:
                up_index_list = [i_up_node.colspan[0] for i_up_node in up_node]
                down_index_list = [i_up_node.colspan[1] for i_up_node in up_node]
                up_node_temp: Set[Node] = set()
                for i_up_node in up_node:
                    up_node_temp.update(
                        set(i_up_node.down_pointer[i_up_node.colspan[0]:i_up_node.colspan[1] + 1]))
                up_node: Set[Node] = set()
                for i_up_node_temp in up_node_temp:
                    if i_up_node_temp:
                        up_node.add(i_up_node_temp)
                if up_node:
                    up_is_head = False
                while up_node:
                    random_element: Node = random.choice(list(up_node))
                    if random_element.colspan[0] not in up_index_list or random_element.colspan[
                        1] not in down_index_list:
                        up_is_head = False
                        break
                    for i_random_element_down_node in set(
                            random_element.down_pointer[random_element.colspan[0]:random_element.colspan[1] + 1]):
                        if i_random_element_down_node:
                            up_node.add(i_random_element_down_node)
                    up_node.discard(random_element)
                up_is_head = True
        else:
            min_up_node = min(list(up_node), key=lambda obj: obj.rowspan[1])
            if have_next_level_head(min_up_node, "down"):
                up_node.update(
                    set(min_up_node.down_pointer[min_up_node.colspan[0]:min_up_node.colspan[1] + 1]))
                up_node.discard(min_up_node)
                up_all_head_node.update(up_node)
            else:
                up_is_head = False
    if left_is_head and not up_is_head:
        head_nodes=left_all_head_node
    elif not left_is_head and up_is_head:
        head_nodes=up_all_head_node
        pass
    elif left_is_head and up_is_head:
        left_node: Set[Node] = set()
        for i, i_row_head in enumerate(rows_head):
            left_node.add(i_row_head.right_pointer[i + 1])
        up_node: Set[Node] = set()
        for i, i_row_head in enumerate(rows_head):
            up_node.add(i_row_head.down_pointer[i + 1])
        if Counter(i_left_node.node_type for i_left_node in left_node)["key"]>Counter(i_up_node.node_type for i_up_node in up_node)["key"]:
            head_nodes=left_node

        else:
            head_nodes = up_node
    else:
        head_nodes = []
    for cell_node in all_table_node:
        if cell_node in head_nodes:
            cell_node.node_type = "key"
        else:
            cell_node.node_type = "value"

    amended_table=[]
    if one_level_head:
        amended_table.append(one_level_head)
    for cell_node in all_table_node:
        temp = {}
        temp["text"] = cell_node.text
        temp["colspan"] = cell_node.colspan
        temp["rowspan"] = cell_node.rowspan
        temp["node_type"] = cell_node.node_type
        amended_table.append(temp)
    return amended_table



        









