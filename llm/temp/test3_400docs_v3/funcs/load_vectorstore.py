# -*- coding:utf-8 -*-
import os

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms.base import LLM
from typing import List, Optional
import requests
import json
from langchain.vectorstores import FAISS
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI



os.environ['OPENAI_API_KEY']="EMPTY"
os.environ['OPENAI_API_BASE']="http://124.70.207.36:7002/v1"
embedding = OpenAIEmbeddings(model="text-davinci-003")
llm=ChatOpenAI(model="qwen-14b-chat")

def start():
    global llm,embedding
    all_faiss_index = {}
    txt_path = r'/root/report_qa_new/test3_400docs_v3/plain_text'
    vs_path = r'/root/report_qa_new/test3_400docs_v3/pregenerated_faiss'
    with open(r'/root/report_qa_new/test3_400docs_v3/' + 'txt_faiss_map.json', encoding="utf-8") as f:
        txt_faiss_map = json.load(f)
    for i, dir_name in enumerate(os.listdir(txt_path)):
        temp = {}
        for file_name in os.listdir(txt_path + '/' + dir_name + "/"):
            if dir_name == "钻井地质设计报告":
                faiss_index = FAISS.load_local(vs_path + '/' + 'zuanjing', embedding, txt_faiss_map[file_name])
                temp[file_name.split('井')[0] + '井'] = (faiss_index, file_name[:-4])
            elif dir_name == "油田开发年报":
                faiss_index = FAISS.load_local(vs_path + '/' + 'youtian', embedding, txt_faiss_map[file_name])
                temp[file_name.split('年')[0] + '年'] = (faiss_index, file_name[:-4])
            elif dir_name == "气田开发年报":
                faiss_index = FAISS.load_local(vs_path + '/' + 'qitian', embedding, txt_faiss_map[file_name])
                temp[file_name.split('年')[0] + '年'] = (faiss_index, file_name[:-4])
        all_faiss_index[dir_name] = temp
    print("all_faiss_index:", all_faiss_index)
    return all_faiss_index, llm



def start_table():
    global llm,embedding
    all_faiss_index_table = {}
    pdf_path = r'/root/report_qa_new/test3_400docs_v3/PDF'
    vs_path = r'/root/report_qa_new/test3_400docs_v3/pregenerated_faiss'
    with open(r'/root/report_qa_new/test3_400docs_v3/' + 'pdf_faiss_map.json', encoding="utf-8") as f:
        pdf_faiss_map = json.load(f)
    for i, dir_name in enumerate(os.listdir(pdf_path)):
        temp = {}
        for file_name in os.listdir(pdf_path + '/' +  dir_name + "/"):
            if dir_name == "钻井地质设计报告":
                faiss_index = FAISS.load_local(vs_path + '/' + 'zuanjing', embedding, pdf_faiss_map[file_name])
                temp[file_name.split('井')[0] + '井'] = (faiss_index, file_name[:-4])
            elif dir_name == "油田开发年报":
                faiss_index = FAISS.load_local(vs_path + '/' + 'youtian', embedding, pdf_faiss_map[file_name])
                temp[file_name.split('年')[0] + '年'] = (faiss_index, file_name[:-4])
            elif dir_name == "气田开发年报":
                faiss_index = FAISS.load_local(vs_path + '/' + 'qitian', embedding, pdf_faiss_map[file_name])
                temp[file_name.split('年')[0] + '年'] = (faiss_index, file_name[:-4])
        all_faiss_index_table[dir_name] = temp
    print("all_faiss_index_table:", all_faiss_index_table)
    return all_faiss_index_table