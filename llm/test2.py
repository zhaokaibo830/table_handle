import os
os.environ['OPENAI_API_KEY']="EMPTY"
os.environ['OPENAI_API_BASE']="http://124.70.207.36:7002/v1"
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
embedding = OpenAIEmbeddings(model="text-davinci-003")
loader = TextLoader("2.txt")
index = VectorstoreIndexCreator(embedding=embedding).from_loaders([loader])
llm = ChatOpenAI(model="qwen-14b-chat")
questions = [
 "Who is the speaker",
 "What did the president say about Ketanji Brown Jackson",
 "What are the threats to America",
 "Who are mentioned in the speech",
 "Who is the vice president",
 "How many projects were announced",
]
for query in questions:
 print("Query:", query)
 print("Answer:", index.query(query, llm=llm))