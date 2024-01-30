import json
from tools.node import Node
from typing import List, Set

# 读取表格的json文件
with open("test.json", "r", encoding='utf-8') as f:
    table_dict = json.load(f)

# 把表格中的每个单元格转换成Node类对象
all_table_node: List[Node] = []
table_rows, table_columns = 0, 0
key_num, value_num = 0, 0
# 计算表格的行数和列数
for one_row in table_dict['trs']:
    all_cells_of_row = one_row['tds']
    for cell in all_cells_of_row:
        left_index, right_index = cell['colspan'][0], cell['colspan'][1]
        up_index, down_index = cell['rowspan'][0], cell['rowspan'][1]
        table_columns = right_index if table_columns < right_index else table_columns
        table_rows = down_index if table_rows < down_index else table_rows

for one_row in table_dict['trs']:
    all_cells_of_row = one_row['tds']
    for cell in all_cells_of_row:
        left_index, right_index = cell['colspan'][0], cell['colspan'][1]
        up_index, down_index = cell['rowspan'][0], cell['rowspan'][1]
        if cell['node_type'] == "key":
            key_num = key_num + 1
        else:
            value_num = value_num + 1

        created_node = Node(context=cell['context'], colspan=cell['colspan'], rowspan=cell['rowspan'],
                            up_pointer=[None] * (table_columns + 1),
                            down_pointer=[None] * (table_columns + 1),
                            left_pointer=[None] * (table_rows + 1),
                            right_pointer=[None] * (table_rows + 1),
                            node_type=cell['node_type'])

        created_node.set_of_affiliation.add(created_node)
        all_table_node.append(created_node)

print("table_rows:", table_rows)
print("table_columns:", table_columns)
# 构建十字双向链表
row_column_head = Node(context="", colspan=[0, 0], rowspan=[0, 0], up_pointer=[None], down_pointer=[None],
                       left_pointer=[None], right_pointer=[None], node_type="row_column_head")

pre = row_column_head
rows_head = []
for i in range(table_rows):
    row_head_i = Node(context="", colspan=[0, 0], rowspan=[i + 1, i + 1], up_pointer=[None] * (table_columns + 1),
                      down_pointer=[None] * (table_columns + 1),
                      left_pointer=[None] * (table_rows + 1), right_pointer=[None] * (table_rows + 1),
                      node_type='rows_head')
    row_head_i.up_pointer[0] = pre
    rows_head.append(row_head_i)
    pre.down_pointer[0] = row_head_i
    pre = row_head_i

pre = row_column_head
columns_head = []
for i in range(table_columns):
    column_head_i = Node(context="", colspan=[i + 1, i + 1], rowspan=[0, 0], up_pointer=[None] * (table_columns + 1),
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
    # print("正在插入节点：",cell_node.context)
    # print("列：",cell_node.colspan)
    # print("行：",cell_node.rowspan)
    # print("cell_node.left_pointer:",cell_node.left_pointer)
    # print("cell_node.right_pointer:",cell_node.right_pointer)
    # print("cell_node.up_pointer:",cell_node.up_pointer)
    # print("cell_node.down_pointer:",cell_node.down_pointer)
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
                                               max(i_pre.rowspan[0], up_index): min(i_pre.rowspan[1], down_index) + 1]
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
                                              max(i_pre.colspan[0], left_index): min(i_pre.colspan[1], right_index) + 1]
            for j_down_node in i_pre_all_down_node:
                if not j_down_node:
                    all_pre_temp.add(i_pre)
                else:
                    all_pre_temp.add(j_down_node)
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

