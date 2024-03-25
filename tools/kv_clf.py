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


def table_head_extract(text_list)->List:
    """
    利用大模型提取表格中可能为表头的单元格
    :param text_list: 表格中的所有单元格文本构成的列表
    :return:
    table_head：可能为表头的单元格文本列表
    """
    text = "\n".join(text_list)
    analysis_prompt = PromptTemplate(input_variables=["text"], template=table_head_analysis_prompt)
    extract_prompt = PromptTemplate(input_variables=["analysis_text"], template=table_head_extract_prompt)
    # print(sys.argv[3])
    # print(type(sys.argv[3]))
    print("-----------------输出text-------------------------------------")
    print(text)
    tag = True
    table_head_temp: List = []
    while tag:
        analysis_chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat", temperature=random.random() / 2),
                                  prompt=analysis_prompt)
        # chain = LLMChain(llm=ChatOpenAI(model=sys.argv[3]), prompt=prompt)
        analysis_text = analysis_chain.run(text=text)
        print("-----------------输出大模型的analysis_text结果-------------------------------------")
        print(analysis_text)
        output_chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat", temperature=0), prompt=extract_prompt)
        table_head_result = output_chain.run(text=analysis_text)
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
    for i_text_list in text_list:
        for j_table_head_temp in table_head_temp:
            if ((keep_chinese_english_digit(j_table_head_temp) in keep_chinese_english_digit(i_text_list)) or (
                    keep_chinese_english_digit(i_text_list) in keep_chinese_english_digit(
                j_table_head_temp))) and keep_chinese_english_digit(
                j_table_head_temp) and keep_chinese_english_digit(i_text_list):
                table_head.append(i_text_list)
                break
    return table_head
    pass



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
    for i_row_j_col in table_dict['cells']:
        cell_text_list.append(
            i_row_j_col["text"].replace("\n", "").replace("\t", "").replace("\r", "").replace(" ", ""))
    # all_table_node列表，其中的每一个元素是输入表格中的一个单元格
    all_table_node: List[Node]
    # rows_head是表格构成的双向十字链表以行进行索引的头指针列表
    rows_head: List[Node]
    # segmented_table是一个列表，其中的每一个元素是一个当前子表中所有的单元格组成的集合
    segmented_table: List[Set[Node]]

    # key粗粒度检测
    loop = 1
    # table_head_dict统计每一个单元格被判断为key的次数
    table_head_dict: Dict = {}
    for _ in range(loop):
        count = 0
        while True:
            count += 1
            table_head = table_head_extract(cell_text_list)
            for i_row_j_col in table_dict['cells']:
                if i_row_j_col["text"].replace("\n", "").replace("\t", "").replace("\r", "").replace(" ",
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
                        print(j_cell.text, end="#")
                    print()
                print(table_dict)
                for i_table_head in table_head:
                    if i_table_head in table_head_dict:
                        table_head_dict[i_table_head] += 1
                    else:
                        table_head_dict[i_table_head] = 1
                # 分割后没有剩余的key说明此时划分的key、value结果在结构上是无歧义的
                break
            if count >= 2:
                print(
                    "---------------------------有剩余的key且已经达到了最大处理次数，并打印此时的table_dict，打印完之后不再处理-----------------------------------------")
                for i_segmented_table in segmented_table:
                    for j_cell in list(i_segmented_table):
                        print(j_cell.text, end="#")
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
                    print(j_cell.text, end="#")
                print()
            print(table_dict)
    # table_head存放key粗粒度检测结果
    table_head: List = []
    for k, v in table_head_dict.items():
        if v > loop / 2:
            table_head.append(k)
    print("--------------输出key粗粒度检测结果的所有表头-----------------")
    print(table_head)
    for i_row_j_col in table_dict['cells']:
        if i_row_j_col["text"].replace("\n", "").replace("\t", "").replace("\r", "").replace(" ",
                                                                                                "") in table_head:
            i_row_j_col["node_type"] = "key"
        else:
            i_row_j_col["node_type"] = "value"

    segmented_table, all_table_node, rows_head = table_seg(table_dict)
    # all_table_node_kv_count统计key粗粒度和每一步细粒度检测的属性类别，key为1，value为0
    all_table_node_kv_count = [[1] if i_cell.node_type == "key" else [0] for i_cell in all_table_node]

    print("----------对整个表进行了key-value分类，输出此时的all_table_node_kv_count---------------")
    for k in range(len(all_table_node_kv_count)):
        print(all_table_node[k].text, "-->", all_table_node_kv_count[k])


    print("-------------开始打印key-----------------")
    for i in range(len(all_table_node)):
        if sum(all_table_node_kv_count[i]) >= len(all_table_node_kv_count[i]) / 2:
            all_table_node[i].node_type = "key"
            print(all_table_node[i].text)
        else:
            all_table_node[i].node_type = "value"
        for cell in table_dict['cells']:
            if cell["colspan"] == all_table_node[i].colspan and cell["rowspan"] == all_table_node[i].rowspan:
                cell["node_type"] = all_table_node[i].node_type
                break

    res = []
    for irowjcol in table_dict['cells']:
        if irowjcol["node_type"] == "key":
            res.append(irowjcol["text"])
    print(res)

    return table_dict


if __name__ == '__main__':
    os.environ['OPENAI_API_KEY'] = "EMPTY"
    os.environ['OPENAI_API_BASE'] = "http://124.70.207.36:7002/v1"

    with open(r"E:\code\table_handle\test.json", "r", encoding='utf-8') as f:
        table_dict: Dict = json.load(f)
        table_dict = kv_clf(table_dict)