import json
from tools.table_seg import table_seg
from tools.node import Node
from tools.kv_clf import kv_clf
from tools.simple_table2text import simple_table2text
from functools import cmp_to_key
from typing import List, Set, Dict
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form
import json
import os
from pydantic import BaseModel
import sys
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from tools.prompt import polish_prompt_en, sub_table_extract_prompt_en, polish_prompt_ch, sub_table_extract_prompt_ch
from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from tools.kv_amend import sub_table_kv_amend, table_kv_amend
from tools.func import language_judgement, sub_table_adjust, cmp_dict, cmp_node
from tools.st_merge import sub_table_merge
from tools.is_simple_table import is_simple_table
from tools.create_cross_list import create_cross_list
from tools.func import is_rectangle

def is_table(table_dict):
    pass


def table2text(table_dict, is_node_type=False, coarse_grained_degree=1, fine_grained_degree=0):
    left_index, up_index = table_dict["cells"][0]["colspan"][0], table_dict["cells"][0]["rowspan"][0]
    for i_cell in table_dict["cells"]:
        left_index = left_index if left_index <= i_cell["colspan"][0] else i_cell["colspan"][0]
        up_index = up_index if up_index <= i_cell["rowspan"][0] else i_cell["rowspan"][0]
    for i_cell in table_dict["cells"]:
        i_cell["colspan"] = [i_cell["colspan"][0] - left_index, i_cell["colspan"][1] - left_index]
        i_cell["rowspan"] = [i_cell["rowspan"][0] - up_index, i_cell["rowspan"][1] - up_index]

    table_dict["cells"].sort(key=cmp_to_key(cmp_dict))
    language = language_judgement(table_dict["cells"])
    if not is_rectangle(set(create_cross_list(table_dict["cells"])[0])):
        print("******表格类型：不是一个表格********")
        caption = ""
        _, _, rows_head, _ = create_cross_list(table_dict["cells"])
        for i, i_row_head in enumerate(rows_head):
            temp: Node = i_row_head.right_pointer[i + 1]
            while temp:
                caption += temp.text + "  "
                temp = temp.right_pointer[i + 1]
            caption += "\n"
        pass
    else:
        whole_table_amended_table, whole_table_unified_table, whole_table_have_table_head = is_simple_table(
            table_dict["cells"], language)
        segmented_table: List[Set[Node]] = []
        if whole_table_have_table_head:
            print("******表格类型，是一个简单表格********")
            segmented_table, all_table_node, rows_head = table_seg({"cells": whole_table_unified_table})
            segmented_table = sub_table_merge(segmented_table, all_table_node)
        else:
            print("******表格类型，是一个复杂表格********")
            if not is_node_type:
                table_dict = \
                    kv_clf(table_dict, coarse_grained_degree, fine_grained_degree, checkpoint=[0, fine_grained_degree],
                           language=language)[-1]
                # print(table_dict)
            segmented_table, all_table_node, rows_head = table_seg(table_dict)
            segmented_table = sub_table_adjust(segmented_table, all_table_node)
            segmented_table = table_kv_amend(segmented_table, all_table_node)
            segmented_table = sub_table_merge(segmented_table, all_table_node)

        caption = ""
        for i, segment_i in enumerate(segmented_table):
            segment_i = list(segment_i)
            segment_i.sort(key=cmp_to_key(cmp_node))
            if len(segment_i) == 2:
                if language == "Chinese":
                    caption += segment_i[0].text + "是" + segment_i[1].text + "。 "
                else:
                    caption += segment_i[0].text + "is" + segment_i[1].text + ". "
            elif len(segment_i) > 2:
                sub_table_cell = []
                for segment_i_cell_j in segment_i:
                    temp_dict = {
                        "colspan": [segment_i_cell_j.colspan[0], segment_i_cell_j.colspan[1]],
                        "rowspan": [segment_i_cell_j.rowspan[0], segment_i_cell_j.rowspan[1]],
                        "text": segment_i_cell_j.text,
                        "node_type": segment_i_cell_j.node_type
                    }
                    sub_table_cell.append(temp_dict)
                # print("-------------打印子表---------------------")
                # print(sub_table_cell)
                try:
                    _, unified_table, have_table_head = sub_table_kv_amend(sub_table_cell)
                    caption += simple_table2text(unified_table, have_table_head, language)
                except Exception as e:
                    print("子表处理异常！！！！！！")
                    print(e)
                    caption += " ".join([segment_i_cell_j.text for segment_i_cell_j in segment_i])
            elif len(segment_i) == 1:
                caption += segment_i[0].text + "  "

    if language == "Chinese":
        p_prompt = PromptTemplate(input_variables=["text"], template=polish_prompt_ch)
    else:
        p_prompt = PromptTemplate(input_variables=["text"], template=polish_prompt_en)
    polish_chain = LLMChain(llm=ChatOpenAI(model=os.environ['MODEL_NAME']), prompt=p_prompt)
    polish_caption = polish_chain.run(text=caption)
    return polish_caption


if __name__ == "__main__":
    from tools.preprocess import any_format_to_json

    os.environ['OPENAI_API_KEY'] = "EMPTY"
    os.environ['OPENAI_API_BASE'] = "http://124.70.207.36:7002/v1"
    gt_table, propositions = any_format_to_json(r"E:\code\table_handle\tools\11.xlsx")
    caption = table2text(gt_table, is_node_type=False, coarse_grained_degree=1, fine_grained_degree=20)
    print(caption)
