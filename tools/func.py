from typing import List

def language_judgement(table:List)->str:
    """
    判断输入的表格是中文还是英文
    :param table:
    :return:
    """
    for cell in table:
        str_text = cell['text']
        for char in str_text:
            if "\u4e00" <= char <= "\u9fff":
                return "Chinese"

    return "English"

if __name__ == '__main__':
    print(language_judgement([
            {"text":"frvefcvecs"},
            {"text":"    你1234e123     "}
        ]))