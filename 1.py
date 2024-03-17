from typing import List, Set, Dict

# ll: Dict = {"CDXSWC": 11111}
# print(ll)
# ss="ascw\nrd  qcw\nd  qecwde"
# ss=ss.replace(" ","")
# print(ss)
# ss=ss.replace("\n","")
# print(ss)
import ast

# user = """
# {
#   "表头": [
#     "井号",
#     "井别",
#     "井型",
#     "井位坐标",
#     "X（m）",
#     "Y（m）",
#     "地面海拔（m）",
#     "补心海拔（m）",
#     "目的层",
#     "设计垂深（m）",
#     "完钻层位",
#     "完井方式",
#     "完钻原则",
#     "采(注)井段中深(m)",
#     "层位",
#     "压力资料",
#     "地层压力(MPa)",
#     "测压时间(h:min)",
#     "油压(MPa)",
#     "套压(MPa)",
#     "靶心坐标",
#     "X（m）",
#     "Y（m）",
#     "靶区半径(m)",
#     "大门方向（°）",
#     "靶点位移(m)",
#     "靶点方位（°）",
#     "中靶垂深(m)",
#     "靶心海拔(m)"
#   ]
# }
#
# """
# "dvwsc"
# user="[“井号”, “钻井顺序”, “施工井队”, “井别”, “井型”, “前拖距离（m）”, “地理位置”, “井组复测坐标（X, Y）”, “构造位置”, “井口坐标（X, Y）”, “设计位移（m）”, “设计方位（°）”, “中靶坐标（X, Y）”, “靶心半径（m）”, “磁偏角”, “中靶垂深（m）”, “设计井深（m）”, “靶心海拔（m）”, “大门方向（°）”, “地面海拔（m）”, “补心海拔（m）”, “目的层”, “完钻层位”, “完钻原则”, “完井方式”]'
# print("\n".join(user))
# user_dict = ast.literal_eval(user)
# print(user_dict,type(user_dict))
# print(user_dict["表头"])


# a=[1,2,3,4,5,6,7,8,9]
# b=[1,2,3,4,5,6,8,9,7]
# print(len(set(a)))
# print(a is b)
# a:List, b:Set=[],set()

# import random
#
# my_list = [1, 2, 3, 4, 5]
#
# # 创建列表副本
# shuffled_list = my_list.copy()
#
# # 使用 random.shuffle() 打乱副本的元素顺序
# random.shuffle(shuffled_list)
#
# print(my_list)          # 原始列表
# print(shuffled_list)    # 打乱顺序后的列表
# ss="wdecr3ewdcec{}edcewd"
# ll=[1,2,3,4,5,6,7,8,9]
# print(isinstance(ll,list))
# try:
#     raise Exception('Symbol must be a single character string.')
# except Exception as e:
#     print(e)
# for i in range(1, 11):
#     for j in range(1, 11):
#         print(i, j)
#         if j // 2 == 0:
#             break
#         print("Ss",i, j)
# ll=[[] for _ in range(4)]
# print(ll)
#
# ll[0].append(1)
# print(ll)

# class A:
#     def __init__(self):
#         self.a=1
#
# a=A()
# b=A()
# c=A()
# mm=[a,b]
# print(mm.index(c))

# import random
#
# my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# num_to_select = 5
#
# selected_values = sorted(random.sample(my_list, num_to_select))
# # selected_values.sort()
#
# print("随机选择的值：", selected_values)


# import re
#
# def keep_chinese_english(text):
#     # 使用正则表达式匹配中文汉字和英文字母
#     pattern = re.compile(r'[^a-zA-Z0-9\u4e00-\u9fa5]')
#     result = pattern.sub('', text)
#     return result
#
# # 示例
# input_string = "靶心半径(m)"
# filtered_string = keep_chinese_english(input_string)
#
# print("原始字符串:", input_string)
# print("处理后字符串:", filtered_string)


# import tabula
#
# # 从图片提取表格数据
# df = tabula.read_pdf("1.png", pages="all")
#
# # 将提取的数据保存为Excel文件
# df.to_excel("output.xlsx", index=False)
# ll=[0,1,2,3,4,5]
# for i in range(len(ll)):
#     print(ll[i])
#     ll.remove(ll[i])
# if []:
#     print(1)

import re

pattern = ".*+?^$(){}[]|\\"  # 包含一些正则表达式中的特殊字符
escaped_pattern = re.escape(pattern)

print("Original Pattern:", pattern)
print("Escaped Pattern:", escaped_pattern)
print(type(escaped_pattern))
