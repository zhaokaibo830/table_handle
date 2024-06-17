import copy
import os
import json
from typing import List, Set, Dict
from langchain.chat_models import ChatOpenAI
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import ast
from tools.prompt import table_head_analysis_prompt_en, table_head_extract_prompt_en, table_head_analysis_prompt_ch, \
    table_head_extract_prompt_ch
from tools.table_seg import table_seg
from tools.node import Node
import random
import re
from langchain_core.output_parsers import StrOutputParser


def replace_multiple_spaces(text):
    return re.sub(r'\s+', ' ', text)


def keep_chinese_english_digit(text) -> str:
    # 使用正则表达式匹配中文汉字和英文字母
    pattern = re.compile(r'[^a-zA-Z\u4e00-\u9fa5]')
    result = pattern.sub('', text)
    return result


async def table_head_extract(text_list, language) -> List:
    """
    利用大模型提取表格中可能为表头的单元格
    :param text_list: 表格中的所有单元格文本构成的列表
    :return:
    table_head：可能为表头的单元格文本列表
    """
    text = "\n".join(text_list)
    if language == "Chinese":
        analysis_prompt = PromptTemplate(input_variables=["text"], template=table_head_analysis_prompt_ch)
        extract_prompt = PromptTemplate(input_variables=["analysis_text"], template=table_head_extract_prompt_ch)
    else:
        analysis_prompt = PromptTemplate(input_variables=["text"], template=table_head_analysis_prompt_en)
        extract_prompt = PromptTemplate(input_variables=["analysis_text"], template=table_head_extract_prompt_en)
    # print(sys.argv[3])
    # print(type(sys.argv[3]))
    print("-----------------输出text-------------------------------------")
    print(text)
    tag = True
    table_head_temp: List = []
    while tag:
        # analysis_chain = LLMChain(llm=ChatOpenAI(model=os.environ['MODEL_NAME'], temperature=random.random() / 2),
        #                           prompt=analysis_prompt)
        llm = ChatOpenAI(model=os.environ['MODEL_NAME'], temperature=random.random() / 2)
        analysis_chain = analysis_prompt | llm | StrOutputParser()
        # analysis_chain = analysis_chain | StrOutputParser()
        # chain = LLMChain(llm=ChatOpenAI(model=sys.argv[3]), prompt=prompt)
        analysis_text = await analysis_chain.ainvoke({"text": text})
        print("-----------------输出大模型的analysis_text结果-------------------------------------")
        print(analysis_text)
        # output_chain = LLMChain(llm=ChatOpenAI(model=os.environ['MODEL_NAME'], temperature=0), prompt=extract_prompt)
        # table_head_result = await output_chain.arun(text=analysis_text)
        # output_chain |= StrOutputParser()
        llm = ChatOpenAI(model=os.environ['MODEL_NAME'], temperature=0)
        output_chain = extract_prompt | llm | StrOutputParser()
        table_head_result = await output_chain.ainvoke({"text": analysis_text})
        print("-----------------输出大模型的table_head_extract结果-------------------------------------")
        print(table_head_result)
        json_left_index, json_right_index = table_head_result.find("["), table_head_result.find("]")
        if json_left_index != -1 and json_right_index != -1:
            try:
                print(table_head_result[json_left_index:json_right_index + 1])
                try:
                    table_head_temp = ast.literal_eval(table_head_result[json_left_index:json_right_index + 1])
                except Exception as e:
                    raise Exception("ast.literal_eval解析错误\n" + str(e))
                print("-------------table_head_temp------------------")
                print(table_head_temp)
                if not isinstance(table_head_temp, list):
                    raise Exception('返回结果不是一个列表！')
                else:
                    for i in range(len(table_head_temp)):
                        if not isinstance(table_head_temp[i], str):
                            table_head_temp[i] = str(table_head_temp[i])
                tag = False
            except Exception as e:
                print("-----------------输出表头提取错误信息-------------------------------------")
                print(e)
    table_head: List = []

    if language == "Chinese":
        for i_text_list in text_list:
            for j_table_head_temp in table_head_temp:
                if ((keep_chinese_english_digit(j_table_head_temp) in keep_chinese_english_digit(i_text_list)) or (
                        keep_chinese_english_digit(i_text_list) in keep_chinese_english_digit(
                    j_table_head_temp))) and keep_chinese_english_digit(
                    j_table_head_temp) and keep_chinese_english_digit(i_text_list):
                    table_head.append(i_text_list)
                    break
    else:
        for i_text_list in text_list:
            for j_table_head_temp in table_head_temp:
                if ((replace_multiple_spaces(
                        keep_chinese_english_digit(j_table_head_temp)).lower() in keep_chinese_english_digit(
                    i_text_list)) or (
                            keep_chinese_english_digit(i_text_list) in replace_multiple_spaces(
                        keep_chinese_english_digit(j_table_head_temp)).lower())) and replace_multiple_spaces(
                    keep_chinese_english_digit(j_table_head_temp)).lower() and keep_chinese_english_digit(i_text_list):
                    table_head.append(i_text_list)
                    break

    return table_head
    pass


