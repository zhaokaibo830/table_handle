import json
from tools.node import Node
from typing import List, Set


def is_merge(first_sub_table: Set[Node], second_sub_table: Set[Node]) -> bool:
    """
    判断两个子表是否需要合并
    :param first_sub_table:
    :param second_sub_table:
    :return:
    """
    first_sub_table_left_index = list(first_sub_table)[0].colspan[0]
    first_sub_table_right_index = list(first_sub_table)[0].colspan[1]
    first_sub_table_up_index = list(first_sub_table)[0].rowspan[0]
    first_sub_table_down_index = list(first_sub_table)[0].rowspan[1]
    for cell in first_sub_table:
        first_sub_table_left_index = cell.colspan[0] if first_sub_table_left_index > cell.colspan[
            0] else first_sub_table_left_index
        first_sub_table_right_index = cell.colspan[1] if first_sub_table_right_index < cell.colspan[
            1] else first_sub_table_right_index
        first_sub_table_up_index = cell.rowspan[0] if first_sub_table_up_index > cell.rowspan[
            0] else first_sub_table_up_index
        first_sub_table_down_index = cell.rowspan[1] if first_sub_table_down_index < cell.rowspan[
            1] else first_sub_table_down_index

    second_sub_table_left_index = list(second_sub_table)[0].colspan[0]
    second_sub_table_right_index = list(second_sub_table)[0].colspan[1]
    second_sub_table_up_index = list(second_sub_table)[0].rowspan[0]
    second_sub_table_down_index = list(second_sub_table)[0].rowspan[1]
    for cell in second_sub_table:
        second_sub_table_left_index = cell.colspan[0] if second_sub_table_left_index > cell.colspan[
            0] else second_sub_table_left_index
        second_sub_table_right_index = cell.colspan[1] if second_sub_table_right_index < cell.colspan[
            1] else second_sub_table_right_index
        second_sub_table_up_index = cell.rowspan[0] if second_sub_table_up_index > cell.rowspan[
            0] else second_sub_table_up_index
        second_sub_table_down_index = cell.rowspan[1] if second_sub_table_down_index < cell.rowspan[
            1] else second_sub_table_down_index

    # print("--first_sub_table_up_index, second_sub_table_up_index, first_sub_table_down_index, first_sub_table_down_index--")
    # print(first_sub_table_up_index,second_sub_table_up_index,first_sub_table_down_index,first_sub_table_down_index)

    if first_sub_table_up_index == second_sub_table_up_index and first_sub_table_down_index == second_sub_table_down_index:
        if first_sub_table_left_index > second_sub_table_left_index:
            first_sub_table, second_sub_table = second_sub_table, first_sub_table
            first_sub_table_left_index, second_sub_table_left_index = second_sub_table_left_index, first_sub_table_left_index
            first_sub_table_right_index, second_sub_table_right_index = second_sub_table_right_index, first_sub_table_right_index
            first_sub_table_up_index, second_sub_table_up_index = second_sub_table_up_index, first_sub_table_up_index
            first_sub_table_down_index, second_sub_table_down_index = second_sub_table_down_index, first_sub_table_down_index
        if first_sub_table_right_index + 1 != second_sub_table_left_index:
            print(1)
            return False

        first_sub_table_right_up_node: Node = None
        for node in first_sub_table:
            if node.colspan[1] == first_sub_table_right_index and node.rowspan[0] == first_sub_table_up_index:
                first_sub_table_right_up_node = node
                break
        second_sub_table_left_up_node: Node = None
        for node in second_sub_table:
            if node.colspan[0] == second_sub_table_left_index and node.rowspan[0] == second_sub_table_up_index:
                second_sub_table_left_up_node = node
                break

        first_sub_table_key_down_index = first_sub_table_up_index
        first_sub_table_value_range = []
        temp = first_sub_table_right_up_node
        while temp and temp in first_sub_table:
            if temp.node_type == "key":
                if first_sub_table_value_range:
                    print(2)
                    return False
                first_sub_table_key_down_index = temp.rowspan[1]
            else:
                first_sub_table_value_range.append([temp.rowspan[0], temp.rowspan[1]])
            temp = temp.down_pointer[first_sub_table_right_index]

        second_sub_table_key_down_index = -1
        second_sub_table_value_range = []
        temp = second_sub_table_left_up_node
        while temp and temp in second_sub_table:
            if temp.node_type == "key":
                if second_sub_table_value_range:
                    print(4)
                    return False
                second_sub_table_key_down_index = temp.rowspan[1]
            else:
                second_sub_table_value_range.append([temp.rowspan[0], temp.rowspan[1]])
            temp = temp.down_pointer[second_sub_table_left_index]

        if first_sub_table_key_down_index != second_sub_table_key_down_index:
            print(5)
            return False
        if len(first_sub_table_value_range) == len(second_sub_table_value_range) == 1:
            print(6)
            return False
        if not first_sub_table_value_range or not second_sub_table_value_range:
            print(7)
            return False
        if first_sub_table_value_range[-1][1] != second_sub_table_value_range[-1][1]:
            print(8)
            return False
        for i_first_sub_table_value_range in first_sub_table_value_range:
            for i_second_sub_table_value_range in second_sub_table_value_range:
                if i_first_sub_table_value_range[0] < i_second_sub_table_value_range[0] < i_first_sub_table_value_range[
                    1] < \
                        i_second_sub_table_value_range[1]:
                    print(9)
                    return False
                if i_second_sub_table_value_range[0] < i_first_sub_table_value_range[0] < \
                        i_second_sub_table_value_range[1] < \
                        i_first_sub_table_value_range[1]:
                    print(10)
                    return False
        for i_first_sub_table in first_sub_table:
            if i_first_sub_table.node_type == "key" and i_first_sub_table.rowspan[0] > first_sub_table_key_down_index:
                return False
        print(11)
        return True

    if first_sub_table_left_index == second_sub_table_left_index and first_sub_table_right_index == second_sub_table_right_index:
        if first_sub_table_up_index > second_sub_table_up_index:
            first_sub_table, second_sub_table = second_sub_table, first_sub_table
            first_sub_table_left_index, second_sub_table_left_index = second_sub_table_left_index, first_sub_table_left_index
            first_sub_table_right_index, second_sub_table_right_index = second_sub_table_right_index, first_sub_table_right_index
            first_sub_table_up_index, second_sub_table_up_index = second_sub_table_up_index, first_sub_table_up_index
            first_sub_table_down_index, second_sub_table_down_index = second_sub_table_down_index, first_sub_table_down_index
        if first_sub_table_down_index + 1 != second_sub_table_up_index:
            print(12)
            return False

        first_sub_table_left_down_node: Node = None
        for node in first_sub_table:
            if node.colspan[0] == first_sub_table_left_index and node.rowspan[1] == first_sub_table_down_index:
                first_sub_table_left_down_node = node
                break
        second_sub_table_left_up_node: Node = None
        for node in second_sub_table:
            if node.colspan[0] == second_sub_table_left_index and node.rowspan[0] == second_sub_table_up_index:
                second_sub_table_left_up_node = node
                break

        first_sub_table_key_right_index = -1
        first_sub_table_value_range = []
        temp = first_sub_table_left_down_node
        while temp and temp in first_sub_table:
            if temp.node_type == "key":
                if first_sub_table_value_range:
                    print(13)
                    return False
                first_sub_table_key_down_index = temp.colspan[1]
            else:
                first_sub_table_value_range.append([temp.colspan[0], temp.colspan[1]])
            temp = temp.right_pointer[first_sub_table_down_index]

        second_sub_table_key_right_index = second_sub_table_left_index
        second_sub_table_value_range = []
        temp = second_sub_table_left_up_node
        while temp and temp in second_sub_table:
            if temp.node_type == "key":
                if second_sub_table_value_range:
                    print(14)
                    return False
                second_sub_table_key_right_index = temp.colspan[1]
            else:
                second_sub_table_value_range.append([temp.colspan[0], temp.colspan[1]])
            temp = temp.right_pointer[second_sub_table_down_index]

        if first_sub_table_key_right_index != second_sub_table_key_right_index:
            print(15)
            return False
        if len(first_sub_table_value_range) == len(second_sub_table_value_range) == 1:
            print(16)
            return False
        if not first_sub_table_value_range or not second_sub_table_value_range:
            print(17)
            return False
        if first_sub_table_value_range[-1][1] != second_sub_table_value_range[-1][1]:
            print(18)
            return False
        for i_first_sub_table_value_range in first_sub_table_value_range:
            for i_second_sub_table_value_range in second_sub_table_value_range:
                if i_first_sub_table_value_range[0] < i_second_sub_table_value_range[0] < i_first_sub_table_value_range[
                    1] < \
                        i_second_sub_table_value_range[1]:
                    print(19)
                    return False
                if i_second_sub_table_value_range[0] < i_first_sub_table_value_range[0] < \
                        i_second_sub_table_value_range[1] < \
                        i_first_sub_table_value_range[1]:
                    print(20)
                    return False
        for i_first_sub_table in first_sub_table:
            if i_first_sub_table.node_type == "key" and i_first_sub_table.colspan[0] > first_sub_table_key_right_index:
                return False
        print(21)
        return True
    print(22)
    return False


