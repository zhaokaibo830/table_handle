
from typing import List, Set, Dict

import json
import os



def cal_f1score(path):
    TP = 0  # TP将key预测为key
    TN = 0  # TN将value预测为value
    FP = 0  # FN将value预测为key
    FN = 0  # TN将key预测为value
    for table_path in os.listdir(path):
        table_path = os.path.join(path, table_path)
        with open(os.path.join(path, table_path, "json_gt.json"), "r", encoding='utf-8') as f:
            gt_table: Dict = json.load(f)
        with open(os.path.join(path, table_path, "our_json.json"), "r", encoding='utf-8') as f:
            predict_table: Dict = json.load(f)

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
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    accuracy = (TP + TN) / (TP + FP + TN + FN)
    F1_Score = 2 * (precision * recall) / (precision + recall)
    result = {"TP": TP,
              "TN": TN,
              "FP": FP,
              "FN": FN,
              "precision": precision,
              "recall": recall,
              "accuracy": accuracy,
              "F1_Score": F1_Score
              }

    print(result)
    with open("f1score.json", 'w', encoding='utf-8') as f:
        # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
        json.dump(result, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    cal_f1score(r"C:\Users\A\Desktop\表格数据集")
