import json
from tools.node import Node
from typing import List, Set

with open("test.json", "r", encoding='utf-8') as f:
    table_dict = json.load(f)

all_table_node: List[Node] = []
table_rows, table_columns = 0, 0
key_num, value_num = 0, 0
for one_row in table_dict['trs']:
    all_cells_of_row = one_row['tds']
    for cell in all_cells_of_row:
        left_index, right_index = cell['colspan'][0], cell['colspan'][1]
        up_index, down_index = cell['rowspan'][0], cell['rowspan'][1]
        table_columns = right_index if table_columns < right_index else table_columns
        table_rows = down_index if table_rows < down_index else table_rows
        if cell['node_type'] == "key":
            key_num = key_num + 1
        else:
            value_num = value_num + 1

        created_node = Node(context=cell['context'], colspan=cell['colspan'], rowspan=cell['rowspan'],
                            up_pointer=[None] * (table_rows + 1),
                            down_pointer=[None] * (table_rows + 1),
                            left_pointer=[None] * (table_columns + 1),
                            right_pointer=[None] * (table_columns + 1),
                            node_type=cell['node_type'])

        created_node.set_of_affiliation.add(created_node)
        all_table_node.append(created_node)

row_column_head = Node(context="", colspan=[0, 0], rowspan=[0, 0], up_pointer=[None], down_pointer=[None],
                       left_pointer=[None], right_pointer=[None], node_type="row_column_head")

pre = row_column_head
rows_head = []
for i in range(table_rows):
    row_head_i = Node(context="", colspan=[0, 0], rowspan=[i + 1, i + 1], up_pointer=[None] * (table_rows + 1),
                      down_pointer=[None] * (table_rows + 1),
                      left_pointer=[None] * (table_columns + 1), right_pointer=[None] * (table_columns + 1),
                      node_type='rows_head')
    row_head_i.up_pointer[0] = pre
    rows_head.append(row_head_i)
    pre.down_pointer[0] = row_head_i
    pre = row_head_i

pre = row_column_head
columns_head = []
for i in range(table_columns):
    column_head_i = Node(context="", colspan=[i + 1, i + 1], rowspan=[0, 0], up_pointer=[None] * (table_rows + 1),
                         down_pointer=[None] * (table_rows + 1),
                         left_pointer=[None] * (table_columns + 1), right_pointer=[None] * (table_columns + 1),
                         node_type="columns_head")
    column_head_i.left_pointer[0] = pre
    columns_head.append(column_head_i)
    pre.right_pointer[0] = column_head_i
    pre = column_head_i

