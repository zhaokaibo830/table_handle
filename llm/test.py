from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
import os
os.environ['OPENAI_API_KEY']="EMPTY"
os.environ['OPENAI_API_BASE']="http://124.70.207.36:7002/v1"
# load_dotenv()

# main_chain = (PromptTemplate(template="""{query}""",
#                              input_variables=["query"])
#               | ChatOpenAI(model="qwen-14b-chat", temperature=1))
llm = ChatOpenAI(model="qwen-14b-chat")
# print(main_chain.invoke({'query':'你好？'}).content)
print(llm.predict("你好"))