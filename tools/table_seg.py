import json
from tools.node import Node
from typing import List, Set
from tools.create_cross_list import create_cross_list


def table_seg(table_dict) -> (List[Set[Node]], List[Node], List[Node]):
    """
    对复杂表格进行分块
    :param table_dict: 表格的字典表示，其中每个节点的类型已知
    :return:
    segmented_table:返回一个列表，其中的每一个元素是一个子表中所有的单元格组成的集合
    all_table_node:返回一个列表，其中的每一个元素是输入表格中的一个单元格
    rows_head:返回复杂表格构成的双向十字链表以行进行索引的头指针列表
    """
    all_table_node: List[Node]
    table_rows, table_columns = 0, 0
    key_num, value_num = 0, 0

    # 计算表格的行数和列数

    all_cells = table_dict['cells']
    for cell in all_cells:
        left_index, right_index = cell['colspan'][0], cell['colspan'][1]
        up_index, down_index = cell['rowspan'][0], cell['rowspan'][1]
        table_columns = right_index if table_columns < right_index else table_columns
        table_rows = down_index if table_rows < down_index else table_rows
        if cell['node_type'] == "key":
            key_num = key_num + 1
        else:
            value_num = value_num + 1

    all_table_node, row_column_head, rows_head, columns_head = create_cross_list(table_dict['cells'])

    # print("table_rows:", table_rows)
    # print("table_columns:", table_columns)

    # print("构建完十字双向链表")

    # 对表格进行分块
    handled_key_num = 0
    last_handled_key_num = -1
    handled_value_num = 0
    last_handled_value_num = -1
    # 判断最近一轮是否有过单元格合并
    while last_handled_value_num < handled_value_num or last_handled_key_num < handled_key_num:
        # print("last_handled_key_num,last_handled_value_num:", last_handled_key_num, last_handled_value_num)
        # print("handled_key_num,handled_value_num:", handled_key_num, handled_value_num)
        # temp_last_handled_key_num = last_handled_key_num
        # temp_last_handled_value_num = last_handled_value_num
        last_handled_key_num = handled_key_num
        last_handled_value_num = handled_value_num

        # 处理key
        tag = True
        while key_num > handled_key_num and tag:
            tag = False
            for i in range(1, table_rows + 1):
                i_row_j_col_node: Node = rows_head[i - 1].right_pointer[i]
                while i_row_j_col_node:
                    # print("正在处理节点：", i_row_j_col_node.text)
                    # print("列：", i_row_j_col_node.colspan)
                    # print("行：", i_row_j_col_node.rowspan)
                    # print("cell_node.left_pointer:", i_row_j_col_node.left_pointer)
                    # print("cell_node.right_pointer:", i_row_j_col_node.right_pointer)
                    # print("cell_node.up_pointer:", i_row_j_col_node.up_pointer)
                    # print("cell_node.down_pointer:", i_row_j_col_node.down_pointer)
                    if i_row_j_col_node.visited or i_row_j_col_node.node_type == "value":
                        i_row_j_col_node = i_row_j_col_node.right_pointer[i]
                        continue
                    # 判断属性为key的结点是否有可能和下方节点合并
                    current_down_all_node_temp: List[Node] = i_row_j_col_node.down_pointer[
                                                             i_row_j_col_node.colspan[0]:i_row_j_col_node.colspan[
                                                                                             1] + 1]
                    current_down_all_node: List[Node] = []
                    for i_current_down_all_node_temp in current_down_all_node_temp:
                        if i_current_down_all_node_temp not in current_down_all_node:
                            current_down_all_node.append(i_current_down_all_node_temp)
                    if all(i_current_down_all_node for i_current_down_all_node in current_down_all_node):
                        current_down_all_node_left_index, current_down_all_node_right_index = \
                            current_down_all_node[0].colspan[0], current_down_all_node[-1].colspan[1]
                        if current_down_all_node_left_index == i_row_j_col_node.colspan[
                            0] and current_down_all_node_right_index == i_row_j_col_node.colspan[1]:
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
                            if current_down_all_node_left_index <= i_row_j_col_node.colspan[
                                0] and current_down_all_node_right_index >= i_row_j_col_node.colspan[1]:
                                if len(current_down_all_node) == 1 and current_down_all_node[0].node_type == "value":
                                    current_down_node_all_up_node_temp: List[Node] = current_down_all_node[
                                                                                         0].up_pointer[
                                                                                     current_down_all_node[0].colspan[
                                                                                         0]:
                                                                                     current_down_all_node[0].colspan[
                                                                                         1] + 1]
                                    current_down_node_all_up_node: List[Node] = []
                                    for i_current_down_node_all_up_node_temp in current_down_node_all_up_node_temp:
                                        if i_current_down_node_all_up_node_temp not in current_down_node_all_up_node:
                                            current_down_node_all_up_node.append(i_current_down_node_all_up_node_temp)
                                    if all(i_current_down_node_all_up_node.node_type == "key" for
                                           i_current_down_node_all_up_node in current_down_node_all_up_node):
                                        if current_down_node_all_up_node[0].colspan[0] == \
                                                current_down_all_node[0].colspan[0] and \
                                                current_down_node_all_up_node[-1].colspan[1] == \
                                                current_down_all_node[0].colspan[1]:
                                            down_nodes_may_merge = True
                                        else:
                                            down_nodes_may_merge = False
                                    else:
                                        down_nodes_may_merge = False
                                else:
                                    down_nodes_may_merge = False
                            else:
                                down_nodes_may_merge = False
                    else:
                        down_nodes_may_merge = False
                    # 判断属性为key的结点是否有可能和右方节点合并
                    current_right_all_node_temp: List[Node] = i_row_j_col_node.right_pointer[
                                                              i_row_j_col_node.rowspan[0]:i_row_j_col_node.rowspan[
                                                                                              1] + 1]
                    current_right_all_node: List[Node] = []
                    for i_current_right_all_node_temp in current_right_all_node_temp:
                        if i_current_right_all_node_temp not in current_right_all_node:
                            current_right_all_node.append(i_current_right_all_node_temp)
                    if all(i_current_right_all_node for i_current_right_all_node in current_right_all_node):
                        current_right_all_node_up_index, current_right_all_node_down_index = \
                            current_right_all_node[0].rowspan[0], current_right_all_node[-1].rowspan[1]
                        if current_right_all_node_up_index == i_row_j_col_node.rowspan[
                            0] and current_right_all_node_down_index == i_row_j_col_node.rowspan[1]:
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
                            if current_right_all_node_up_index <= i_row_j_col_node.rowspan[
                                0] and current_right_all_node_down_index >= i_row_j_col_node.rowspan[1]:
                                if len(current_right_all_node) == 1 and current_right_all_node[0].node_type == "value":
                                    current_right_node_all_left_node_temp: List[Node] = current_right_all_node[
                                                                                            0].left_pointer[
                                                                                        current_right_all_node[
                                                                                            0].rowspan[
                                                                                            0]:
                                                                                        current_right_all_node[
                                                                                            0].rowspan[
                                                                                            1] + 1]
                                    current_right_node_all_left_node: List[Node] = []
                                    for i_current_right_node_all_left_node_temp in current_right_node_all_left_node_temp:
                                        if i_current_right_node_all_left_node_temp not in current_right_node_all_left_node:
                                            current_right_node_all_left_node.append(
                                                i_current_right_node_all_left_node_temp)
                                    if all(i_current_right_node_all_left_node.node_type == "key" for
                                           i_current_right_node_all_left_node in current_right_node_all_left_node):
                                        if current_right_node_all_left_node[0].rowspan[0] == \
                                                current_right_all_node[0].rowspan[0] and \
                                                current_right_node_all_left_node[-1].rowspan[1] == \
                                                current_right_all_node[0].rowspan[1]:
                                            right_nodes_may_merge = True
                                        else:
                                            right_nodes_may_merge = False
                                    else:
                                        right_nodes_may_merge = False
                                else:
                                    right_nodes_may_merge = False
                            else:
                                right_nodes_may_merge = False

                    else:
                        right_nodes_may_merge = False
                    # 如果属性为key的结点有可能和下方结点合并但一定不会和右方结点合并，则此时只能和下方结点进行合并
                    if down_nodes_may_merge and not right_nodes_may_merge:
                        temp_set = set()
                        temp_set.update(i_row_j_col_node.set_of_affiliation)
                        for i_current_down_all_node in current_down_all_node:
                            temp_set.update(i_current_down_all_node.set_of_affiliation)

                        for set_of_affiliation_i_node in list(i_row_j_col_node.set_of_affiliation):
                            set_of_affiliation_i_node.set_of_affiliation = set()
                            set_of_affiliation_i_node.set_of_affiliation.update(temp_set)
                        for i_current_down_all_node in current_down_all_node:
                            i_current_down_all_node.set_of_affiliation = set()
                            i_current_down_all_node.set_of_affiliation.update(temp_set)
                        i_row_j_col_node.visited = True
                        tag = True
                        i_row_j_col_node.merge_method = "vertical"
                        handled_key_num += 1
                        if len(current_down_all_node) > 1:
                            for i_current_down_all_node in current_down_all_node:
                                if i_current_down_all_node.node_type == "key":
                                    i_current_down_all_node.merge_method = "vertical"
                        else:
                            if current_down_all_node[0].node_type == "value":
                                current_down_all_node[0].merge_method = "vertical"
                                if not current_down_all_node[0].visited and current_down_all_node[0].colspan[0] == \
                                        i_row_j_col_node.colspan[0] and current_down_all_node[0].colspan[1] == \
                                        i_row_j_col_node.colspan[1]:
                                    current_down_all_node[0].visited = True
                                    handled_value_num += 1
                        pass
                    # 如果属性为key的结点有可能和右方结点合并但一定不会和下方结点合并，则此时只能和右方结点进行合并
                    elif not down_nodes_may_merge and right_nodes_may_merge:
                        temp_set = set()
                        temp_set.update(i_row_j_col_node.set_of_affiliation)
                        for i_current_right_all_node in current_right_all_node:
                            temp_set.update(i_current_right_all_node.set_of_affiliation)
                            # i_row_j_col_node.set_of_affiliation = i_row_j_col_node.set_of_affiliation | i_current_right_all_node.set_of_affiliation
                        for set_of_affiliation_i_node in list(i_row_j_col_node.set_of_affiliation):
                            set_of_affiliation_i_node.set_of_affiliation = set()
                            set_of_affiliation_i_node.set_of_affiliation.update(temp_set)
                        for i_current_right_all_node in current_right_all_node:
                            i_current_right_all_node.set_of_affiliation = set()
                            i_current_right_all_node.set_of_affiliation.update(temp_set)
                        i_row_j_col_node.visited = True
                        tag = True
                        i_row_j_col_node.merge_method = "horizontal"
                        handled_key_num += 1

                        if len(current_right_all_node) > 1:
                            for i_current_right_all_node in current_right_all_node:
                                if i_current_right_all_node.node_type == "key":
                                    i_current_right_all_node.merge_method = "horizontal"
                        else:
                            if current_right_all_node[0].node_type == "value":
                                current_right_all_node[0].merge_method = "horizontal"
                                if not current_right_all_node[0].visited and current_right_all_node[0].rowspan[0] == \
                                        i_row_j_col_node.rowspan[0] and current_right_all_node[0].rowspan[1] == \
                                        i_row_j_col_node.rowspan[1]:
                                    current_right_all_node[0].visited = True
                                    handled_value_num += 1
                        pass
                    i_row_j_col_node: Node = i_row_j_col_node.right_pointer[i]

        # 处理value
        tag = True
        while value_num > handled_value_num and tag:
            tag = False
            for i in range(1, table_rows + 1):
                i_row_j_col_node: Node = rows_head[i - 1].right_pointer[i]
                while i_row_j_col_node:
                    # print("正在处理节点：", i_row_j_col_node.text)
                    # print("列：", i_row_j_col_node.colspan)
                    # print("行：", i_row_j_col_node.rowspan)
                    # print("cell_node.left_pointer:", i_row_j_col_node.left_pointer)
                    # print("cell_node.right_pointer:", i_row_j_col_node.right_pointer)
                    # print("cell_node.up_pointer:", i_row_j_col_node.up_pointer)
                    # print("cell_node.down_pointer:", i_row_j_col_node.down_pointer)
                    if i_row_j_col_node.visited or i_row_j_col_node.node_type == "key":
                        i_row_j_col_node = i_row_j_col_node.right_pointer[i]
                        continue
                    # if len(i_row_j_col_node.set_of_affiliation) > 1:
                    #     i_row_j_col_node.visited = True
                    #     handled_value_num += 1
                    #     i_row_j_col_node = i_row_j_col_node.right_pointer[i]
                    #     continue
                    # 判断属性为value的结点是否有可能和上方节点合并
                    current_up_all_node_temp: List[Node] = i_row_j_col_node.up_pointer[
                                                           i_row_j_col_node.colspan[0]:i_row_j_col_node.colspan[1] + 1]
                    current_up_all_node: List[Node] = []
                    for i_current_up_all_node_temp in current_up_all_node_temp:
                        if i_current_up_all_node_temp not in current_up_all_node:
                            current_up_all_node.append(i_current_up_all_node_temp)
                    if all(i_current_up_all_node and i_current_up_all_node not in columns_head for i_current_up_all_node in current_up_all_node):
                        current_up_all_node_left_index, current_up_all_node_right_index = \
                            current_up_all_node[0].colspan[0], \
                                current_up_all_node[-1].colspan[1]
                        if current_up_all_node_left_index == i_row_j_col_node.colspan[
                            0] and current_up_all_node_right_index == i_row_j_col_node.colspan[1]:
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
                                if all(i_current_up_all_node.node_type == "value" for i_current_up_all_node in
                                       current_up_all_node):
                                    if all(
                                            i_current_up_all_node.merge_method == "vertical" and i_current_up_all_node.visited
                                            for i_current_up_all_node in current_up_all_node):
                                        up_nodes_may_merge = True
                                    else:
                                        up_nodes_may_merge = False
                                elif all(i_current_up_all_node.node_type == "key" for i_current_up_all_node in
                                         current_up_all_node):
                                    if not any(
                                            i_current_up_all_node.merge_method == "horizontal" for i_current_up_all_node
                                            in current_up_all_node):
                                        up_nodes_may_merge = True
                                    else:
                                        up_nodes_may_merge = False
                                else:
                                    up_nodes_may_merge = False
                        else:
                            if current_up_all_node_left_index <= i_row_j_col_node.colspan[
                                0] and current_up_all_node_right_index >= i_row_j_col_node.colspan[1]:
                                if all(i_current_up_all_node.node_type == "value" for i_current_up_all_node in
                                       current_up_all_node):
                                    up_nodes_may_merge = False
                                    current_up_all_key_node: List[Node] = []
                                    if all(
                                            i_current_up_all_node.merge_method == "vertical" and i_current_up_all_node.visited
                                            for i_current_up_all_node in current_up_all_node):
                                        for i_row in range(i_row_j_col_node.rowspan[1], 0, -1):
                                            current_up_all_key_node: List[Node] = []
                                            i_row_node = rows_head[i_row - 1]
                                            while i_row_node:
                                                # print(5)
                                                if i_row_j_col_node.colspan[0] <= i_row_node.colspan[0] <= \
                                                        i_row_j_col_node.colspan[1] or i_row_j_col_node.colspan[0] <= \
                                                        i_row_node.colspan[1] <= i_row_j_col_node.colspan[1]:
                                                    current_up_all_key_node.append(i_row_node)
                                                i_row_node=i_row_node.right_pointer[i_row]
                                            if any(i_current_up_all_key_node.node_type == "key" for
                                                   i_current_up_all_key_node in current_up_all_key_node):
                                                break
                                        if len(current_up_all_key_node) > 0 and all(
                                                i_current_up_all_key_node.node_type == "key" for
                                                i_current_up_all_key_node in current_up_all_key_node):
                                            if all(i_current_up_all_key_node.rowspan[1] ==
                                                   current_up_all_key_node[0].rowspan[1] for
                                                   i_current_up_all_key_node in current_up_all_key_node):
                                                if current_up_all_key_node[0].colspan[0]==i_row_j_col_node.colspan[0] and current_up_all_key_node[-1].colspan[1]==i_row_j_col_node.colspan[1]:
                                                    up_nodes_may_merge = True
                                    else:
                                        up_nodes_may_merge = False
                                else:
                                    up_nodes_may_merge = False
                            else:
                                up_nodes_may_merge = False
                    else:
                        up_nodes_may_merge = False

                    # 判断属性为value的结点是否有可能和左方节点合并
                    current_left_all_node_temp: List[Node] = i_row_j_col_node.left_pointer[
                                                             i_row_j_col_node.rowspan[0]:i_row_j_col_node.rowspan[
                                                                                             1] + 1]
                    current_left_all_node: List[Node] = []
                    for i_current_left_all_node_temp in current_left_all_node_temp:
                        if i_current_left_all_node_temp not in current_left_all_node:
                            current_left_all_node.append(i_current_left_all_node_temp)
                    if all(i_current_left_all_node and i_current_left_all_node not in rows_head for i_current_left_all_node in current_left_all_node):
                        current_left_all_node_up_index, current_left_all_node_down_index = \
                            current_left_all_node[0].rowspan[
                                0], current_left_all_node[-1].rowspan[1]
                        if current_left_all_node_up_index == i_row_j_col_node.rowspan[
                            0] and current_left_all_node_down_index == i_row_j_col_node.rowspan[1]:
                            if len(current_left_all_node) == 1:
                                if current_left_all_node[0].node_type == "key":
                                    if current_left_all_node[0].visited:
                                        left_nodes_may_merge = False
                                    else:
                                        left_nodes_may_merge = True
                                else:
                                    if current_left_all_node[0].visited:
                                        if current_left_all_node[0].merge_method == "horizontal":
                                            left_nodes_may_merge = True
                                        else:
                                            left_nodes_may_merge = False
                                    else:
                                        left_nodes_may_merge = False
                            else:
                                if all(i_current_left_all_node.node_type == "value" for i_current_left_all_node in
                                       current_left_all_node):
                                    if all(
                                            i_current_left_all_node.merge_method == "horizontal" and i_current_left_all_node.visited
                                            for i_current_left_all_node in current_left_all_node):
                                        left_nodes_may_merge = True
                                    else:
                                        left_nodes_may_merge = False
                                elif all(i_current_left_all_node.node_type == "key" for i_current_left_all_node in
                                         current_left_all_node):
                                    if not any(
                                            i_current_left_all_node.merge_method == "vertical" for
                                            i_current_left_all_node
                                            in current_left_all_node):
                                        left_nodes_may_merge = True
                                    else:
                                        left_nodes_may_merge = False
                                else:
                                    left_nodes_may_merge = False
                        else:

                            if current_left_all_node_up_index <= i_row_j_col_node.rowspan[
                                0] and current_left_all_node_down_index >= i_row_j_col_node.rowspan[1]:
                                if all(i_current_left_all_node.node_type == "value" for i_current_left_all_node in
                                       current_left_all_node):
                                    left_nodes_may_merge = False
                                    current_left_all_key_node: List[Node] = []
                                    if all(
                                            i_current_left_all_node.merge_method == "horizontal" and i_current_left_all_node.visited
                                            for i_current_left_all_node in current_left_all_node):
                                        for i_col in range(i_row_j_col_node.colspan[1], 0, -1):
                                            current_left_all_key_node: List[Node] = []
                                            i_col_node = columns_head[i_col - 1]
                                            while i_col_node:
                                                if i_row_j_col_node.rowspan[0] <= i_col_node.rowspan[0] <= \
                                                        i_row_j_col_node.rowspan[1] or i_row_j_col_node.rowspan[0] <= \
                                                        i_col_node.rowspan[1] <= i_row_j_col_node.rowspan[1]:
                                                    current_left_all_key_node.append(i_col_node)
                                                i_col_node = i_col_node.down_pointer[i_col]
                                            if any(i_current_left_all_key_node.node_type == "key" for
                                                   i_current_left_all_key_node in current_left_all_key_node):
                                                break

                                        if len(current_left_all_key_node) > 0 and all(
                                                i_current_left_all_key_node.node_type == "key" for
                                                i_current_left_all_key_node in current_left_all_key_node):

                                            if all(i_current_left_all_key_node.colspan[1] ==
                                                   current_left_all_key_node[0].colspan[1] for
                                                   i_current_left_all_key_node in current_left_all_key_node):
                                                if current_left_all_key_node[0].rowspan[0] == i_row_j_col_node.rowspan[0] and current_left_all_key_node[-1].rowspan[1] ==i_row_j_col_node.rowspan[1]:
                                                    left_nodes_may_merge = True
                                    else:
                                        left_nodes_may_merge = False
                                else:
                                    left_nodes_may_merge = False
                            else:
                                left_nodes_may_merge = False
                    else:
                        left_nodes_may_merge = False

                    if i_row_j_col_node.text=="Emily":
                        print(up_nodes_may_merge,left_nodes_may_merge)
                    # 如果属性为value的结点有可能和上方结点合并但一定不会和左方结点合并，则此时只能和上方结点进行合并
                    if up_nodes_may_merge and not left_nodes_may_merge:
                        temp_set: Set[Node] = set()
                        for i_current_up_all_node in current_up_all_node:
                            temp_set.update(i_current_up_all_node.set_of_affiliation)
                        temp_set.update(i_row_j_col_node.set_of_affiliation)
                        for i_temp_set in temp_set:
                            i_temp_set.set_of_affiliation = set()
                            i_temp_set.set_of_affiliation.update(temp_set)

                        i_row_j_col_node.visited = True
                        tag = True
                        handled_value_num += 1
                        i_row_j_col_node.merge_method = "vertical"
                        if all(i_current_up_all_node.node_type == "key" for i_current_up_all_node in
                               current_up_all_node):
                            for i_current_up_all_node in current_up_all_node:
                                if not i_current_up_all_node.visited:
                                    i_current_up_all_node.visited = True
                                    handled_key_num += 1
                                    i_current_up_all_node.merge_method = "vertical"
                    # 如果属性为value的结点有可能和左方结点合并但一定不会和上方结点合并，则此时只能和左方结点进行合并
                    elif not up_nodes_may_merge and left_nodes_may_merge:
                        temp_set: Set[Node] = set()
                        for i_current_left_all_node in current_left_all_node:
                            temp_set.update(i_current_left_all_node.set_of_affiliation)
                        temp_set.update(i_row_j_col_node.set_of_affiliation)
                        for i_temp_set in temp_set:
                            i_temp_set.set_of_affiliation = set()
                            i_temp_set.set_of_affiliation.update(temp_set)

                        i_row_j_col_node.visited = True
                        tag = True
                        handled_value_num += 1
                        i_row_j_col_node.merge_method = "horizontal"
                        if all(i_current_left_all_node.node_type == "key" for i_current_left_all_node in
                               current_left_all_node):
                            for i_current_left_all_node in current_left_all_node:
                                if not i_current_left_all_node.visited:
                                    i_current_left_all_node.visited = True
                                    handled_key_num += 1
                                    i_current_left_all_node.merge_method = "horizontal"

                    i_row_j_col_node: Node = i_row_j_col_node.right_pointer[i]

    segmented_table = []
    segmented_dict = {}
    for cell_node in all_table_node:
        # print("正在处理节点：", cell_node.text)
        # print("列：", cell_node.colspan)
        # print("行：", cell_node.rowspan)
        # print("cell_node.left_pointer:", cell_node.left_pointer)
        # print("cell_node.right_pointer:", cell_node.right_pointer)
        # print("cell_node.up_pointer:", cell_node.up_pointer)
        # print("cell_node.down_pointer:", cell_node.down_pointer)
        # print(cell_node.visited)
        if all((cell_node not in segment_i) for segment_i in segmented_table):
            segmented_table.append(cell_node.set_of_affiliation)
    for i, segment_i in enumerate(segmented_table):
        # print("---------------------------------------------------------------------------------------")
        # print("正在打印第{}个子表：".format(i + 1))
        segmented_dict['sub_table_{}'.format(i + 1)] = []
        for j, cell in enumerate(list(segment_i)):
            temp = {}
            temp["text"] = cell.text
            temp["colspan"] = cell.colspan
            temp["rowspan"] = cell.rowspan
            segmented_dict['sub_table_{}'.format(i + 1)].append(temp)
            # print("**************")
            # print("节点：", cell.text)
            # print("列：", cell.colspan)
            # print("行：", cell.rowspan)
            # print("cell_node.left_pointer:", cell.left_pointer)
            # print("cell_node.right_pointer:", cell.right_pointer)
            # print("cell_node.up_pointer:", cell.up_pointer)
            # print("cell_node.down_pointer:", cell.down_pointer)

    with open('./sub_tables.json', 'w', encoding='utf-8') as f:
        # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
        json.dump(segmented_dict, f, indent=4, ensure_ascii=False)
    return segmented_table, all_table_node, rows_head


