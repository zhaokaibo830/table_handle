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
import re


def keep_chinese_english_digit(text)->str:
    # 使用正则表达式匹配中文汉字和英文字母
    pattern = re.compile(r'[^a-zA-Z\u4e00-\u9fa5]')
    result = pattern.sub('', text)
    return result


def table_head_extract(context_list)->List:
    """
    利用大模型提取表格中可能为表头的单元格
    :param context_list: 表格中的所有单元格文本构成的列表
    :return:
    table_head：可能为表头的单元格文本列表
    """
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
    for i_context_list in context_list:
        for j_table_head_temp in table_head_temp:
            if ((keep_chinese_english_digit(j_table_head_temp) in keep_chinese_english_digit(i_context_list)) or (
                    keep_chinese_english_digit(i_context_list) in keep_chinese_english_digit(
                j_table_head_temp))) and keep_chinese_english_digit(
                j_table_head_temp) and keep_chinese_english_digit(i_context_list):
                table_head.append(i_context_list)
                break
    return table_head
    pass


def is_sub_table(left_up_node: Node, right_down_node: Node)->bool:
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


def get_sub_table_nodes(left_up_node: Node, right_down_node: Node, rows_head: List[Node])->List[Node]:
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
    sub_table_dict = {"trs": []}
    for irow in whole_table_dict["trs"]:
        tag = True
        for irowjcol in irow["tds"]:
            for i_sub_table_node in sub_table_nodes:
                if irowjcol["colspan"] == i_sub_table_node.colspan and irowjcol["rowspan"] == i_sub_table_node.rowspan:
                    if tag:
                        sub_table_dict["trs"].append({"tds": []})
                        tag = False
                    temp = {"colspan": [i_sub_table_node.colspan[0] - column_shift + 1,
                                        i_sub_table_node.colspan[1] - column_shift + 1],
                            "rowspan": [i_sub_table_node.rowspan[0] - row_shift + 1,
                                        i_sub_table_node.rowspan[1] - row_shift + 1],
                            "context": i_sub_table_node.context,
                            "node_type": i_sub_table_node.node_type
                            }
                    sub_table_dict["trs"][-1]["tds"].append(temp)
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


