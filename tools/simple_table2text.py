from tools.node import Node
from typing import List, Set, Dict
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


def simple_table2text(simple_table: List[Dict], have_table_head: bool, language: str) -> str:
    caption = ""
    if not have_table_head:
        for cell in simple_table:
            caption = caption + " "+cell["text"]
    else:
        all_table_node, row_column_head, rows_head, columns_head = create_cross_list(simple_table)
        data_start_row = 0
        col_ranges = []
        caption_template = ""
        for i, i_row_head in enumerate(rows_head):
            i_row_nodes: List[Node] = []
            temp: Node = i_row_head.right_pointer[i + 1]
            if i+1<temp.rowspan[1]:
                continue
            if temp.down_pointer[temp.colspan[0]].node_type == "key":
                continue
            data_start_row = temp.rowspan[1]
            while temp:
                i_row_nodes.append(temp)
                temp = temp.right_pointer[i + 1]
            for j, cell in enumerate(i_row_nodes):
                if language == "Chinese":
                    i_template = "是{}。 "
                else:
                    i_template = "is {}. "
                col_ranges.append(cell.colspan[:])
                temp_cell: Node = cell
                level = 0
                while temp_cell not in columns_head:
                    if level == 0:
                        i_template = temp_cell.text +" " + i_template
                    else:
                        if language == "Chinese":
                            i_template = temp_cell.text + "的" + i_template
                        else:
                            i_template = temp_cell.text + "'s " + i_template
                    level += 1
                    temp_cell = temp_cell.up_pointer[temp_cell.colspan[0]]
                caption_template += i_template
            break
        print("col_ranges:", col_ranges)
        pre_row_nodes: List[Node] = []
        print("caption_template:", caption_template)
        print("data_start_row:", data_start_row)
        for k, i_row_head in enumerate(rows_head):
            if k < data_start_row:
                continue
            text_list: List[str] = []
            i_row_nodes: List[Node] = []
            print("data_start_row:", data_start_row)
            print("k:", k)
            temp_node: Node = i_row_head.right_pointer[k + 1]
            i_row_nodes.append(temp_node)
            for j_col_range in col_ranges:
                text_list.append(temp_node.text)
                print("j_col_range:", j_col_range)
                if j_col_range[1] == temp_node.colspan[1]:
                    temp_node = temp_node.right_pointer[k + 1]
                    i_row_nodes.append(temp_node)
            print(text_list)
            if not all([cell in pre_row_nodes for cell in i_row_nodes]):
                caption += caption_template.format(*text_list)
            pre_row_nodes = i_row_nodes[:]
    return caption


if __name__ == "__main__":
    from tools.preprocess import any_format_to_json
    from tools.kv_amend import kv_amend
    gt_table, propositions = any_format_to_json("11.xlsx")
    # amended_table, unified_table, have_table_head = kv_amend(gt_table["cells"])
    print(gt_table)
    caption = simple_table2text(gt_table["cells"], True, "Chinese")
    print(caption)