def is_sub_table(left_up_node: Node, right_down_node: Node) -> bool:
    """
    判断复杂表格中是否存在一个以left_up_node为左上角单元格、right_down_node为右下方单元格的子块
    :param left_up_node: 左上角单元格
    :param right_down_node: 右下方单元格
    :return:
    """
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


def get_sub_table_nodes(left_up_node: Node, right_down_node: Node, rows_head: List[Node]) -> List[Node]:
    """
    得到子表中的所有结点
    :param left_up_node: 子表中左上角单元格
    :param right_down_node: 子表中右下角单元格
    :param rows_head: 表格构成的双向十字链表以行进行索引的头指针列表
    :return:
    sub_table_nodes：为子表中所有结点构成的列表
    """
    sub_table_nodes: List[Node] = []
    left_index, right_index, up_index, down_index = left_up_node.colspan[0], right_down_node.colspan[1], \
        left_up_node.rowspan[0], right_down_node.rowspan[1]
    for i in range(up_index, down_index + 1):
        temp_node: Node = rows_head[i - 1].right_pointer[i]
        while temp_node and temp_node.colspan[0] <= right_index:
            if temp_node in sub_table_nodes:
                temp_node = temp_node.right_pointer[i]
                continue
            else:
                if temp_node.colspan[0] >= left_index and temp_node.colspan[1] <= right_index and temp_node.rowspan[
                    0] >= up_index and temp_node.rowspan[1] <= down_index:
                    sub_table_nodes.append(temp_node)

            temp_node = temp_node.right_pointer[i]

    return sub_table_nodes


def sub_table_have_remain_key(sub_table_nodes: List[Node], whole_table_dict: Dict) -> bool:
    """
    判断表格分块后是否还存在多余的key
    :param sub_table_nodes: 子表的结点列表
    :param whole_table_dict: 整个复杂表格的字典表示，其中每个节点的类型已知
    """
    column_shift, row_shift = sub_table_nodes[0].colspan[0], sub_table_nodes[0].rowspan[0]
    for i_sub_table_node in sub_table_nodes:
        column_shift = i_sub_table_node.colspan[0] if column_shift > i_sub_table_node.colspan[0] else column_shift
        row_shift = i_sub_table_node.rowspan[1] if row_shift > i_sub_table_node.rowspan[1] else row_shift
    sub_table_dict = {"cells": []}
    all_cells = whole_table_dict['cells']
    for irowjcol in all_cells:
        for i_sub_table_node in sub_table_nodes:
            if irowjcol["colspan"] == i_sub_table_node.colspan and irowjcol["rowspan"] == i_sub_table_node.rowspan:
                temp = {"colspan": [i_sub_table_node.colspan[0] - column_shift + 1,
                                    i_sub_table_node.colspan[1] - column_shift + 1],
                        "rowspan": [i_sub_table_node.rowspan[0] - row_shift + 1,
                                    i_sub_table_node.rowspan[1] - row_shift + 1],
                        "text": i_sub_table_node.text,
                        "node_type": i_sub_table_node.node_type
                        }
                sub_table_dict["cells"].append(temp)
                break
    sub_table_segmented_table: List[Set[Node]]
    sub_table_segmented_table, _, _ = table_seg(sub_table_dict)
    if all([False if (
            len(i_sub_table_segmented_table) == 1 and list(i_sub_table_segmented_table)[0].node_type == "key") else True
            for
            i_sub_table_segmented_table in sub_table_segmented_table]):
        return False
    else:
        return True


