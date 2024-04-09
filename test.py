import json
from tools.table_seg import table_seg
from tools.node import Node
from tools.kv_clf import kv_clf
from tools.table2text import table2text
from tools.preprocess import any_format_to_json
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
from tools.prompt import fact_verification_analysis_prompt, fact_verification_judge_prompt
from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

os.environ['OPENAI_API_KEY'] = "EMPTY"
os.environ['OPENAI_API_BASE'] = "http://124.70.207.36:7002/v1"
analysis_prompt = PromptTemplate(input_variables=["context"], template=fact_verification_analysis_prompt)
analysis_chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat", prompt=analysis_prompt))
judge_prompt = PromptTemplate(input_variables=["context"], template=fact_verification_judge_prompt)
judge_chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat", prompt=judge_prompt))
total_TP = 0  # TP将key预测为key
total_TN = 0  # TN将value预测为value
total_FP = 0  # FN将value预测为key
total_FN = 0  # TN将key预测为value
total_fv_true_count = 0  # 统计全部命题判断正确的数量
total_fv_false_count = 0  # 统计全部命题判断错误的数量
key_clf_result = {}
for item in os.listdir("data"):
    TP = 0  # TP将key预测为key
    TN = 0  # TN将value预测为value
    FP = 0  # FN将value预测为key
    FN = 0  # TN将key预测为value
    fv_true_count = 0  # 统计此类数据命题判断正确的数量
    fv_false_count = 0  # 统计此类数据命题判断错误的数量
    item_path = os.path.join("data", item)
    for file_name in os.listdir(item_path):
        file_path = os.path.join(item_path, file_name)
        # print(file_path)
        gt_table, propositions = any_format_to_json(file_path)
        predict_table = {"cells": []}
        for cell in gt_table["cells"]:
            temp = {
                "colspan": [cell["colspan"][0], cell["colspan"][1]],
                "rowspan": [cell["rowspan"][0], cell["rowspan"][1]],
                "text": cell["text"]
            }
            predict_table["cells"].append(temp)
        predict_table = kv_clf(predict_table, coarse_grained_degree=10, fine_grained_degree=10)
        for predict_cell in predict_table["cells"]:
            for gt_cell in gt_table["cells"]:
                if predict_cell["colspan"] == gt_cell["colspan"] and predict_cell["rowspan"] == gt_cell["rowspan"]:
                    if gt_cell["node_type"] == "key":
                        if predict_cell["node_type"] == "key":
                            total_TP += 1
                            TP += 1
                        else:
                            total_FN += 1
                            FN += 1
                    else:
                        if predict_cell["node_type"] == "key":
                            total_FP += 1
                            FP += 1
                        else:
                            total_TN += 1
                            TN += 1
        table_description = table2text(predict_table, coarse_grained_degree=10, fine_grained_degree=20)
        for one_proposition in propositions:
            proposition = one_proposition["proposition"]
            value = one_proposition["value"]
            analysis_caption = analysis_chain.run(context=proposition)
            judge_caption = judge_chain.run(analysis=analysis_caption)
            if value == "1":
                if "true" in judge_caption:
                    total_fv_true_count += 1
                    fv_true_count += 1
                else:
                    total_fv_false_count += 1
                    fv_false_count += 1
            else:
                if "false" in judge_caption:
                    total_fv_true_count += 1
                    fv_true_count += 1
                else:
                    total_fv_false_count += 1
                    fv_false_count += 1

    precision = TP / (TP + FP)  # 精确率
    recall = TP / (TP + FN)  # 召回率
    accuracy = (TP + TN) / (TP + FP + TN + FN)  # 准确率
    F1_Score = 2 * (precision * recall) / (precision + recall)
    fv_accuracy = fv_true_count / (fv_true_count + fv_false_count)
    key_clf_result[item] = {"TP": TP, "TN": TN, "FP": FP, "FN": FN, "precision": precision, "recall": recall,
                            "accuracy": accuracy, "F1_Score": F1_Score, "fv_true_count": total_fv_true_count,
                            "fv_false_count": fv_false_count, "fv_accuracy": fv_accuracy}

total_precision = total_TP / (total_TP + total_FP)
total_recall = total_TP / (total_TP + total_FN)
total_accuracy = (total_TP + total_TN) / (total_TP + total_FP + total_TN + total_FN)
total_F1_Score = 2 * (total_precision * total_recall) / (total_precision + total_recall)
total_fv_accuracy = total_fv_true_count / (total_fv_true_count + total_fv_false_count)
key_clf_result["total"] = {"total_TP": total_TP, "total_TN": total_TN, "total_FP": total_FP, "total_FN": total_FN,
                           "total_precision": total_precision, "total_recall": total_recall,
                           "total_accuracy": total_accuracy, "total_F1_Score": total_F1_Score,
                           "total_fv_true_count": total_fv_true_count, "total_fv_false_count": total_fv_false_count,
                           "total_fv_accuracy": total_fv_accuracy}

with open('./key_clf_result.json', 'w', encoding='utf-8') as f:
    # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
    json.dump(key_clf_result, f, indent=4, ensure_ascii=False)
