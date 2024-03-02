import os
import json
from typing import List, Set, Dict
from langchain.chat_models import ChatOpenAI
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import ast
from tools.prompt import table_head_analysis_prompt, table_head_extract_prompt
from tools.table_seg import table_seg
from tools.node import Node
import random


def table_head_extract(context_list):
    context = "\n".join(context_list)
    analysis_prompt = PromptTemplate(input_variables=["context"], template=table_head_analysis_prompt)
    extract_prompt = PromptTemplate(input_variables=["analysis_context"], template=table_head_extract_prompt)
    # print(sys.argv[3])
    # print(type(sys.argv[3]))
    print("-----------------输出context-------------------------------------")
    print(context)
    tag = True
    table_head_temp: List = []
    while tag:
        analysis_chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat", temperature=random.random() / 2),
                                  prompt=analysis_prompt)
        # chain = LLMChain(llm=ChatOpenAI(model=sys.argv[3]), prompt=prompt)
        analysis_context = analysis_chain.run(context=context)
        print("-----------------输出大模型的analysis_context结果-------------------------------------")
        print(analysis_context)
        output_chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat", temperature=0), prompt=extract_prompt)
        table_head_result = output_chain.run(context=analysis_context)

        json_left_index, json_right_index = table_head_result.find("["), table_head_result.find("]")
        if json_left_index != -1 and json_right_index != -1:
            try:
                table_head_temp = ast.literal_eval(table_head_result[json_left_index:json_right_index + 1])
                if not isinstance(table_head_temp, list):
                    raise Exception('返回结果不是一个列表！')
                else:
                    for i in range(len(table_head_temp)):
                        if not isinstance(table_head_temp[i], str):
                            table_head_temp[i] = str(table_head_temp[i]).replace("\n", "").replace("\t", "").replace(
                                "\r", "")
                tag = False
            except Exception as e:
                print("-----------------输出表头提取错误信息-------------------------------------")
                print(e)
    table_head: List = []
    for i_context_list in context_list:
        for j_table_head_temp in table_head_temp:
            if j_table_head_temp in i_context_list or i_context_list in j_table_head_temp:
                table_head.append(i_context_list)
                break
    return table_head
    pass


def is_sub_table(left_up_node: Node, right_down_node: Node):
    if left_up_node.colspan[0] > right_down_node.colspan[0] or left_up_node.rowspan[0] > right_down_node.rowspan[0]:
        return False
    if left_up_node.colspan[1] > right_down_node.colspan[1] or left_up_node.rowspan[1] > right_down_node.rowspan[1]:
        return False
    left_index, right_index, up_index, down_index = left_up_node.colspan[0], right_down_node.colspan[1], \
    left_up_node.rowspan[0], right_down_node.rowspan[1]

    temp_node: Node = left_up_node
    while True:
        temp_node = temp_node.right_pointer[up_index]
        if not temp_node:
            break
        if temp_node.rowspan[0] < up_index:
            return False
        if temp_node.colspan[1] >= right_index:
            break

    temp_node: Node = left_up_node
    while True:
        temp_node = temp_node.down_pointer[left_index]
        if not temp_node:
            break
        if temp_node.colspan[0] < left_index:
            return False
        if temp_node.rowspan[1] >= down_index:
            break

    temp_node: Node = right_down_node
    while True:
        temp_node = temp_node.up_pointer[right_index]
        if temp_node.rowspan[0] == 0:
            break
        if temp_node.colspan[1] > right_index:
            return False
        if temp_node.rowspan[0] <= up_index:
            break

    temp_node: Node = right_down_node
    while True:
        temp_node = temp_node.left_pointer[down_index]
        if temp_node.colspan[0] == 0:
            break
        if temp_node.rowspan[1] > down_index:
            return False
        if temp_node.colspan[0] <= left_index:
            break

    return True
    pass