async def kv_clf(table_dict_no_node_type: Dict, coarse_grained_degree: int, fine_grained_degree: int,
           checkpoint: List[int], language) -> List:
    """
    利用大模型提取语义信息再结合表格的结构信息对表格中的单元格进行key/value属性分类
    :param table_dict_no_node_type: 表格的字典表示，其中每个节点的类型未知
    :return:
    table_dict:表格的字典表示，其中每个节点的类型已知
    """
    ret = []

    table_dict = table_dict_no_node_type
    # cell_text_list是表格中的所有单元格文本构成的列表
    cell_text_list: List[str] = []
    if language == "Chinese":
        for i_row_j_col in table_dict['cells']:
            cell_text_list.append(
                i_row_j_col["text"].replace("\n", "").replace("\t", "").replace("\r", "").replace(" ",
                                                                                                  ""))
    else:
        for i_row_j_col in table_dict['cells']:
            cell_text_list.append(
                replace_multiple_spaces(
                    i_row_j_col["text"].replace("\n", "").replace("\t", "").replace("\r",
                                                                                    "")).strip().lower())
    # all_table_node列表，其中的每一个元素是输入表格中的一个单元格
    all_table_node: List[Node]
    # rows_head是表格构成的双向十字链表以行进行索引的头指针列表
    rows_head: List[Node]
    # segmented_table是一个列表，其中的每一个元素是一个当前子表中所有的单元格组成的集合
    segmented_table: List[Set[Node]]

    # key粗粒度检测
    loop = coarse_grained_degree
    # table_head_dict统计每一个单元格被判断为key的次数
    table_head_dict: Dict = {}
    for _ in range(loop):
        count = 0
        while True:
            count += 1
            table_head = await table_head_extract(cell_text_list, language)
            if language == "Chinese":
                for i_row_j_col in table_dict['cells']:
                    if i_row_j_col["text"].replace("\n", "").replace("\t", "").replace("\r", "").replace(" ",
                                                                                                         "") in table_head:
                        i_row_j_col["node_type"] = "key"
                    else:
                        i_row_j_col["node_type"] = "value"
            else:
                for i_row_j_col in table_dict['cells']:
                    if replace_multiple_spaces(i_row_j_col["text"].replace("\n", "").replace("\t", "").replace("\r",
                                                                                                               "")).strip().lower() in table_head:
                        i_row_j_col["node_type"] = "key"
                    else:
                        i_row_j_col["node_type"] = "value"

            segmented_table, all_table_node, rows_head = table_seg(table_dict)
            if all([False if (len(i_segmented_table) == 1 and list(i_segmented_table)[0].node_type == "key") else True
                    for
                    i_segmented_table in segmented_table]):
                # print(
                #     "---------------------------没有剩余的key，并打印table_dict-----------------------------------------")
                # for i_segmented_table in segmented_table:
                #     for j_cell in list(i_segmented_table):
                #         print(j_cell.text, end="#")
                #     print()
                # print(table_dict)
                for i_table_head in table_head:
                    if i_table_head in table_head_dict:
                        table_head_dict[i_table_head] += 1
                    else:
                        table_head_dict[i_table_head] = 1
                # 分割后没有剩余的key说明此时划分的key、value结果在结构上是无歧义的
                break
            if count >= 1:
                # print(
                #     "---------------------------有剩余的key且已经达到了最大处理次数，并打印此时的table_dict，打印完之后不再处理-----------------------------------------")
                # for i_segmented_table in segmented_table:
                #     for j_cell in list(i_segmented_table):
                #         print(j_cell.text, end="#")
                #     print()
                # print(table_dict)
                for i_table_head in table_head:
                    if i_table_head in table_head_dict:
                        table_head_dict[i_table_head] += 1
                    else:
                        table_head_dict[i_table_head] = 1
                break
            # print(
            #     "---------------------------有剩余的key还没达到了最大处理次数，打印此时的table_dict，打印完之后再次处理-----------------------------------------")
            # for i_segmented_table in segmented_table:
            #     for j_cell in list(i_segmented_table):
            #         print(j_cell.text, end="#")
            #     print()
            # print(table_dict)
    # table_head存放key粗粒度检测结果
    table_head: List = []
    for k, v in table_head_dict.items():
        if v > loop / 2:
            table_head.append(k)
    # print("--------------输出key粗粒度检测结果的所有表头-----------------")
    # print(table_head)
    if language == "Chinese":
        for i_row_j_col in table_dict['cells']:
            if i_row_j_col["text"].replace("\n", "").replace("\t", "").replace("\r", "").replace(" ",
                                                                                                 "") in table_head:
                i_row_j_col["node_type"] = "key"
            else:
                i_row_j_col["node_type"] = "value"
    else:
        for i_row_j_col in table_dict['cells']:
            if replace_multiple_spaces(i_row_j_col["text"].replace("\n", "").replace("\t", "").replace("\r",
                                                                                                       "")).strip().lower() in table_head:
                i_row_j_col["node_type"] = "key"
            else:
                i_row_j_col["node_type"] = "value"
    coarse_table = {"cells": []}
    for i_row_j_col in table_dict['cells']:
        coarse_table["cells"].append({
            "colspan": [i_row_j_col["colspan"][0], i_row_j_col["colspan"][1]],
            "rowspan": [i_row_j_col["rowspan"][0], i_row_j_col["rowspan"][1]],
            "text": i_row_j_col["text"],
            "node_type": i_row_j_col["node_type"]
        })
    # coarse_table=copy.deepcopy(table_dict)
    segmented_table, all_table_node, rows_head = table_seg(table_dict)
    # all_table_node_kv_count统计key粗粒度和每一步细粒度检测的属性类别，key为1，value为0
    all_table_node_kv_count = [[1] if i_cell.node_type == "key" else [0] for i_cell in all_table_node]

    # print("----------对整个表进行了key-value分类，输出此时的all_table_node_kv_count---------------")
    # for k in range(len(all_table_node_kv_count)):
    #     print(all_table_node[k].text, "-->", all_table_node_kv_count[k])

    if 0 in checkpoint:
        ret.append(coarse_table)

    # key细粒度检测
    handle_sub_table_count = 0
    while handle_sub_table_count < fine_grained_degree:
        weights = [1 / len(x) for x in all_table_node_kv_count]
        index = random.choices(range(len(all_table_node_kv_count)), weights=weights, k=1)[0]
        index_node = all_table_node[index]
        # print("-------------index_node------------")
        # print(index_node.text)
        tag_temp = False
        for m in range(len(all_table_node_kv_count)):
            for n in range(len(all_table_node_kv_count)):
                if m == n:
                    continue
                m_node, n_node = all_table_node[m], all_table_node[n]
                if not (m_node.colspan[0] <= index_node.colspan[0] and m_node.rowspan[0] <= index_node.rowspan[0] and
                        n_node.colspan[1] >= index_node.colspan[1] and n_node.rowspan[1] >= index_node.rowspan[1]):
                    continue
                if not is_sub_table(m_node, n_node):
                    continue
                sub_table_nodes: List[Node] = get_sub_table_nodes(m_node, n_node, rows_head)
                if len(sub_table_nodes) > len(all_table_node) / 2:
                    continue
                # print("-----------left_up_node, right_down_node-----------------")
                # print(all_table_node[m].text, all_table_node[n].text)
                # print("--------------------sub_table_nodes-----------------------")
                # for i_sub_table_node in sub_table_nodes:
                #     print(i_sub_table_node.text)
                sub_table_cell_text_list: List[str] = []
                if language == "Chinese":
                    for i_sub_table_node in sub_table_nodes:
                        sub_table_cell_text_list.append(
                            i_sub_table_node.text.replace(" ", "").replace("\n",
                                                                           "").replace("\t",
                                                                                       "").replace(
                                "\r",
                                ""))
                else:
                    for i_sub_table_node in sub_table_nodes:
                        sub_table_cell_text_list.append(
                            replace_multiple_spaces(
                                i_sub_table_node.text.replace("\n", "").replace("\t",
                                                                                "").replace(
                                    "\r",
                                    "")).strip().lower())
                sub_table_head = await table_head_extract(sub_table_cell_text_list, language)
                if language == "Chinese":
                    for i_sub_table_node in sub_table_nodes:
                        if i_sub_table_node.text.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r",
                                                                                                              "") in sub_table_head:
                            i_sub_table_node.node_type = "key"
                        else:
                            i_sub_table_node.node_type = "value"
                else:
                    for i_sub_table_node in sub_table_nodes:
                        if replace_multiple_spaces(
                                i_sub_table_node.text.replace("\n", "").replace("\t", "").replace("\r",
                                                                                                  "")).strip().lower() in sub_table_head:
                            i_sub_table_node.node_type = "key"
                        else:
                            i_sub_table_node.node_type = "value"
                if sub_table_have_remain_key(sub_table_nodes, table_dict):
                    continue
                if language == "Chinese":
                    for i_sub_table_node in sub_table_nodes:
                        cell_index = all_table_node.index(i_sub_table_node)
                        if i_sub_table_node.text.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r",
                                                                                                              "") in sub_table_head:
                            all_table_node_kv_count[cell_index].append(1)
                        else:
                            all_table_node_kv_count[cell_index].append(0)
                else:
                    for i_sub_table_node in sub_table_nodes:
                        cell_index = all_table_node.index(i_sub_table_node)
                        if replace_multiple_spaces(
                                i_sub_table_node.text.replace("\n", "").replace("\t", "").replace("\r",
                                                                                                  "")).strip().lower() in sub_table_head:
                            all_table_node_kv_count[cell_index].append(1)
                        else:
                            all_table_node_kv_count[cell_index].append(0)

                handle_sub_table_count += 1
                tag_temp = True
                # print("----------输出handle_sub_table_count---------------")
                # print(handle_sub_table_count)
                # print("----------输出此时的all_table_node_kv_count---------------")
                # for k in range(len(all_table_node_kv_count)):
                #     print(all_table_node[k].text, "-->", all_table_node_kv_count[k])
                if handle_sub_table_count in checkpoint:
                    for i in range(len(all_table_node)):
                        if sum(all_table_node_kv_count[i]) >= len(all_table_node_kv_count[i]) / 2:
                            all_table_node[i].node_type = "key"
                            # print(all_table_node[i].text)
                        else:
                            all_table_node[i].node_type = "value"
                        for cell in table_dict['cells']:
                            if cell["colspan"] == all_table_node[i].colspan and cell["rowspan"] == all_table_node[
                                i].rowspan:
                                cell["node_type"] = all_table_node[i].node_type
                                break
                    checkpoint_table = {"cells": []}
                    for i_row_j_col in table_dict['cells']:
                        checkpoint_table["cells"].append({
                            "colspan": [i_row_j_col["colspan"][0], i_row_j_col["colspan"][1]],
                            "rowspan": [i_row_j_col["rowspan"][0], i_row_j_col["rowspan"][1]],
                            "text": i_row_j_col["text"],
                            "node_type": i_row_j_col["node_type"]
                        })
                    ret.append(checkpoint_table)
                if tag_temp:
                    break
            if tag_temp:
                break
    return ret


if __name__ == '__main__':
    from tools.preprocess import any_format_to_json

    os.environ['OPENAI_API_KEY'] = "EMPTY"
    os.environ['OPENAI_API_BASE'] = "http://124.70.207.36:7002/v1"

    gt_table, propositions = any_format_to_json(r"E:\code\table_handle\tools\11.xlsx")
    print(gt_table)
    predict_table_list = kv_clf(gt_table, coarse_grained_degree=1, fine_grained_degree=50,
                                checkpoint=[_ for _ in range(0, 51, 2)],
                                language="Chinese")
    for i, predict_table in enumerate(predict_table_list):
        print(f"----------------------{i}-----------------------")
        print(predict_table)

    # for i in range(len(all_table_node)):
    #     for j in range(i+1,len(all_table_node)):
    #         print("-----------left_up_node, right_down_node-----------------")
    #         print(all_table_node[i].text, all_table_node[j].text)
    #         is_sub_table(all_table_node[i], all_table_node[j])
