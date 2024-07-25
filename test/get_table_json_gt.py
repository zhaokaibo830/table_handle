import os
import json

from tools.preprocess import excel_to_json

def get_table_json_gt(path):
    for table_path in os.listdir(path):
        excel_path=os.path.join(path,table_path,"excel.xlsx")
        table = excel_to_json(excel_path)
        with open(os.path.join(path,table_path,"json_gt.json"), 'w', encoding='utf-8') as f:
            # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
            json.dump(table, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    get_table_json_gt(r"C:\Users\A\Desktop\表格数据集")