def merge_two_sub_tables(first_sub_table: Set[Node], second_sub_table: Set[Node]):
    """
    对两个子表进行合并
    :param first_sub_table:
    :param second_sub_table:
    :return:
    """
    temp_Set = first_sub_table | second_sub_table
    for cell in list(temp_Set):
        cell.set_of_affiliation = temp_Set
    return temp_Set


def sub_table_merge(segmented_table: List[Set[Node]]):
    tag = True
    while tag:
        tag = False
        flag = False
        for i in range(len(segmented_table)):
            for j in range(len(segmented_table)):
                if i == j:
                    continue

                if is_merge(segmented_table[i], segmented_table[j]):
                    print("--------------------打印可能合并的第一个子表！--------------------")
                    for cell in list(segmented_table[i]):
                        print("text:", cell.text, end="#")
                        print("colspan:", cell.colspan, end="#")
                        print("rowspan:", cell.rowspan)
                    print("--------------------打印可能合并的第二个子表！--------------------")
                    for cell in list(segmented_table[j]):
                        print("text:", cell.text, end="#")
                        print("colspan:", cell.colspan, end="#")
                        print("rowspan:", cell.rowspan)

                    tag = True
                    merged_table: Set[Node] = merge_two_sub_tables(segmented_table[i], segmented_table[j])
                    i_segmented_table, j_segmented_table = segmented_table[i], segmented_table[j]
                    segmented_table.remove(i_segmented_table)
                    segmented_table.remove(j_segmented_table)
                    segmented_table.append(merged_table)
                    flag = True
                    break
            if flag:
                break
    return segmented_table


if __name__ == '__main__':
    from tools.table_seg import table_seg

    with open(r"E:\code\table_handle\result\3.json", "r", encoding='utf-8') as f:
        table_dict = json.load(f)
    segmented_table: List[Set[Node]]
    segmented_table, _, _ = table_seg(table_dict)

    segmented_table = sub_table_merge(segmented_table)
    for i, i_sub_table in enumerate(segmented_table):
        print("--------------------打印第{}个子表！--------------------".format(i))
        for cell in list(i_sub_table):
            print("text:", cell.text, end="#")
            print("colspan:", cell.colspan, end="#")
            print("rowspan:", cell.rowspan)
