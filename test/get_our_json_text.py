import json

from tools.preprocess import excel_to_json
from tools.table_seg import table_seg
from tools.node import Node
from tools.kv_clf import kv_clf
from tools.simple_table2text import simple_table2text
from functools import cmp_to_key
from typing import List, Set, Dict
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form
import os
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from tools.prompt import polish_prompt_en, sub_table_extract_prompt_en, polish_prompt_ch, sub_table_extract_prompt_ch
from tools.kv_amend import sub_table_kv_amend, table_kv_amend
from tools.func import language_judgement, sub_table_adjust, cmp_dict, cmp_node
from tools.st_merge import sub_table_merge
from tools.is_simple_table import is_simple_table
from tools.create_cross_list import create_cross_list
from tools.func import is_rectangle
from langchain_core.output_parsers import StrOutputParser
import asyncio

app = FastAPI()


os.environ['MODEL_NAME']="gpt-4o-mini"
os.environ['OPENAI_API_BASE']="https://api.chatanywhere.com.cn/v1"
os.environ['OPENAI_API_KEY'] ="sk-Mj4ShXvqWIAEexqoQfBqdwjAKvFeOcVGiiXn2heC3b9bukw4"

# os.environ['MODEL_NAME']="qwen1.5-14b-chat"
# os.environ['OPENAI_API_BASE']="http://124.70.213.108:7009/v1"
# os.environ['OPENAI_API_KEY'] ="EMPTY"

async def get_our_json_text(path):
    for i,table_path in enumerate(os.listdir(path)):
        if i!=0:
            continue
        excel_path=os.path.join(path,table_path,"excel.xlsx")
        table_dict = excel_to_json(excel_path)
        is_node_type = False
        coarse_grained_degree = 1
        fine_grained_degree = 0

        print("fine_grained_degree:", fine_grained_degree)

        table_dict["cells"].sort(key=cmp_to_key(cmp_dict))
        language = language_judgement(table_dict["cells"])

        for cell in table_dict["cells"]:
            cell["node_type"]="value"

        whole_table_amended_table, whole_table_unified_table, whole_table_have_table_head = await is_simple_table(
            table_dict["cells"], language)
        segmented_table: List[Set[Node]] = []
        if whole_table_have_table_head:
        # if False:
            table_dict={"cells":whole_table_amended_table}
            print("******表格类型，是一个简单表格********")
            segmented_table, all_table_node, rows_head = table_seg({"cells": whole_table_unified_table})
            segmented_table = sub_table_merge(segmented_table, all_table_node)
        else:
            print("******表格类型，是一个复杂表格********")
            if not is_node_type:
                table_dict = \
                    (await kv_clf(table_dict, coarse_grained_degree, fine_grained_degree,
                                  checkpoint=[0, fine_grained_degree],
                                  language=language))[-1]
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
        llm = ChatOpenAI(model=os.environ['MODEL_NAME'])
        print("caption:", caption)
        polish_chain = p_prompt | llm | StrOutputParser()
        polish_caption = await polish_chain.ainvoke({"text": caption})
        # polish_chain = LLMChain(llm=ChatOpenAI(model=os.environ['MODEL_NAME']), prompt=p_prompt)
        # polish_caption = polish_chain.run(text=caption)
        print("polish_caption:", polish_caption)
        print("table_dict:", table_dict)
        with open(os.path.join(path,table_path,"ours_text.txt"), 'w') as file:
            # 写入内容到文件
            file.write(polish_caption)
        with open(os.path.join(path,table_path,"our_json.json"), 'w', encoding='utf-8') as f:
            # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
            json.dump(table_dict, f, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    asyncio.run(get_our_json_text(r"C:\Users\A\Desktop\表格数据集"))
