from tools.node import Node
from typing import List, Set
def create_cross_list(table: List):
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
    return all_table_node, row_column_head, rows_head, columns_head
