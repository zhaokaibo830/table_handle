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
from tools.prompt import fact_verification_analysis_prompt_en, fact_verification_judge_prompt_en
from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from tools.kv_amend import kv_amend
from tools.func import language_judgement

os.environ['OPENAI_API_KEY'] = "EMPTY"
os.environ['OPENAI_API_BASE'] = "http://124.70.207.36:7002/v1"
analysis_prompt = PromptTemplate(input_variables=["context", "proposition"],
                                 template=fact_verification_analysis_prompt_en)
analysis_chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat"), prompt=analysis_prompt)
judge_prompt = PromptTemplate(input_variables=["analysis"], template=fact_verification_judge_prompt_en)
judge_chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat"), prompt=judge_prompt)


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


def kv_fv_test(coarse_grained_degree, fine_grained_degree, file_path, fine_degrees):
    gt_table, propositions = any_format_to_json(file_path)
    predict_table = {"cells": []}
    for cell in gt_table["cells"]:
        temp = {
            "colspan": [cell["colspan"][0], cell["colspan"][1]],
            "rowspan": [cell["rowspan"][0], cell["rowspan"][1]],
            "text": cell["text"]
        }
        predict_table["cells"].append(temp)
    language = language_judgement(predict_table["cells"])
    predict_table_list = kv_clf(predict_table, coarse_grained_degree=coarse_grained_degree,
                                fine_grained_degree=fine_grained_degree, checkpoint=fine_degrees, language=language)
    one_file_result = {}

    for i, predict_table in enumerate(predict_table_list):
        TP = 0  # TP将key预测为key
        TN = 0  # TN将value预测为value
        FP = 0  # FN将value预测为key
        FN = 0  # TN将key预测为value
        fv_true_count = 0  # 统计此类数据命题判断正确的数量
        fv_false_count = 0  # 统计此类数据命题判断错误的数量
        segmented_table, _, _ = table_seg(predict_table)

        caption = ""
        predict_table = {"cells": []}
        for j, segment_i in enumerate(segmented_table):
            sub_table_cell = []
            for segment_i_cell_j in segment_i:
                sub_table_cell.append({
                    "colspan": [segment_i_cell_j.colspan[0], segment_i_cell_j.colspan[1]],
                    "rowspan": [segment_i_cell_j.rowspan[0], segment_i_cell_j.rowspan[1]],
                    "text": segment_i_cell_j.text,
                    "node_type": segment_i_cell_j.node_type
                })
            amended_table, _, _ = kv_amend(sub_table_cell)
            predict_table["cells"].extend(amended_table)
        print("----------打印最后的predict_table---------")
        print(predict_table)
        for predict_cell in predict_table["cells"]:
            for gt_cell in gt_table["cells"]:
                if predict_cell["colspan"] == gt_cell["colspan"] and predict_cell["rowspan"] == gt_cell["rowspan"]:
                    if gt_cell["node_type"] == "key":
                        if predict_cell["node_type"] == "key":
                            TP += 1
                        else:
                            FN += 1
                    else:
                        if predict_cell["node_type"] == "key":
                            FP += 1
                        else:
                            TN += 1
        table_description = table2text(predict_table, is_node_type=True)
        for one_proposition in propositions:
            proposition = one_proposition["proposition"]
            value = one_proposition["value"]
            analysis_caption = analysis_chain.run(context=table_description, proposition=proposition)
            judge_caption = judge_chain.run(analysis=analysis_caption)
            if value == "1":
                if "true" in judge_caption:
                    fv_true_count += 1
                else:
                    fv_false_count += 1
            else:
                if "false" in judge_caption:
                    fv_true_count += 1
                else:
                    fv_false_count += 1
        precision = TP / (TP + FP)
        recall = TP / (TP + FN)
        accuracy = (TP + TN) / (TP + FP + TN + FN)
        F1_Score = 2 * (precision * recall) / (precision + recall)
        fv_accuracy = fv_true_count / (fv_true_count + fv_false_count)
        one_file_result["fine_degree-" + str(fine_degrees[i])] = {"TP": TP, "TN": TN, "FP": FP,
                                                                  "FN": FN, "table_description": table_description,
                                                                  "fv_true_count": fv_true_count,
                                                                  "fv_false_count": fv_false_count,
                                                                  "precision": precision, "recall": recall,
                                                                  "accuracy": accuracy, "F1_Score": F1_Score,
                                                                  "fv_accuracy": fv_accuracy}

    return one_file_result


