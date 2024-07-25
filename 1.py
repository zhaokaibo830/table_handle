import os
import time

import requests
from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import asyncio
from langchain.chains import LLMChain
os.environ['OPENAI_API_KEY'] = "sk-Mj4ShXvqWIAEexqoQfBqdwjAKvFeOcVGiiXn2heC3b9bukw4"
os.environ['OPENAI_API_BASE'] = "https://api.chatanywhere.com.cn/v1"
# os.environ['OPENAI_API_BASE'] = "http://10.8.0.6:7002/v1"
os.environ['MODEL_NAME'] = "gpt-3.5-turbo"

async def test():
    polish_prompt_ch = """
                {text}
                变换以上内容的描述方式。
                """


    p_prompt = PromptTemplate(input_variables=["text"], template=polish_prompt_ch)

    llm = ChatOpenAI(model=os.environ['MODEL_NAME'])
    polish_chain = p_prompt | llm | StrOutputParser()
#     caption="""项目 是1月。 径流量(108m3）的三峡蓄水前 是114.3。 径流量(108m3）的2003-2019年 是159.8。 径流量(108m3）的2019年 是227.3。 径流量(108m3）的2020年 是220.6。 径流量(108m3）的距平百分率1 是0.93。 径流量(108m3）的距平百分率2
# 是0.38。 径流量(108m3）的距平百分率3 是-0.03。 输沙量(104t)的三峡蓄水前 是55.6。 输沙量(104t)的2003-2019年 是5.2。 输沙量(104t)的2019年 是4.55。 输沙量(104t)的2020年 是5.7。 输沙量(104t)的距平百分率1 是-0.9。 输沙量(104t)的距平
# 百分率2 是0.1。 输沙量(104t)的距平百分率3 是0.25。 项目 是2月。 径流量(108m3）的三峡蓄水前 是93.65。 径流量(108m3）的2003-2019年 是140.7。 径流量(108m3）的2019年 是171.5。 径流量(108m3）的2020年 是184.4。 径流量(108m3）的距平百
# 分率1 是0.97。 径流量(108m3）的距平百分率2 是0.31。 径流量(108m3）的距平百分率3 是0.08。 输沙量(104t)的三峡蓄水前 是29.3。 输沙量(104t)的2003-2019年 是4.2。 输沙量(104t)的2019年 是3.73。 输沙量(104t)的2020年 是6.94。 输沙量(104t
# )的距平百分率1 是-0.76。 输沙量(104t)的距平百分率2 是0.65。 输沙量(104t)的距平百分率3 是0.86。 项目 是3月。 径流量(108m3）的三峡蓄水前 是115.6。 径流量(108m3）的2003-2019年 是170.5。 径流量(108m3）的2019年 是229.9。 径流量(108m3
# ）的2020年 是263.8。 径流量(108m3）的距平百分率1 是1.28。 径流量(108m3）的距平百分率2 是0.55。 径流量(108m3）的距平百分率3 是0.15。 输沙量(104t)的三峡蓄水前 是81.2。 输沙量(104t)的2003-2019年 是5.51。 输沙量(104t)的2019年 是6.94
# 。 输沙量(104t)的2020年 是5.44。 输沙量(104t)的距平百分率1 是-0.93。 输沙量(104t)的距平百分率2 是-0.01。 输沙量(104t)的距平百分率3 是-0.22。 项目 是4月。 径流量(108m3）的三峡蓄水前 是171.3。 径流量(108m3）的2003-2019年 是216.7。
#  径流量(108m3）的2019年 是273.2。 径流量(108m3）的2020年 是272.9。 径流量(108m3）的距平百分率1 是0.59。 径流量(108m3）的距平百分率2 是0.26。 径流量(108m3）的距平百分率3 是0。 输沙量(104t)的三峡蓄水前 是449。 输沙量(104t)的2003-2
# 019年 是9.42。 输沙量(104t)的2019年 是6.38。 输沙量(104t)的2020年 是6.74。 输沙量(104t)的距平百分率1 是-0.98。 输沙量(104t)的距平百分率2 是-0.28。 输沙量(104t)的距平百分率3 是0.06。 项目 是5月。 径流量(108m3）的三峡蓄水前 是310.
# 4。 径流量(108m3）的2003-2019年 是349.3。 """
    caption="你好"
    polish_caption = await polish_chain.ainvoke({"text": caption})
    print(polish_caption)
if __name__ == '__main__':
    asyncio.run(test())
