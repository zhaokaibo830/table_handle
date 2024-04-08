import json
from tools.table_seg import table_seg
from tools.node import Node
from tools.kv_clf import kv_clf
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


@app.post("/table/table2text")
def table2text(file: UploadFile = File(...)):
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
                caption += segment_i[0].text + "is" + segment_i[1].text + ". "
            elif len(segment_i) > 2:
                sub_table_cell = []
                for segment_i_cell_j in segment_i:
                    caption += segment_i_cell_j.text + "  "
                caption += "。"
            elif len(segment_i) == 1:
                caption += segment_i[0].text + "  "
        p_prompt = PromptTemplate(input_variables=["text"], template=polish_prompt)
        # polish_chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat"),prompt=p_prompt)
        polish_chain = LLMChain(llm=ChatOpenAI(model=sys.argv[3]),prompt=p_prompt)
        polish_caption = polish_chain.run(text=caption)
        res = {
            "data": {
                "text": polish_caption
            }
        }
        print("---------polish_caption-----------")
        print(polish_caption)
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
        caption = table2text(file)
        print("已经调用了tabletotext")
        print("caption:", caption["data"]["text"])
        text = caption["data"]["text"]
        if caption["data"]["text"] == "您的输入文件有误！":
            res = {
                "data": {
                    "answer": "您的输入文件有误！"
                }
            }

            return res
        else:
            try:
                text = caption["data"]["text"]
                prompt_template = """
                {text}
                请根据以上信息回答如下问题，
                {question}
                """
                prompt = PromptTemplate(input_variables=["text", "question"], template=prompt_template)
                # print(sys.argv[3])
                # print(type(sys.argv[3]))
                # chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat"), prompt=prompt)
                chain = LLMChain(llm=ChatOpenAI(model=sys.argv[3]), prompt=prompt)
                print("question:", question)
                result = chain.run(text=text, question=question)
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


if __name__ == "__main__":
    uvicorn.run(port=8000, app=app, host="0.0.0.0")