for cell_node in all_table_node:

    left_index, right_index = cell_node.colspan[0], cell_node.colspan[1]
    up_index, down_index = cell_node.rowspan[0], cell_node.rowspan[1]

    # 插入到水平双向链表
    all_left_pre: Set[Node] = set(rows_head[up_index - 1:down_index])
    tag = True
    while tag:
        tag = False
        all_pre_temp: Set[Node] = set()
        for i_pre in all_left_pre:
            if not i_pre:
                all_pre_temp.add(i_pre)
            else:
                i_pre_all_right_node: List[Node] = i_pre.right_pointer[up_index: down_index + 1]
                for j_right_node in i_pre_all_right_node:
                    if not j_right_node:
                        all_pre_temp.add(i_pre)
                    else:
                        if j_right_node.colspan[1] < left_index:
                            all_pre_temp.add(j_right_node)
                            tag = True
        if tag:
            all_left_pre = all_pre_temp

    all_right_next: Set[Node] = set()
    for j_pre in all_left_pre:
        all_right_next.update(j_pre.right_pointer[up_index: down_index + 1])

    for j_pre in all_left_pre:
        j_pre_up_index, j_pre_down_index = max(j_pre.rowspan[0], up_index), min(j_pre.rowspan[1], down_index)
        cell_node.left_pointer[j_pre_up_index:j_pre_down_index + 1] = [j_pre] * (j_pre_down_index - j_pre_up_index + 1)
        j_pre.right_pointer[j_pre_up_index:j_pre_down_index + 1] = [cell_node] * (j_pre_down_index - j_pre_up_index + 1)

    for j_next in all_right_next:
        if not j_next:
            j_next_up_index, j_next_down_index = (max(j_next.rowspan[0], up_index),
                                                  min(j_next.rowspan[1], down_index))
            cell_node.right_pointer[j_next_up_index: j_next_down_index + 1] = [j_next] * (
                    j_next_down_index - j_next_up_index + 1)
            j_next.left_pointer[j_next_up_index: j_next_down_index + 1] = [cell_node] * (
                    j_next_down_index - j_next_up_index + 1)

    # 插入到垂直双向链表
    all_up_pre: Set[Node] = set(columns_head[left_index - 1: right_index])
    tag = True
    while tag:
        tag = False
        all_pre_temp: Set[Node] = set()
        for i_pre in all_up_pre:
            if not i_pre:
                all_pre_temp.add(i_pre)
            else:
                i_pre_all_down_node: List[Node] = i_pre.down_pointer[left_index: right_index + 1]
                for j_down_node in i_pre_all_down_node:
                    if not j_down_node:
                        all_pre_temp.add(i_pre)
                    else:
                        if j_down_node.rowspan[1] < up_index:
                            all_pre_temp.add(j_down_node)
                            tag = True
        if tag:
            all_up_pre = all_pre_temp

    all_down_next: Set[Node] = set()
    for j_pre in all_up_pre:
        all_down_next.update(j_pre.down_pointer[left_index: right_index + 1])

    for j_pre in all_up_pre:
        j_pre_left_index, j_pre_right_index = max(j_pre.colspan[0], left_index), min(j_pre.colspan[1], right_index)
        cell_node.up_pointer[j_pre_left_index:j_pre_right_index + 1] = [j_pre] * (
                j_pre_right_index - j_pre_left_index + 1)
        j_pre.down_pointer[j_pre_left_index:j_pre_right_index + 1] = [cell_node] * (
                j_pre_right_index - j_pre_left_index + 1)

    for j_next in all_down_next:
        if not j_next:
            j_next_left_index, j_next_right_index = (max(j_next.colspan[0], left_index),
                                                     min(j_next.colspan[1], right_index))
            cell_node.down_pointer[j_next_left_index: j_next_right_index + 1] = [j_next] * (
                    j_next_right_index - j_next_left_index + 1)
            j_next.up_pointer[j_next_left_index: j_next_right_index + 1] = [cell_node] * (
                    j_next_right_index - j_next_left_index + 1)

handled_key_num = 0
last_handled_key_num = -1
handled_value_num = 0
last_handled_value_num = -1

