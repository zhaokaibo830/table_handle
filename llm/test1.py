import os
import random

os.environ['OPENAI_API_KEY'] = "EMPTY"
os.environ['OPENAI_API_BASE'] = "http://124.70.207.36:7002/v1"
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders import TextLoader, UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.docstore.document import Document

prompt_template = "{adjective}"
prompt = PromptTemplate(input_variables=["adjective"], template=prompt_template)
chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat", temperature=random.random() / 2), prompt=prompt)

embeddings = OpenAIEmbeddings(model="text-davinci-003", request_timeout=120)

input="""
["行政区/县",
"岳麓区",
"街道",
"芙蓉街道".
"学校信息",
"学校名称",
"明峰中学",
"教学楼",
"北区5A",
"学年",
"2023-2026",
"入学日期",
"2023年9月日"]
以上列表是一个表格的全部内容，其中每一个元素对应表格的一个单元格内容，请根据语义信息找出其中可能是表头的单元格,。请一步一步进行分析，要注意每一个元素内容对应一个单元格，所以不能对每一行的内容进行拆分理解。
"""
result = chain.run(adjective=input)

print(result)
print("-----------------------------------------------")

# loader = TextLoader("state_of_the_union.txt")
# index =VectorstoreIndexCreator(embedding=embedding).from_loaders([loader])
# llm = ChatOpenAI(model="qwen-14b-chat")
# questions = [
#  "Who is the speaker",
#  "What did the president say about Ketanji Brown Jackson",
#  "What are the threats to America",
#  "Who are mentioned in the speech",
#  "Who is the vice president",
#  "How many projects were announced",
# ]
# for query in questions:
#     print("Query:", query)
#     print("Answer:", index.query(query, llm=llm))
# def embedding():
#     global embeddings
#     doc_result = embeddings.embed_documents(
#         [
#             "Hi there!",
#             "Oh, hello!",
#             "What's your name?",
#             "My friends call me World",
#             "Hello World!"
#         ]
#     );
#     print(doc_result)
#
# embedding()
# loader = TextLoader("1.txt", autodetect_encoding=True)
# documents = loader.load()
# print(type(documents))
# print(documents)
metadata1 = {"source_sub_table_index": 3}
document1 = Document(page_content="苏里格气田第三天然气处理厂CL3-W1-JC1地下水监测井地质设计", metadata=metadata1)
metadata2 = {"source_sub_table_index": 5}
document2 = Document(page_content="苏里格气田第三天然气处理厂", metadata=metadata2)
documents = [document1, document2]
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=20, chunk_overlap=0)
# texts = text_splitter.split_documents(documents)
faiss_index = FAISS.from_documents(documents, embeddings)
# temp=llm.predict("中国")
Q = "地下水"
docs = faiss_index.similarity_search(Q, k=1)

# print(temp)
print(docs)