# 对表格进行分块
handled_key_num = 0
last_handled_key_num = -1
handled_value_num = 0
last_handled_value_num = -1
mm = 0
while last_handled_value_num < handled_value_num or last_handled_key_num < handled_key_num:
    print("last_handled_key_num,last_handled_value_num:", last_handled_key_num, last_handled_value_num)
    print("handled_key_num,handled_value_num:", handled_key_num, handled_value_num)
    temp_last_handled_key_num = last_handled_key_num
    temp_last_handled_value_num = last_handled_value_num
    last_handled_key_num = handled_key_num
    last_handled_value_num = handled_value_num
    # if mm==3:
    #     break
    # mm+=1

    # 处理key
    tag = True
    while key_num > handled_key_num and tag:
        tag = False
        for i in range(1, table_rows + 1):
            i_row_j_col_node: Node = rows_head[i - 1].right_pointer[i]
            while i_row_j_col_node:
                # print("正在处理节点：", i_row_j_col_node.context)
                # print("列：", i_row_j_col_node.colspan)
                # print("行：", i_row_j_col_node.rowspan)
                # print("cell_node.left_pointer:", i_row_j_col_node.left_pointer)
                # print("cell_node.right_pointer:", i_row_j_col_node.right_pointer)
                # print("cell_node.up_pointer:", i_row_j_col_node.up_pointer)
                # print("cell_node.down_pointer:", i_row_j_col_node.down_pointer)
                if i_row_j_col_node.visited or i_row_j_col_node.node_type == "value":
                    i_row_j_col_node = i_row_j_col_node.right_pointer[i]
                    continue

                current_down_all_node: List[Node] = i_row_j_col_node.down_pointer[
                                                    i_row_j_col_node.colspan[0]:i_row_j_col_node.colspan[1] + 1]

                if not any(not i_current_down_all_node for i_current_down_all_node in current_down_all_node):
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
                        down_nodes_may_merge = False
                else:
                    down_nodes_may_merge = False

                current_right_all_node: List[Node] = i_row_j_col_node.right_pointer[
                                                     i_row_j_col_node.rowspan[0]:i_row_j_col_node.rowspan[1] + 1]

                if not any(not i_current_right_all_node for i_current_right_all_node in current_right_all_node):
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
                        right_nodes_may_merge = False
                else:
                    right_nodes_may_merge = False

                if down_nodes_may_merge and not right_nodes_may_merge:
                    for i_current_down_all_node in current_down_all_node:
                        i_row_j_col_node.set_of_affiliation = i_row_j_col_node.set_of_affiliation | i_current_down_all_node.set_of_affiliation
                        i_current_down_all_node.merge_method="vertical"
                    for i_current_down_all_node in current_down_all_node:
                        i_current_down_all_node.set_of_affiliation = i_row_j_col_node.set_of_affiliation
                    i_row_j_col_node.visited = True
                    tag = True
                    i_row_j_col_node.merge_method = "vertical"
                    handled_key_num += 1
                    pass
                elif not down_nodes_may_merge and right_nodes_may_merge:
                    for i_current_right_all_node in current_right_all_node:
                        i_row_j_col_node.set_of_affiliation = i_row_j_col_node.set_of_affiliation | i_current_right_all_node.set_of_affiliation
                        i_current_right_all_node.merge_method="horizontal"
                    for i_current_right_all_node in current_right_all_node:
                        i_current_right_all_node.set_of_affiliation = i_row_j_col_node.set_of_affiliation
                    i_row_j_col_node.visited = True
                    tag = True
                    i_row_j_col_node.merge_method = "horizontal"
                    handled_key_num += 1
                    pass
                i_row_j_col_node: Node = i_row_j_col_node.right_pointer[i]

    # 处理value
    tag = True
    while value_num > handled_value_num and tag:
        tag = False
        for i in range(1, table_rows + 1):
            i_row_j_col_node: Node = rows_head[i - 1].right_pointer[i]
            while i_row_j_col_node:
                # print("正在处理节点：", i_row_j_col_node.context)
                # print("列：", i_row_j_col_node.colspan)
                # print("行：", i_row_j_col_node.rowspan)
                # print("cell_node.left_pointer:", i_row_j_col_node.left_pointer)
                # print("cell_node.right_pointer:", i_row_j_col_node.right_pointer)
                # print("cell_node.up_pointer:", i_row_j_col_node.up_pointer)
                # print("cell_node.down_pointer:", i_row_j_col_node.down_pointer)
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

                if not any(not i_current_up_all_node for i_current_up_all_node in current_up_all_node) and all(
                        i_current_up_all_node not in columns_head for i_current_up_all_node in current_up_all_node):
                    current_up_all_node_left_index, current_up_all_node_right_index = current_up_all_node[0].colspan[0], \
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
                            up_nodes_may_merge = False
                    else:
                        up_nodes_may_merge = False
                else:
                    up_nodes_may_merge = False

                current_left_all_node: List[Node] = i_row_j_col_node.left_pointer[
                                                    i_row_j_col_node.rowspan[0]:i_row_j_col_node.rowspan[1] + 1]

                if not any(not i_current_left_all_node for i_current_left_all_node in current_left_all_node) and all(
                        current_left_all_node not in rows_head for i_current_left_all_node in current_left_all_node):
                    current_left_all_node_up_index, current_left_all_node_down_index = current_left_all_node[0].rowspan[
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
                else:
                    left_nodes_may_merge = False

                if up_nodes_may_merge and not left_nodes_may_merge:
                    current_up_all_node[0].set_of_affiliation.update(i_row_j_col_node.set_of_affiliation)
                    i_row_j_col_node.set_of_affiliation=current_up_all_node[0].set_of_affiliation
                    i_row_j_col_node.visited = True
                    tag = True
                    handled_value_num += 1
                    i_row_j_col_node.merge_method="vertical"
                    if current_up_all_node[0].node_type == "key":
                        current_up_all_node[0].visited = True
                        handled_key_num += 1
                        last_handled_key_num = handled_key_num
                        current_up_all_node[0].merge_method="vertical"

                if not up_nodes_may_merge and left_nodes_may_merge:
                    current_left_all_node[0].set_of_affiliation.update(i_row_j_col_node.set_of_affiliation)
                    i_row_j_col_node.set_of_affiliation =current_left_all_node[0].set_of_affiliation
                    i_row_j_col_node.visited = True
                    tag = True
                    handled_value_num += 1
                    i_row_j_col_node.merge_method = "horizontal"
                    if current_left_all_node[0].node_type == "key":
                        current_left_all_node[0].visited = True
                        handled_key_num += 1
                        last_handled_key_num = handled_key_num
                        current_left_all_node[0].merge_method="horizontal"

                i_row_j_col_node: Node = i_row_j_col_node.right_pointer[i]

segmented_table = []
segmented_dict = {}
for cell_node in all_table_node:
    # print("正在处理节点：", cell_node.context)
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
    print("---------------------------------------------------------------------------------------")
    print("正在打印第{}个子表：".format(i + 1))
    segmented_dict['sub_table_{}'.format(i + 1)] = []
    for j, cell in enumerate(list(segment_i)):
        temp = {}
        temp["context"] = cell.context
        temp["colspan"] = cell.colspan
        temp["rowspan"] = cell.colspan
        segmented_dict['sub_table_{}'.format(i + 1)].append(temp)
        print("**************")
        print("节点：", cell.context)
        print("列：", cell.colspan)
        print("行：", cell.rowspan)
        print("cell_node.left_pointer:", cell.left_pointer)
        print("cell_node.right_pointer:", cell.right_pointer)
        print("cell_node.up_pointer:", cell.up_pointer)
        print("cell_node.down_pointer:", cell.down_pointer)

with open('./sub_tables.json', 'w', encoding='utf-8') as f:
    # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
    json.dump(segmented_dict, f, indent=4,ensure_ascii=False)
