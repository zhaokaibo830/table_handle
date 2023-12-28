import json
from tools.node import Node

with open("test.json", "r", encoding='utf-8') as f:
    table_dict = json.load(f)
print(table_dict)
print(type(table_dict))
root = Node(children=[])
for one_row in table_dict['trs']:
    all_cells_of_row = one_row['tds']
    for cell in all_cells_of_row:
        root.children.append(Node(colspan=cell['colspan'], rowspan=cell['rowspan'], context=cell['context']))
    pass