if __name__ == "__main__":

    while True:
        for item in os.listdir("data"):
            if item not in os.listdir("result"):
                os.mkdir(os.path.join("result", item))
            item_path = os.path.join("data", item)
            for file_name in os.listdir(item_path):
                # try:
                print(item + file_name.split(".")[0] + ".json")
                if file_name.split(".")[0] + ".json" in os.listdir(os.path.join("result", item)):
                    continue
                one_file_result = kv_fv_test(coarse_grained_degree=1, fine_grained_degree=50,
                                             file_path=os.path.join(item_path, file_name),
                                             fine_degrees=[_ for _ in range(0, 51, 2)])
                with open(os.path.join("result", item, file_name.split(".")[0] + ".json"), 'w',
                          encoding='utf-8') as f:
                    # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
                    json.dump(one_file_result, f, indent=4, ensure_ascii=False)
                # except Exception as e:
                #     print("************************************************************************")
                #     print(e)
                #     print(item + file_name.split(".")[0] + ".json" + "处理异常！！！！")
                #     print("************************************************************************")

    # for item in os.listdir("result"):
    #     item_path = os.path.join("result", item)
    #     one_class_TP = 0
    #     one_class_TN = 0
    #     one_class_FP = 0
    #     one_class_FN = 0
    #     one_class_fv_true_count = 0
    #     one_class_fv_false_count = 0
    #     if "one_class_result.json" in os.listdir(os.path.join("result", item)):
    #         continue
    #     one_class_result = {}
    #     for file_name in os.listdir(item_path):
    #         with open(os.path.join("result", item, file_name), "r", encoding='utf-8') as f:
    #             one_file_result: Dict = json.load(f)
    #         for fine_degree in one_file_result.keys():
    #             if fine_degree in one_class_result:
    #                 one_class_result[fine_degree]["TP"] += one_file_result[fine_degree]["TP"]
    #                 one_class_result[fine_degree]["TN"] += one_file_result[fine_degree]["TN"]
    #                 one_class_result[fine_degree]["FP"] += one_file_result[fine_degree]["FP"]
    #                 one_class_result[fine_degree]["FN"] += one_file_result[fine_degree]["FN"]
    #                 one_class_result[fine_degree]["fv_true_count"] += one_file_result[fine_degree]["fv_true_count"]
    #                 one_class_result[fine_degree]["fv_false_count"] += one_file_result[fine_degree][
    #                     "fv_false_count"]
    #             else:
    #                 one_class_result[fine_degree]["TP"] = one_file_result[fine_degree]["TP"]
    #                 one_class_result[fine_degree]["TN"] = one_file_result[fine_degree]["TN"]
    #                 one_class_result[fine_degree]["FP"] = one_file_result[fine_degree]["FP"]
    #                 one_class_result[fine_degree]["FN"] = one_file_result[fine_degree]["FN"]
    #                 one_class_result[fine_degree]["fv_true_count"] = one_file_result[fine_degree]["fv_true_count"]
    #                 one_class_result[fine_degree]["fv_false_count"] = one_file_result[fine_degree][
    #                     "fv_false_count"]
    #
    #     for fine_degree in one_class_result.keys():
    #         total_TP = one_class_result[fine_degree]["TP"]
    #         total_TN = one_class_result[fine_degree]["TN"]
    #         total_FP = one_class_result[fine_degree]["FP"]
    #         total_FN = one_class_result[fine_degree]["FN"]
    #         total_fv_true_count = one_class_result[fine_degree]["fv_true_count"]
    #         total_fv_false_count = one_class_result[fine_degree]["fv_false_count"]
    #
    #         total_precision = total_TP / (total_TP + total_FP)
    #         total_recall = total_TP / (total_TP + total_FN)
    #         total_accuracy = (total_TP + total_TN) / (
    #                 total_TP + total_FP + total_TN + total_FN)
    #         total_F1_Score = 2 * (total_precision * total_recall) / (
    #                 total_precision + total_recall)
    #         total_fv_accuracy = total_fv_true_count / (total_fv_true_count + total_fv_false_count)
    #         one_class_result[fine_degree]["precision"] = total_precision
    #         one_class_result[fine_degree]["recall"] = total_recall
    #         one_class_result[fine_degree]["accuracy"] = total_accuracy
    #         one_class_result[fine_degree]["F1Score"] = total_F1_Score
    #         one_class_result[fine_degree]["fv_accuracy"] = total_fv_accuracy
    #
    #     with open(os.path.join("result", item, "one_class_result.json"), 'w', encoding='utf-8') as f:
    #         # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
    #         json.dump(one_class_result, f, indent=4, ensure_ascii=False)

    # total_result={}
    # for item in os.listdir("result"):
    #     with open(os.path.join("result", item, "one_class_result.json"), "r", encoding='utf-8') as f:
    #         one_class_result = json.load(f)
    #     for fine_degree in one_class_result.keys():
    #         if fine_degree in total_result:
    #             total_result[fine_degree]["TP"] += one_class_result[fine_degree]["TP"]
    #             total_result[fine_degree]["TN"] += one_class_result[fine_degree]["TN"]
    #             total_result[fine_degree]["FP"] += one_class_result[fine_degree]["FP"]
    #             total_result[fine_degree]["FN"] += one_class_result[fine_degree]["FN"]
    #             total_result[fine_degree]["fv_true_count"] += one_class_result[fine_degree]["fv_true_count"]
    #             total_result[fine_degree]["fv_false_count"] += one_class_result[fine_degree][
    #                 "fv_false_count"]
    #         else:
    #             total_result[fine_degree]["TP"] = one_class_result[fine_degree]["TP"]
    #             total_result[fine_degree]["TN"] = one_class_result[fine_degree]["TN"]
    #             total_result[fine_degree]["FP"] = one_class_result[fine_degree]["FP"]
    #             total_result[fine_degree]["FN"] = one_class_result[fine_degree]["FN"]
    #             total_result[fine_degree]["fv_true_count"] = one_class_result[fine_degree]["fv_true_count"]
    #             total_result[fine_degree]["fv_false_count"] = one_class_result[fine_degree][
    #                 "fv_false_count"]
    # for fine_degree in total_result.keys():
    #     total_TP=total_result[fine_degree]["TP"]
    #     total_TN=total_result[fine_degree]["TN"]
    #     total_FP=total_result[fine_degree]["FP"]
    #     total_FN=total_result[fine_degree]["FN"]
    #     total_fv_true_count=total_result[fine_degree]["fv_true_count"]
    #     total_fv_false_count=total_result[fine_degree]["fv_false_count"]
    #
    #     total_precision = total_TP / (total_TP + total_FP)
    #     total_recall = total_TP / (total_TP + total_FN)
    #     total_accuracy = (total_TP + total_TN) / (
    #             total_TP + total_FP + total_TN + total_FN)
    #     total_F1_Score = 2 * (total_precision * total_recall) / (
    #             total_precision + total_recall)
    #     total_fv_accuracy = total_fv_true_count / (total_fv_true_count + total_fv_false_count)
    #     total_result[fine_degree]["precision"]=total_precision
    #     total_result[fine_degree]["recall"]=total_recall
    #     total_result[fine_degree]["accuracy"]=total_accuracy
    #     total_result[fine_degree]["F1Score"]=total_F1_Score
    #     total_result[fine_degree]["fv_accuracy"]=total_fv_accuracy
    #
    # with open(os.path.join("result", "total_result.json"), 'w', encoding='utf-8') as f:
    #     # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
    #     json.dump(total_result, f, indent=4, ensure_ascii=False)
