import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, Body
import os
from tools.preprocess import excel_to_json
from tools.table2text import table2text
import json
from typing import List, Set, Dict
from pydantic import BaseModel

os.environ['OPENAI_API_KEY'] = "EMPTY"
os.environ['OPENAI_API_BASE'] = "http://124.70.213.108:7009/v1"
# os.environ['OPENAI_API_BASE'] = "http://10.8.0.6:7002/v1"
os.environ['MODEL_NAME'] = "qwen1.5-14b-chat"

app = FastAPI()


class Item(BaseModel):
    content: List


@app.post("/api/table2text")
async def input_json(item: Item = Body(...)):
    """
    :param item: 接受的json不是文件
    :return:输出表格的描述
    """
    # try:
    for i_cell in item.content:
        if "node_type" not in i_cell:
            i_cell["node_type"] = "value"
    print("-------------------input-----------------------------------")
    print({"content": item.content})
    print("-------------------------------------------------------------")
    print(111111111111111111)
    res = await table2text({"cells": item.content})
    # except Exception as e:
    #     print(e)
    #     res = "表格理解出错！！！"
    print("-------------------output-----------------------------------")
    print(res)
    print("-------------------------------------------------------------")
    return {"text": res}


@app.post("/api/table2text_excel")
async def input_excel(file: UploadFile = File(...)):
    """
    :param file: 接收excel文件
    :return: 输出表格的描述
    """
    try:
        # 读取表格的json文件
        f = open("temp.xlsx", 'wb')
        data = file.file.read()
        f.write(data)
        f.close()
        table_dict = excel_to_json("temp.xlsx")
        print("-------------------读取excel-->json-----------------------------------")
        print(table_dict)
        print("-------------------------------------------------------------")
        res = await table2text(table_dict)
    except Exception as e:
        print(e)
        res = "表格理解出错！！！"
    print("-------------------output-----------------------------------")
    print(res)
    print("-------------------------------------------------------------")
    return res


@app.post("/api/table2text_json_file")
async def input_json_file(file: UploadFile = File(...)):
    """
    :param file: 接收的json是文件
    :return:
    """
    try:
        # 读取表格的json文件
        f = open("temp.json", 'wb')
        data = file.file.read()
        f.write(data)
        f.close()
        with open("temp.json", "r", encoding='utf-8') as f:
            table_dict: Dict = json.load(f)
        print("-------------------input-----------------------------------")
        print(table_dict)
        print("-------------------------------------------------------------")
        res = await table2text({"cells": table_dict["content"]})

    except Exception as e:
        print(e)
        res = "表格理解出错！！！"
    print("-------------------output-----------------------------------")
    print(res)
    print("-------------------------------------------------------------")
    return res


if __name__ == "__main__":
    for key, value in os.environ.items():
        print(f"{key}: {value}")
    uvicorn.run(port=8005, app=app, host="0.0.0.0")
