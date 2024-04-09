import json
from tools.table_seg import table_seg
from tools.node import Node
from tools.kv_clf import kv_clf
from tools.simple_table_handle import simple_table_handle
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
from tools.prompt import polish_prompt, sub_table_extract_prompt
from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS


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


def table2text(table_dict, coarse_grained_degree, fine_grained_degree):
    table_dict = kv_clf(table_dict, coarse_grained_degree, fine_grained_degree)
    print(table_dict)
    segmented_table: List[Set[Node]]
    segmented_table, _, _ = table_seg(table_dict)

    caption = ""
    for i, segment_i in enumerate(segmented_table):
        segment_i = list(segment_i)
        segment_i.sort(key=cmp_to_key(cmp))
        if len(segment_i) == 2:
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
            caption += simple_table_handle(sub_table_cell)
        elif len(segment_i) == 1:
            caption += segment_i[0].text + "  "
    p_prompt = PromptTemplate(input_variables=["text"], template=polish_prompt)
    polish_chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat", prompt=p_prompt))
    polish_caption = polish_chain.run(text=caption)
    return polish_caption