if __name__ == '__main__':
    from tools.preprocess import any_format_to_json
    import random
    from tools.func import cmp_dict, cmp_node
    from functools import cmp_to_key
    gt_table, propositions = any_format_to_json(r"E:\code\table_handle\tools\11.xlsx")
    # print("----------------gt_table-------------")
    # print(gt_table)
    # random.shuffle(gt_table["cells"])
    # with open( "1.json", 'w',encoding='utf-8') as f:
    #     # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
    #     json.dump(gt_table, f, indent=4, ensure_ascii=False)
    # gt_table["cells"].sort(key=cmp_to_key(cmp_dict))
    # with open( "2.json", 'w',encoding='utf-8') as f:
    #     # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
    #     json.dump(gt_table, f, indent=4, ensure_ascii=False)
    all_table_node: List[Node]
    segmented_table, all_table_node, _ = table_seg(gt_table)
    for i_segmented_table in segmented_table:
        for j_cell in list(i_segmented_table):
            # print(j_cell.text,j_cell.visited,j_cell.merge_method,end="#")
            print(j_cell.text,end="#")

        print()

    # for cell in all_table_node:
    #     print("---------------------------------------------------")
    #     print(cell.text)
    #     for j_cell in list(cell.set_of_affiliation):
    #         print(j_cell.text, end="#")
    #     print()
