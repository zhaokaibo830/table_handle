import json
from tools.node import Node
from LocalModels.LocalLLM import Vicuna
from LocalModels.Url_Test import Available_url
from tools.func import is_align, merge_node, get_key_value
from configs.config import score, score_threshold, n_generate_sample, value_map
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate
from tools.prompt import value_prompt

url = Available_url().url
print(url)
llm = Vicuna(url)
# prompt_template = PromptTemplate.from_template(template=value_prompt)
# llm_chain = ConversationChain(llm=llm,
#                               prompt=prompt_template,
#                               memory=ConversationSummaryBufferMemory(llm=llm, max_token_limit=0,ai_prefix="AI:",human_prefix="问题："),
#                               verbose=False)
# res=llm(value_prompt.format(input="井号是井别"))
# res=llm_chain.run({"input":"井号是井别"})
# print(res)
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
merge_log=[]
while True:
    max_score = 0
    max_i, max_j = -1, -1
    for i in range(len(root.children)):
        for j in range(len(root.children)):
            print("***********正在处理的节点：****************")
            print("输出第i个节点：")
            print("context:",root.children[i].context)
            print("colspan:",root.children[i].colspan)
            print("rowspan:",root.children[i].rowspan)
            print("输出第j个节点：")
            print("context:", root.children[j].context)
            print("colspan:", root.children[j].colspan)
            print("rowspan:", root.children[j].rowspan)
            print("***************************")
            if not is_align(root.children[i], root.children[j]):
                continue
            i_val, j_val = root.children[i].context, root.children[j].context
            key,value = root.children[i], root.children[j]
            llm_result=[]
            for _ in range(n_generate_sample):
                llm_val=llm(value_prompt.format(key=key.context,value=value.context))
                if "是" in llm_val:
                    llm_result.append("是")
                if "否" in llm_val:
                    llm_result.append('否')
                if "可能" in llm_val:
                    llm_result.append('可能')
            value = sum(value * llm_result.count(name) for name, value in value_map.items())
            print("value:",value)
            if max_score <= value:
                max_score = value
                max_i, max_j = i, j

    if max_score < score_threshold:
        break
    merged_colspan, merged_rowspan, merged_context = merge_node(root.children[max_i], root.children[max_j])
    new_node = Node(colspan=merged_colspan, rowspan=merged_rowspan, context=merged_context)
    root.children.pop(max_i)
    root.children.pop(max_j)
    root.children.append(new_node)
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print("merged_context:",merged_context)
    merge_log.append(merged_context)
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print("merge_log:",merge_log)

print("merge_log:",merge_log)