def get_sub_table_nodes(left_up_node: Node, right_down_node: Node, rows_head: List[Node]):
    sub_table_nodes: List[Node] = []
    left_index, right_index, up_index, down_index = left_up_node.colspan[0], right_down_node.colspan[1], \
    left_up_node.rowspan[0], right_down_node.rowspan[1]
    for i in range(up_index, down_index + 1):
        temp_node: Node = rows_head[i].right_pointer[i]
        while temp_node and temp_node.colspan[0] <= right_index:
            if temp_node in sub_table_nodes:
                temp_node = temp_node.right_pointer[i]
                continue
            else:
                if temp_node.colspan[0] >= left_index and temp_node.colspan[1] <= right_index and temp_node.rowspan[
                    0] >= up_index and temp_node.rowspan[1] <= down_index:
                    sub_table_nodes.remove(temp_node)
                    temp_node = temp_node.right_pointer[i]

    return sub_table_nodes


def kv_clf(table_dict_no_node_type: Dict):
    table_dict = table_dict_no_node_type
    cell_text_list: List[str] = []
    for i_row in table_dict["trs"]:
        for i_row_j_col in i_row["tds"]:
            cell_text_list.append(
                i_row_j_col["context"].replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", "") + "\n")
    table_head = table_head_extract(cell_text_list)
    for i_row in table_dict["trs"]:
        for i_row_j_col in i_row["tds"]:
            if i_row_j_col["context"].replace(" ", "").replace("\n", "").replace("\t", "").replace("\r",
                                                                                                   "") in table_head:
                i_row_j_col["node_type"] = "key"
            else:
                i_row_j_col["node_type"] = "value"
    all_table_node: List[Node]
    rows_head: List[Node]
    _, all_table_node, rows_head = table_seg(table_dict)
    all_table_node_kv_count = [[1] if (i_cell.node_type == "key" and len(i_cell.set_of_affiliation) > 1) else [0] for
                               i_cell in all_table_node]
    for i in range(len(all_table_node)):
        for j in range(len(all_table_node)):
            if i == j:
                continue
            if is_sub_table(all_table_node[i], all_table_node[j]):
                sub_table_nodes: List[Node] = get_sub_table_nodes(all_table_node[i], all_table_node[j], rows_head)
                sub_table_cell_text_list: List[str] = []
                for i_sub_table_node in sub_table_nodes:
                    sub_table_cell_text_list.append(
                        i_sub_table_node.context.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r",
                                                                                                              "") + "\n")
                sub_table_head = table_head_extract(sub_table_cell_text_list)
                for i_sub_table_node in sub_table_nodes:
                    cell_index = all_table_node.index(i_sub_table_node)
                    if i_sub_table_node.context.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r",
                                                                                                             "") + "\n" in sub_table_head:
                        all_table_node_kv_count[cell_index].append(1)
                    else:
                        all_table_node_kv_count[cell_index].append(0)
    for i in range(len(all_table_node)):
        if sum(all_table_node_kv_count[i]) >= len(all_table_node_kv_count[i]):
            all_table_node[i].node_type = "key"
        else:
            all_table_node[i].node_type = "value"
        for one_row in table_dict['trs']:
            all_cells_of_row = one_row['tds']
            tag = False
            for cell in all_cells_of_row:
                if cell["colspan"] == all_table_node[i].colspan and cell["rowspan"] == all_table_node[i].colspan:
                    cell["node_type"] = all_table_node[i].node_type
                    tag = True
                    break
            if tag:
                break

    res = []
    for irow in table_dict["trs"]:
        for irowjcol in irow["tds"]:
            if irowjcol["node_type"] == "key":
                res.append(irowjcol["context"])
    print(res)

    return table_dict


if __name__ == '__main__':
    os.environ['OPENAI_API_KEY'] = "EMPTY"
    os.environ['OPENAI_API_BASE'] = "http://124.70.207.36:7002/v1"

    with open(r"E:\code\table_handle\test.json", "r", encoding='utf-8') as f:
        table_dict: Dict = json.load(f)
        table_dict = kv_clf(table_dict)
        # res=[]
        # for i_row in table_dict["trs"]:
        #     for i_row_j_col in i_row["tds"]:
        #         res.append(i_row_j_col["node_type"])
        # print(res)
