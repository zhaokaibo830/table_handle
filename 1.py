from openpyxl import load_workbook

# wb = load_workbook("2.xlsx")
# wbs = wb.active
# cell = wbs['A7']
# print(cell.fill.start_color)
# print(cell.fill.start_color.index)

import openpyxl

# 打开 Excel 文件
workbook = openpyxl.load_workbook('2.xlsx')

# 选择工作表
sheet = workbook['Sheet1']  # 替换为实际的工作表名称

# 获取所有合并单元格的信息
merged_cells = sheet.merged_cells.ranges

# 打印合并单元格的信息
for merged_range in merged_cells:
    print(f'Merged Range: {merged_range}')
    print(type(merged_range))

# 关闭工作簿
workbook.close()
