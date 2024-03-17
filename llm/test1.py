import os
import random
os.environ['OPENAI_API_KEY']="EMPTY"
os.environ['OPENAI_API_BASE']="http://124.70.207.36:7002/v1"
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders import TextLoader, UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
prompt_template = "{adjective}"
prompt = PromptTemplate(input_variables=["adjective"], template=prompt_template)
chain = LLMChain(llm=ChatOpenAI(model="qwen1.5-14b-chat", temperature=random.random()/2), prompt=prompt)

# embeddings = OpenAIEmbeddings(model="text-davinci-003",request_timeout=120)
result=chain.run(adjective='俄罗斯')
print(result)
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
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=100)
# texts = text_splitter.split_documents(documents)
# faiss_index = FAISS.from_documents(texts, embeddings)
# temp=llm.predict("中国")

# print(temp)
# print(faiss_index)