import asyncio
import json

from fastapi import FastAPI, File, UploadFile, Form
import os
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from langchain_core.output_parsers import StrOutputParser
import asyncio
import chardet

app = FastAPI()

os.environ['MODEL_NAME'] = "gpt-4o-mini"
os.environ['OPENAI_API_BASE'] = "https://api.chatanywhere.com.cn/v1"
os.environ['OPENAI_API_KEY'] = "sk-Mj4ShXvqWIAEexqoQfBqdwjAKvFeOcVGiiXn2heC3b9bukw4"

# os.environ['MODEL_NAME'] = "qwen1.5-14b-chat"
# os.environ['OPENAI_API_BASE'] = "http://124.70.213.108:7009/v1"
# os.environ['OPENAI_API_KEY'] = "EMPTY"

smi_prompt = """您现在是一个文本生成助手的评估专家。在用户输入一个复杂表格后，用户要求AI助手对该表格进行总结和描述，AI助手提供了一个回答。我们有一个标准答案，希望您将标准答案与AI助手的回答进行比较，并为AI助手的回答评分。评分范围是1到10分，AI助手回答的越详细、内容越精确并且整体表现越好则分数越高表示，AI助手回答冗余不会减分。输出模板如下：
[分析过程：...,分数：...]

AI助手的结果如下：
{test_text}
            
标准答案如下：           
{gt_text}
            """


async def our_smi(path):
    score = 0
    for i, table_path in enumerate(os.listdir(path)):
        tag = True
        while tag:
            try:
                with open(os.path.join(path, table_path, "gt_text.txt"), 'rb') as file:
                    encoding = chardet.detect(file.read())['encoding']
                with open(os.path.join(path, table_path, "gt_text.txt"), "r", encoding=encoding) as f:
                    gt_text = f.read()
                with open(os.path.join(path, table_path, "ours_text.txt"), 'rb') as file:
                    encoding = chardet.detect(file.read())['encoding']
                with open(os.path.join(path, table_path, "ours_text.txt"), "r", encoding=encoding) as f:
                    our_text = f.read()
                cal_smi_prompt = PromptTemplate(input_variables=["text"], template=smi_prompt)
                llm = ChatOpenAI(model=os.environ['MODEL_NAME'])
                cal_smi_chain = cal_smi_prompt | llm | StrOutputParser()
                polish_caption = await cal_smi_chain.ainvoke({"test_text": our_text, "gt_text": gt_text})
                print("gt_text:", gt_text)
                print("our_text:", our_text)
                print("polish_caption:", polish_caption)
                temp_score = ""
                for char in polish_caption[polish_caption.index('分数：') + 2:]:
                    if char.isdigit():
                        temp_score += char
                    elif temp_score:
                        break
                score += int(temp_score)
                print("score:", score)

                tag = False
            except Exception as e:
                print(e)
    with open("our_score.json", 'w', encoding='utf-8') as f:
        # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
        json.dump({"average_score": score / len(os.listdir(path))}, f, indent=4, ensure_ascii=False)

async def qwen_smi(path):
    score = 0
    for i, table_path in enumerate(os.listdir(path)):
        tag = True
        while tag:
            try:
                with open(os.path.join(path, table_path, "gt_text.txt"), 'rb') as file:
                    encoding = chardet.detect(file.read())['encoding']
                with open(os.path.join(path, table_path, "gt_text.txt"), "r", encoding=encoding) as f:
                    gt_text = f.read()
                with open(os.path.join(path, table_path, "qwen_text.txt"), 'rb') as file:
                    encoding = chardet.detect(file.read())['encoding']
                with open(os.path.join(path, table_path, "qwen_text.txt"), "r", encoding=encoding) as f:
                    qwen_text = f.read()
                cal_smi_prompt = PromptTemplate(input_variables=["text"], template=smi_prompt)
                llm = ChatOpenAI(model=os.environ['MODEL_NAME'])
                cal_smi_chain = cal_smi_prompt | llm | StrOutputParser()
                polish_caption = await cal_smi_chain.ainvoke({"test_text": qwen_text, "gt_text": gt_text})
                print("gt_text:", gt_text)
                print("our_text:", qwen_text)
                print("polish_caption:", polish_caption)
                temp_score = ""
                for char in polish_caption[polish_caption.index('分数：') + 2:]:
                    if char.isdigit():
                        temp_score += char
                    elif temp_score:
                        break
                score += int(temp_score)
                print("score:", score)

                tag = False
            except Exception as e:
                print(e)
    with open("qwen_score.json", 'w', encoding='utf-8') as f:
        # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
        json.dump({"average_score": score / len(os.listdir(path))}, f, indent=4, ensure_ascii=False)

async def chatgpt_smi(path):
    score = 0
    for i, table_path in enumerate(os.listdir(path)):
        tag = True
        while tag:
            try:
                with open(os.path.join(path, table_path, "gt_text.txt"), 'rb') as file:
                    encoding = chardet.detect(file.read())['encoding']
                with open(os.path.join(path, table_path, "gt_text.txt"), "r", encoding=encoding) as f:
                    gt_text = f.read()
                with open(os.path.join(path, table_path, "chatgpt_text.txt"), 'rb') as file:
                    encoding = chardet.detect(file.read())['encoding']
                with open(os.path.join(path, table_path, "chatgpt_text.txt"), "r", encoding=encoding) as f:
                    chatgpt_text = f.read()
                cal_smi_prompt = PromptTemplate(input_variables=["text"], template=smi_prompt)
                llm = ChatOpenAI(model=os.environ['MODEL_NAME'])
                cal_smi_chain = cal_smi_prompt | llm | StrOutputParser()
                polish_caption = await cal_smi_chain.ainvoke({"test_text": chatgpt_text, "gt_text": gt_text})
                print("gt_text:", gt_text)
                print("our_text:", chatgpt_text)
                print("polish_caption:", polish_caption)
                temp_score = ""
                for char in polish_caption[polish_caption.index('分数：') + 2:]:
                    if char.isdigit():
                        temp_score += char
                    elif temp_score:
                        break
                score += int(temp_score)
                print("score:", score)

                tag = False
            except Exception as e:
                print(e)
    with open("chatgpt_score.json", 'w', encoding='utf-8') as f:
        # 使用json.dump()函数将序列化后的JSON格式的数据写入到文件中
        json.dump({"average_score": score / len(os.listdir(path))}, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # asyncio.run(our_smi(r"C:\Users\A\Desktop\表格数据集"))
    # asyncio.run(qwen_smi(r"C:\Users\A\Desktop\表格数据集"))
    asyncio.run(chatgpt_smi(r"C:\Users\A\Desktop\表格数据集"))
