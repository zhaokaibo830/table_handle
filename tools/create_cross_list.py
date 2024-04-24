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
        #
        left_index, right_index = cell_node.colspan[0], cell_node.colspan[1]
        up_index, down_index = cell_node.rowspan[0], cell_node.rowspan[1]

        # 插入到水平双向链表
        all_left_pre: Set[Node] = set(rows_head[up_index - 1:down_index])
        all_right_next: Set[Node] = set()
        for i_row in range(up_index,down_index+1):
            pre=rows_head[i_row-1]
            while pre:
                if pre.colspan[1]<cell_node.colspan[0]:
                    all_left_pre.add(pre)
                elif pre.colspan[0]>cell_node.colspan[1]:
                    all_right_next.add(pre)
                pre=pre.right_pointer[i_row]

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
        all_up_pre: Set[Node] = set()
        all_down_next: Set[Node] = set()
        for i_col in range(left_index, right_index + 1):
            pre = columns_head[i_col - 1]
            while pre:
                if pre.rowspan[1] < cell_node.rowspan[0]:
                    all_up_pre.add(pre)
                elif pre.colspan[0] > cell_node.colspan[1]:
                    all_down_next.add(pre)
                pre = pre.down_pointer[i_col]

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

if __name__ == '__main__':
    from tools.preprocess import any_format_to_json


    gt_table, propositions = any_format_to_json(r"E:\code\table_handle\tools\11.xlsx")
    print(gt_table)
    all_table_node, row_column_head, rows_head, columns_head = create_cross_list(gt_table["cells"])
    for cell_node in all_table_node:
        print("正在插入节点：", cell_node.text)
        print("列：", cell_node.colspan)
        print("行：", cell_node.rowspan)
        print("cell_node.left_pointer:", cell_node.left_pointer)
        print("cell_node.right_pointer:", cell_node.right_pointer)
        print("cell_node.up_pointer:", cell_node.up_pointer)
        print("cell_node.down_pointer:", cell_node.down_pointer)