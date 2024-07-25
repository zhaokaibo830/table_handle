from tools.table_seg import table_seg
from typing import List, Set, Dict
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form
import json
from tools.kv_amend import sub_table_kv_amend, table_kv_amend
from tools.func import language_judgement, sub_table_adjust, cmp_dict, cmp_node
from tools.st_merge import sub_table_merge
from functools import cmp_to_key
from tools.simple_table2text import simple_table2text
import os

def get_gt_text_by_json_gt(path):
    for table_path in os.listdir(path):
        json_gt_path=os.path.join(path,table_path,"json_gt.json")

        with open(json_gt_path, "r", encoding='utf-8') as f:
            table_dict: Dict = json.load(f)

        language = language_judgement(table_dict["cells"])
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
        print(caption)
        with open(os.path.join(path,table_path,"no_polish_gt_text.txt"), 'w') as file:
            # 写入内容到文件
            file.write(caption)


if __name__ == "__main__":
    get_gt_text_by_json_gt(r"C:\Users\A\Desktop\表格数据集")