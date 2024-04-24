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
from tools.kv_amend import kv_amend
from tools.func import language_judgement,sub_table_adjust
from tools.st_merge import sub_table_merge


def cmp(node1: Node, node2: Node):
    if node1.rowspan[0] < node2.rowspan[0]:
        return -1
    elif node1.rowspan[0] > node2.rowspan[0]:
        return 1
    else:
        if node1.colspan[0] < node2.colspan[0]:
            return -1
        else:
            return 1


def table2text(table_dict, is_node_type=False, coarse_grained_degree=5, fine_grained_degree=10):
    language = language_judgement(table_dict["cells"])
    if not is_node_type:
        table_dict = \
            kv_clf(table_dict, coarse_grained_degree, fine_grained_degree, checkpoint=[0, 20], language=language)[-1]
        print(table_dict)
    segmented_table: List[Set[Node]]
    segmented_table, all_table_node, rows_head = table_seg(table_dict)
    segmented_table=sub_table_adjust(segmented_table, all_table_node)
    segmented_table = sub_table_merge(segmented_table)

    caption = ""
    for i, segment_i in enumerate(segmented_table):
        segment_i = list(segment_i)
        segment_i.sort(key=cmp_to_key(cmp))
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
            print("-------------打印子表---------------------")
            print(sub_table_cell)
            try:
                _, unified_table, have_table_head = kv_amend(sub_table_cell)
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
    polish_chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat"), prompt=p_prompt)
    polish_caption = polish_chain.run(text=caption)
    return polish_caption


if __name__ == "__main__":
    from tools.preprocess import any_format_to_json

    os.environ['OPENAI_API_KEY'] = "EMPTY"
    os.environ['OPENAI_API_BASE'] = "http://124.70.207.36:7002/v1"
    gt_table, propositions = any_format_to_json(r"E:\code\table_handle\tools\11.xlsx")
    caption = table2text(gt_table, is_node_type=False, coarse_grained_degree=1, fine_grained_degree=20)
    print(caption)
