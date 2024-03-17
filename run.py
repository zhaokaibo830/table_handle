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

os.environ['OPENAI_API_KEY'] = "EMPTY"
os.environ['OPENAI_API_BASE'] = "http://124.70.207.36:7002/v1"


# os.environ['OPENAI_API_KEY'] = sys.argv[1]
# os.environ['OPENAI_API_BASE'] = sys.argv[2]
# print(sys.argv[1])
# print(sys.argv[2])

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


app = FastAPI()


@app.post("/table/tabletotext")
def tabletotext(file: UploadFile = File(...)):
    try:
        # 读取表格的json文件
        f = open("temp.json", 'wb')
        data = file.file.read()
        f.write(data)
        f.close()
        with open("temp.json", "r", encoding='utf-8') as f:
            table_dict: Dict = json.load(f)

        table_dict = kv_clf(table_dict)
        print(table_dict)
        segmented_table: List[Set[Node]]
        segmented_table, _, _ = table_seg(table_dict)

        caption = ""
        for i, segment_i in enumerate(segmented_table):
            segment_i = list(segment_i)
            segment_i.sort(key=cmp_to_key(cmp))
            if len(segment_i) == 2:
                caption += segment_i[0].context + "是" + segment_i[1].context + "。"
            elif len(segment_i) > 2:
                sub_table_cell = []
                for segment_i_cell_j in segment_i:
                    temp_dict = {
                        "colspan": [segment_i_cell_j.colspan[0], segment_i_cell_j.colspan[1]],
                        "rowspan": [segment_i_cell_j.rowspan[0], segment_i_cell_j.rowspan[1]],
                        "context": segment_i_cell_j.context,
                        "node_type": segment_i_cell_j.node_type
                    }
                    sub_table_cell.append(temp_dict)
                caption += simple_table_handle(sub_table_cell)
            elif len(segment_i) == 1:
                caption += segment_i[0].context + "  "
        p_prompt = PromptTemplate(input_variables=["context"], template=polish_prompt)
        polish_chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat", prompt=p_prompt))
        polish_caption = polish_chain.run(context=caption)
        res = {
            "data": {
                "text": polish_caption
            }
        }
    except Exception as e:
        print(e)
        res = {
            "data": {
                "text": "您的输入文件有误！"
            }
        }
    return res


@app.post("/table/tableqa")
def tableqa(file: UploadFile = File(...), question: str = Form(...)):
    print(question)
    try:
        caption = tabletotext(file)
        print("已经调用了tabletotext")
        print("caption:", caption["data"]["text"])
        context = caption["data"]["text"]
        if caption["data"]["text"] == "您的输入文件有误！":
            res = {
                "data": {
                    "answer": "您的输入文件有误！"
                }
            }

            return res
        else:
            try:
                context = caption["data"]["text"]
                prompt_template = """
                {context}
                请根据以上信息回答如下问题，
                {question}
                """
                prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)
                # print(sys.argv[3])
                # print(type(sys.argv[3]))
                # chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat"), prompt=prompt)
                chain = LLMChain(llm=ChatOpenAI(model=sys.argv[3]), prompt=prompt)
                print("question:", question)
                result = chain.run(context=context, question=question)
                res = {
                    "data": {
                        "answer": result
                    }
                }
            except Exception as e:
                print(e)
                res = {
                    "data": {
                        "answer": "大模型服务已关闭，请联系服务管理员。"
                    }
                }
            return res
    except Exception as e:
        print(e)
        res = {
            "data": {
                "answer": "您的输入文件有误！"
            }
        }
        return res


@app.post("/table/sub_table_extract")
def sub_table_extract(file: UploadFile = File(...), question: str = Form(...)):
    try:
        whole_caption = tabletotext(file)
        f = open("temp.json", 'wb')
        data = file.file.read()
        f.write(data)
        f.close()
        with open("temp.json", "r", encoding='utf-8') as f:
            table_dict: Dict = json.load(f)

        table_dict = kv_clf(table_dict)
        print(table_dict)
        segmented_table: List[Set[Node]]
        segmented_table, _, _ = table_seg(table_dict)
        documents: List[Document] = []
        ste_prompt = PromptTemplate(input_variables=["context"], template=sub_table_extract_prompt)
        ste_chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat", prompt=ste_prompt))
        embeddings = OpenAIEmbeddings(model="text-davinci-003", request_timeout=120)

        for i, segment_i in enumerate(segmented_table):
            segment_i = list(segment_i)
            segment_i.sort(key=cmp_to_key(cmp))
            if len(segment_i) == 2:
                i_caption = segment_i[0].context + "是" + segment_i[1].context + "。"
            elif len(segment_i) > 2:
                sub_table_cell = []
                for segment_i_cell_j in segment_i:
                    temp_dict = {
                        "colspan": [segment_i_cell_j.colspan[0], segment_i_cell_j.colspan[1]],
                        "rowspan": [segment_i_cell_j.rowspan[0], segment_i_cell_j.rowspan[1]],
                        "context": segment_i_cell_j.context,
                        "node_type": segment_i_cell_j.node_type
                    }
                    sub_table_cell.append(temp_dict)
                i_caption = simple_table_handle(sub_table_cell)
            else:
                i_caption = segment_i[0].context + "  "
            i_caption = ste_chain.run(whole_caption=whole_caption, i_caption=i_caption)
            metadata = {"source_sub_table_index": i}
            documents.append(Document(page_content=i_caption, metadata=metadata))

        faiss_index = FAISS.from_documents(documents, embeddings)
        docs = faiss_index.similarity_search(question, k=1)
        index = docs[0].metadata["source_sub_table_index"]
        extractd_sub_table = segmented_table[index]
        extractd_sub_table_list = []
        for i_cell in list(extractd_sub_table):
            temp = {
                "colspan": [i_cell.colspan[0], i_cell.colspan[1]],
                "rowspan": [i_cell.rowspan[0], i_cell.rowspan[1]],
                "context": i_cell.context,
            }
            extractd_sub_table_list.append(temp)
        res = {
            "data": {
                "answer": extractd_sub_table_list
            }
        }
        return res
    except Exception as e:
        print(e)
        res = {
            "data": {
                "answer": "输入的表格有误！"
            }
        }
        return res


if __name__ == "__main__":
    uvicorn.run(port=8000, app=app, host="0.0.0.0")
