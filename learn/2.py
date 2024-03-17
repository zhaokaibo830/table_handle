import openpyxl

# 打开 Excel 文件
workbook = openpyxl.load_workbook('table样例.xlsx')

# 选择一个工作表（可以通过工作表名称或索引）
sheet = workbook['Sheet1']  # 或者使用索引：sheet = workbook.worksheets[0]

# 获取所有合并单元格的信息
merged_cells = sheet.merged_cells.ranges

# 打印合并单元格的信息
for merged_range in merged_cells:
    print(f'Merged Range: {merged_range}')

# 关闭工作簿
workbook.close()