while not (last_handled_value_num == handled_value_num and last_handled_key_num == handled_key_num):
    # 处理key
    while key_num > handled_key_num > last_handled_key_num:
        last_handled_key_num = handled_key_num
        for i in range(1, table_rows + 1):
            i_row_j_col_node: Node = rows_head[i - 1].right_pointer[i]
            while i_row_j_col_node.right_pointer[i]:
                if i_row_j_col_node.visited or i_row_j_col_node.node_type == "value":
                    i_row_j_col_node = i_row_j_col_node.right_pointer[i]
                    continue

                current_down_all_node: List[Node] = i_row_j_col_node.down_pointer[
                                                    i_row_j_col_node.colspan[0]:i_row_j_col_node.colspan[1] + 1]
                current_down_all_node_left_index, current_down_all_node_right_index = current_down_all_node[0].colspan[
                    0], \
                    current_down_all_node[-1].colspan[1]
                if current_down_all_node_left_index == i_row_j_col_node.colspan[
                    0] and current_down_all_node_right_index == \
                        i_row_j_col_node.colspan[1]:
                    if len(current_down_all_node) == 1:
                        if current_down_all_node[0].node_type == "key":
                            down_nodes_may_merge = False
                        elif current_down_all_node[0].visited:
                            down_nodes_may_merge = False
                        else:
                            down_nodes_may_merge = True
                    else:
                        down_nodes_may_merge = True
                else:
                    down_nodes_may_merge = False

                current_right_all_node: List[Node] = i_row_j_col_node.right_pointer[
                                                     i_row_j_col_node.rowspan[0]:i_row_j_col_node.rowspan[1] + 1]
                current_right_all_node_up_index, current_right_all_node_down_index = current_right_all_node[0].rowspan[
                    0], \
                    current_right_all_node[-1].rowspan[1]
                if current_right_all_node_up_index == i_row_j_col_node.rowspan[
                    0] and current_right_all_node_down_index == \
                        i_row_j_col_node.rowspan[1]:
                    if len(current_right_all_node) == 1:
                        if current_right_all_node[0].node_type == "key":
                            right_nodes_may_merge = False
                        elif current_right_all_node[0].visited:
                            right_nodes_may_merge = False
                        else:
                            right_nodes_may_merge = True
                    else:
                        right_nodes_may_merge = True
                else:
                    right_nodes_may_merge = False

                if down_nodes_may_merge and not right_nodes_may_merge:
                    for i_current_down_all_node in current_down_all_node:
                        i_row_j_col_node.set_of_affiliation = i_row_j_col_node.set_of_affiliation | i_current_down_all_node.set_of_affiliation
                    for i_current_down_all_node in current_down_all_node:
                        i_current_down_all_node.set_of_affiliation = i_row_j_col_node.set_of_affiliation
                    i_row_j_col_node.visited = True
                    i_row_j_col_node.merge_method = "vertical"
                    handled_key_num += 1
                    pass
                elif not down_nodes_may_merge and right_nodes_may_merge:
                    for i_current_right_all_node in current_right_all_node:
                        i_row_j_col_node.set_of_affiliation = i_row_j_col_node.set_of_affiliation | i_current_right_all_node.set_of_affiliation
                    for i_current_right_all_node in current_right_all_node:
                        i_current_right_all_node.set_of_affiliation = i_row_j_col_node.set_of_affiliation
                    i_row_j_col_node.visited = True
                    i_row_j_col_node.merge_method = "horizontal"
                    handled_key_num += 1
                    pass
                i_row_j_col_node: Node = i_row_j_col_node.right_pointer[i]

    # 处理value
    while value_num > handled_value_num > last_handled_value_num:
        last_handled_value_num = handled_value_num
        for i in range(1, table_rows + 1):
            i_row_j_col_node: Node = rows_head[i - 1].right_pointer[i]
            while i_row_j_col_node.right_pointer[i]:
                if i_row_j_col_node.visited or i_row_j_col_node.node_type == "key":
                    i_row_j_col_node = i_row_j_col_node.right_pointer[i]
                    continue
                if len(i_row_j_col_node.set_of_affiliation) > 1:
                    i_row_j_col_node.visited = True
                    handled_value_num += 1
                    i_row_j_col_node = i_row_j_col_node.right_pointer[i]
                    continue

                current_up_all_node: List[Node] = i_row_j_col_node.up_pointer[
                                                  i_row_j_col_node.colspan[0]:i_row_j_col_node.colspan[1] + 1]
                current_up_all_node_left_index, current_up_all_node_right_index = current_up_all_node[0].colspan[0], \
                    current_up_all_node[-1].colspan[1]
                if current_up_all_node_left_index == i_row_j_col_node.colspan[0] and current_up_all_node_right_index == \
                        i_row_j_col_node.colspan[1]:
                    if len(current_up_all_node) == 1:
                        if current_up_all_node[0].node_type == "key":
                            if current_up_all_node[0].visited:
                                up_nodes_may_merge = False
                            else:
                                up_nodes_may_merge = True
                        else:
                            if current_up_all_node[0].visited:
                                if current_up_all_node[0].merge_method == "vertical":
                                    up_nodes_may_merge = True
                                else:
                                    up_nodes_may_merge = False
                            else:
                                up_nodes_may_merge = False
                    else:
                        up_nodes_may_merge = False
                else:
                    up_nodes_may_merge = False

                current_left_all_node: List[Node] = i_row_j_col_node.left_pointer[
                                                    i_row_j_col_node.rowspan[0]:i_row_j_col_node.rowspan[1] + 1]
                current_left_all_node_up_index, current_left_all_node_down_index = current_left_all_node[0].rowspan[0], \
                    current_left_all_node[-1].rowspan[1]
                if current_up_all_node_left_index == i_row_j_col_node.rowspan[0] and current_left_all_node_down_index == \
                        i_row_j_col_node.rowspan[1]:
                    if len(current_left_all_node) == 1:
                        if current_left_all_node[0].node_type == "key":
                            if current_left_all_node[0].visited:
                                left_nodes_may_merge = False
                            else:
                                left_nodes_may_merge = True
                        else:
                            if current_left_all_node[0].visited:
                                if current_up_all_node[0].merge_method == "horizontal":
                                    left_nodes_may_merge = True
                                else:
                                    left_nodes_may_merge = False
                            else:
                                left_nodes_may_merge = False
                    else:
                        left_nodes_may_merge = False
                else:
                    left_nodes_may_merge = False

                if up_nodes_may_merge and not left_nodes_may_merge:
                    temp_set = current_up_all_node[0].set_of_affiliation | i_row_j_col_node.set_of_affiliation
                    current_up_all_node[0].set_of_affiliation = temp_set
                    i_row_j_col_node.set_of_affiliation = temp_set
                    i_row_j_col_node.visited = True
                    handled_value_num += 1
                    if current_up_all_node[0].node_type == "key":
                        current_up_all_node[0].visited = True
                        handled_key_num += 1
                        last_handled_key_num = handled_key_num

                if not up_nodes_may_merge and left_nodes_may_merge:
                    temp_set = current_left_all_node[0].set_of_affiliation | i_row_j_col_node.set_of_affiliation
                    current_left_all_node[0].set_of_affiliation = temp_set
                    i_row_j_col_node.set_of_affiliation = temp_set
                    i_row_j_col_node.visited = True
                    handled_value_num += 1
                    if current_left_all_node[0].node_type == "key":
                        current_left_all_node[0].visited = True
                        handled_key_num += 1
                        last_handled_key_num = handled_key_num

                    for i_current_down_all_node in current_down_all_node:
                        temp_set = temp_set | i_current_down_all_node.set_of_affiliation
                    i_row_j_col_node.set_of_affiliation = temp_set
                    for i_current_down_all_node in current_down_all_node:
                        i_current_down_all_node.set_of_affiliation = temp_set
                    i_row_j_col_node.visited = True
                    i_row_j_col_node.merge_method = "vertical"
                    handled_key_num += 1
                    pass
                elif not down_nodes_may_merge and right_nodes_may_merge:
                    temp_set = set()
                    temp_set.add(i_row_j_col_node)
                    for i_current_right_all_node in current_right_all_node:
                        temp_set = temp_set | i_current_right_all_node.set_of_affiliation
                    i_row_j_col_node.set_of_affiliation = temp_set
                    for i_current_right_all_node in current_right_all_node:
                        i_current_right_all_node.set_of_affiliation = temp_set
                    i_row_j_col_node.visited = True
                    i_row_j_col_node.merge_method = "horizontal"
                    handled_key_num += 1
                    pass
                i_row_j_col_node: Node = i_row_j_col_node.right_pointer[i]

segmented_table = []
for cell_node in all_table_node:
    for segment_i in segmented_table:
        if cell_node in segment_i:
            break
    segmented_table.append(cell_node.set_of_affiliation)