def kv_clf(table_dict_no_node_type: Dict) -> Dict:
    """
    利用大模型提取语义信息再结合表格的结构信息对表格中的单元格进行key/value属性分类
    :param table_dict_no_node_type: 表格的字典表示，其中每个节点的类型未知
    :return:
    table_dict:表格的字典表示，其中每个节点的类型已知
    """

    table_dict = table_dict_no_node_type
    # cell_text_list是表格中的所有单元格文本构成的列表
    cell_text_list: List[str] = []
    for i_row in table_dict["trs"]:
        for i_row_j_col in i_row["tds"]:
            cell_text_list.append(
                i_row_j_col["context"].replace("\n", "").replace("\t", "").replace("\r", "").replace(" ", ""))
    # all_table_node列表，其中的每一个元素是输入表格中的一个单元格
    all_table_node: List[Node]
    # rows_head是表格构成的双向十字链表以行进行索引的头指针列表
    rows_head: List[Node]
    # segmented_table是一个列表，其中的每一个元素是一个当前子表中所有的单元格组成的集合
    segmented_table: List[Set[Node]]

    # key粗粒度检测
    loop = 10
    # table_head_dict统计每一个单元格被判断为key的次数
    table_head_dict: Dict = {}
    for _ in range(loop):
        count = 0
        while True:
            count += 1
            table_head = table_head_extract(cell_text_list)
            for i_row in table_dict["trs"]:
                for i_row_j_col in i_row["tds"]:
                    if i_row_j_col["context"].replace("\n", "").replace("\t", "").replace("\r", "").replace(" ",
                                                                                                            "") in table_head:
                        i_row_j_col["node_type"] = "key"
                    else:
                        i_row_j_col["node_type"] = "value"

            segmented_table, all_table_node, rows_head = table_seg(table_dict)
            if all([False if (len(i_segmented_table) == 1 and list(i_segmented_table)[0].node_type == "key") else True
                    for
                    i_segmented_table in segmented_table]):
                print(
                    "---------------------------没有剩余的key，并打印table_dict-----------------------------------------")
                for i_segmented_table in segmented_table:
                    for j_cell in list(i_segmented_table):
                        print(j_cell.context, end="#")
                    print()
                print(table_dict)
                for i_table_head in table_head:
                    if i_table_head in table_head_dict:
                        table_head_dict[i_table_head] += 1
                    else:
                        table_head_dict[i_table_head] = 1
                # 分割后没有剩余的key说明此时划分的key、value结果在结构上是无歧义的
                break
            if count >= 10:
                print(
                    "---------------------------有剩余的key且已经达到了最大处理次数，并打印此时的table_dict，打印完之后不再处理-----------------------------------------")
                for i_segmented_table in segmented_table:
                    for j_cell in list(i_segmented_table):
                        print(j_cell.context, end="#")
                    print()
                print(table_dict)
                for i_table_head in table_head:
                    if i_table_head in table_head_dict:
                        table_head_dict[i_table_head] += 1
                    else:
                        table_head_dict[i_table_head] = 1
                break
            print(
                "---------------------------有剩余的key还没达到了最大处理次数，打印此时的table_dict，打印完之后再次处理-----------------------------------------")
            for i_segmented_table in segmented_table:
                for j_cell in list(i_segmented_table):
                    print(j_cell.context, end="#")
                print()
            print(table_dict)
    # table_head存放key粗粒度检测结果
    table_head: List = []
    for k, v in table_head_dict.items():
        if v > loop / 2:
            table_head.append(k)
    print("--------------输出key粗粒度检测结果的所有表头-----------------")
    print(table_head)
    for i_row in table_dict["trs"]:
        for i_row_j_col in i_row["tds"]:
            if i_row_j_col["context"].replace("\n", "").replace("\t", "").replace("\r", "").replace(" ",
                                                                                                    "") in table_head:
                i_row_j_col["node_type"] = "key"
            else:
                i_row_j_col["node_type"] = "value"

    segmented_table, all_table_node, rows_head = table_seg(table_dict)
    # all_table_node_kv_count统计key粗粒度和每一步细粒度检测的属性类别，key为1，value为0
    all_table_node_kv_count = [[1] if i_cell.node_type == "key" else [0] for i_cell in all_table_node]

    print("----------对整个表进行了key-value分类，输出此时的all_table_node_kv_count---------------")
    for k in range(len(all_table_node_kv_count)):
        print(all_table_node[k].context, "-->", all_table_node_kv_count[k])

    # key细粒度检测
    handle_sub_table_count = 0
    while handle_sub_table_count < 10:
        selected_nodes_index = sorted(random.sample([_ for _ in range(len(all_table_node))], 2))
        i, j = selected_nodes_index[0], selected_nodes_index[1]
        if is_sub_table(all_table_node[i], all_table_node[j]):
            sub_table_nodes: List[Node] = get_sub_table_nodes(all_table_node[i], all_table_node[j], rows_head)
            if len(sub_table_nodes) > len(all_table_node) / 5:
                continue
            print("-----------left_up_node, right_down_node-----------------")
            print(all_table_node[i].context, all_table_node[j].context)
            print("--------------------sub_table_nodes-----------------------")
            for i_sub_table_node in sub_table_nodes:
                print(i_sub_table_node.context)
            sub_table_cell_text_list: List[str] = []
            for i_sub_table_node in sub_table_nodes:
                sub_table_cell_text_list.append(
                    i_sub_table_node.context.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", ""))
            sub_table_head = table_head_extract(sub_table_cell_text_list)

            for i_sub_table_node in sub_table_nodes:
                if i_sub_table_node.context.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r",
                                                                                                         "") in sub_table_head:
                    i_sub_table_node.node_type = "key"
                else:
                    i_sub_table_node.node_type = "value"
            if sub_table_have_remain_key(sub_table_nodes, table_dict):
                continue

            for i_sub_table_node in sub_table_nodes:
                cell_index = all_table_node.index(i_sub_table_node)
                if i_sub_table_node.context.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r",
                                                                                                         "") in sub_table_head:
                    all_table_node_kv_count[cell_index].append(1)
                else:
                    all_table_node_kv_count[cell_index].append(0)

            handle_sub_table_count += 1
            print("----------输出handle_sub_table_count---------------")
            print(handle_sub_table_count)
            print("----------输出此时的all_table_node_kv_count---------------")
            for k in range(len(all_table_node_kv_count)):
                print(all_table_node[k].context, "-->", all_table_node_kv_count[k])

    print("-------------开始打印key-----------------")
    for i in range(len(all_table_node)):
        if sum(all_table_node_kv_count[i]) >= len(all_table_node_kv_count[i]) / 2:
            all_table_node[i].node_type = "key"
            print(all_table_node[i].context)
        else:
            all_table_node[i].node_type = "value"
        for one_row in table_dict['trs']:
            all_cells_of_row = one_row['tds']
            tag = False
            for cell in all_cells_of_row:
                if cell["colspan"] == all_table_node[i].colspan and cell["rowspan"] == all_table_node[i].rowspan:
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
