from langchain.chat_models import ChatOpenAI
import os
os.environ['OPENAI_API_KEY']="EMPTY"
os.environ['OPENAI_API_BASE']="http://124.70.213.108:7009/v1"
llm = ChatOpenAI(model="qwen1.5-14b-chat")
print(llm.predict("你好"))