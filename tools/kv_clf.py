import os
import json
from typing import List, Set, Dict
from langchain.chat_models import ChatOpenAI
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import ast
from tools.prompt import table_head_extract_prompt
from tools.table_seg import table_seg
from tools.node import Node
import random


def table_head_extract(context):
    prompt = PromptTemplate(input_variables=["context"], template=table_head_extract_prompt)
    # print(sys.argv[3])
    # print(type(sys.argv[3]))
    chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat"), prompt=prompt)
    # chain = LLMChain(llm=ChatOpenAI(model=sys.argv[3]), prompt=prompt)
    return ast.literal_eval(chain.run(context=context))["表头"]
    pass


def kv_clf(table_dict_no_node_type: Dict):
    table_dict = table_dict_no_node_type
    context = ""
    for i_row in table_dict["trs"]:
        for i_row_j_col in i_row["tds"]:
            context += i_row_j_col["context"].replace(" ", "").replace("\n", "").replace("\t", "").replace("\r",
                                                                                                           "") + "\n"
    table_head = table_head_extract(context)
    for i_row in table_dict["trs"]:
        for i_row_j_col in i_row["tds"]:
            if i_row_j_col["context"].replace(" ", "").replace("\n", "").replace("\t", "").replace("\r",
                                                                                                   "") in table_head:
                i_row_j_col["node_type"] = "key"
            else:
                i_row_j_col["node_type"] = "value"
    i = 0
    while i < 10:
        i += 1
        segmented_table: List[Set[Node]]=[]
        all_table_node: List[Node]
        _, all_table_node = table_seg(table_dict)
        for cell in all_table_node:
            if len(cell.set_of_affiliation) == 1:
                merge_direction_list = [1, 2, 3, 4]  # 1对应上方，2对应右方，3对应下方，4对应左方
                random.shuffle(merge_direction_list)
                for merge_direction in merge_direction_list:
                    if merge_direction == 1:
                        left_index, right_index = cell.colspan[0], cell.colspan[1]
                        up_all_node: List[Node] = list(set(cell.up_pointer[left_index:right_index + 1]))
                        if len(up_all_node) == 1 and (up_all_node[0] in all_table_node) and up_all_node[0].colspan[
                            0] <= left_index and up_all_node[0].colspan[1] >= right_index:
                            temp_set: Set[Node] = set()
                            temp_set.add(up_all_node[0])
                            temp_set.add(cell)
                            for i_temp_set in list(temp_set):
                                i_temp_set.set_of_affiliation = temp_set
                            break
                    if merge_direction == 4:
                        up_index, down_index = cell.rowspan[0], cell.rowspan[1]
                        left_all_node: List[Node] = list(set(cell.left_pointer[up_index:down_index + 1]))
                        if len(left_all_node) == 1 and (left_all_node[0] in all_table_node) and \
                                left_all_node[0].rowspan[0] <= up_index and left_all_node[0].colspan[1] >= down_index:
                            temp_set: Set[Node] = set()
                            temp_set.add(down_index[0])
                            temp_set.add(cell)
                            for i_temp_set in list(temp_set):
                                i_temp_set.set_of_affiliation = temp_set
                            break
                    if merge_direction == 3:
                        left_index, right_index = cell.colspan[0], cell.colspan[1]
                        down_all_node: List[Node] = cell.down_pointer[left_index:right_index + 1]
                        if all(_ in all_table_node for _ in down_all_node) and down_all_node[0].colspan[
                            0] == left_index and down_all_node[-1].colspan[1] == right_index:
                            temp_set: Set[Node] = set()
                            for i_down_all_node in down_all_node:
                                temp_set.update(i_down_all_node.set_of_affiliation)
                            temp_set.add(cell)
                            for i_temp_set in list(temp_set):
                                i_temp_set.set_of_affiliation = temp_set
                            break
                    if merge_direction == 2:
                        up_index, down_index = cell.rowspan[0], cell.rowspan[1]
                        right_all_node: List[Node] = cell.right_pointer[up_index:down_index + 1]
                        if all(_ in all_table_node for _ in right_all_node) and right_all_node[0].colspan[
                            0] == up_index and right_all_node[-1].colspan[1] == down_index:
                            temp_set: Set[Node] = set()
                            for i_right_all_node in right_all_node:
                                temp_set.update(i_right_all_node.set_of_affiliation)
                            temp_set.add(cell)
                            for i_temp_set in list(temp_set):
                                i_temp_set.set_of_affiliation = temp_set
                            break

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

        for i_segmented_table in segmented_table:
            context = ""
            for i_segmented_table_j_node in list(i_segmented_table):
                context += i_segmented_table_j_node["context"].replace(" ", "").replace("\n", "").replace("\t",
                                                                                                          "").replace(
                    "\r", "") + "\n"
            i_segmented_table_head = table_head_extract(context)
            for i_segmented_table_j_node in list(i_segmented_table):
                for one_row in table_dict['trs']:
                    all_cells_of_row = one_row['tds']
                    for cell in all_cells_of_row:
                        if cell["colspan"] == i_segmented_table_j_node.colspan and cell[
                            "rowspan"] == i_segmented_table_j_node.colspan.rowspan:
                            if cell["context"].replace(" ", "").replace("\n", "").replace("\t", "").replace("\r",
                                                                                                            "") in i_segmented_table_head:
                                cell["node_type"] = "key"
                            else:
                                cell["node_type"] = "value"

    return table_dict


if __name__ == '__main__':
    os.environ['OPENAI_API_KEY'] = "EMPTY"
    os.environ['OPENAI_API_BASE'] = "http://124.70.207.36:7002/v1"

    with open("temp.json", "r", encoding='utf-8') as f:
        table_dict: Dict = json.load(f)
        kv_clf(table_dict)
