import os
from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import asyncio
from langchain.chains import LLMChain
os.environ['OPENAI_API_KEY'] = "EMPTY"
os.environ['OPENAI_API_BASE'] = "http://124.70.213.108:7009/v1"
# os.environ['OPENAI_API_BASE'] = "http://10.8.0.6:7002/v1"
os.environ['MODEL_NAME'] = "qwen1.5-14b-chat"

async def test():
    polish_prompt_ch = """
                {text}
                变换以上内容的描述方式。
                """


    p_prompt = PromptTemplate(input_variables=["text"], template=polish_prompt_ch)

    llm = ChatOpenAI(model=os.environ['MODEL_NAME'])
    polish_chain = p_prompt | llm | StrOutputParser()
    caption="""项目 是1月。 径流量(108m3）的三峡蓄水前 是114.3。 径流量(108m3）的2003-2019年 是159.8。 径流量(108m3）的2019年 是227.3。 径流量(108m3）的2020年 是220.6。 径流量(108m3）的距平百分率1 是0.93。 径流量(108m3）的距平百分率2 
是0.38。 径流量(108m3）的距平百分率3 是-0.03。 输沙量(104t)的三峡蓄水前 是55.6。 输沙量(104t)的2003-2019年 是5.2。 输沙量(104t)的2019年 是4.55。 输沙量(104t)的2020年 是5.7。 输沙量(104t)的距平百分率1 是-0.9。 输沙量(104t)的距平 
百分率2 是0.1。 输沙量(104t)的距平百分率3 是0.25。 项目 是2月。 径流量(108m3）的三峡蓄水前 是93.65。 径流量(108m3）的2003-2019年 是140.7。 径流量(108m3）的2019年 是171.5。 径流量(108m3）的2020年 是184.4。 径流量(108m3）的距平百 
分率1 是0.97。 径流量(108m3）的距平百分率2 是0.31。 径流量(108m3）的距平百分率3 是0.08。 输沙量(104t)的三峡蓄水前 是29.3。 输沙量(104t)的2003-2019年 是4.2。 输沙量(104t)的2019年 是3.73。 输沙量(104t)的2020年 是6.94。 输沙量(104t
)的距平百分率1 是-0.76。 输沙量(104t)的距平百分率2 是0.65。 输沙量(104t)的距平百分率3 是0.86。 项目 是3月。 径流量(108m3）的三峡蓄水前 是115.6。 径流量(108m3）的2003-2019年 是170.5。 径流量(108m3）的2019年 是229.9。 径流量(108m3
）的2020年 是263.8。 径流量(108m3）的距平百分率1 是1.28。 径流量(108m3）的距平百分率2 是0.55。 径流量(108m3）的距平百分率3 是0.15。 输沙量(104t)的三峡蓄水前 是81.2。 输沙量(104t)的2003-2019年 是5.51。 输沙量(104t)的2019年 是6.94
。 输沙量(104t)的2020年 是5.44。 输沙量(104t)的距平百分率1 是-0.93。 输沙量(104t)的距平百分率2 是-0.01。 输沙量(104t)的距平百分率3 是-0.22。 项目 是4月。 径流量(108m3）的三峡蓄水前 是171.3。 径流量(108m3）的2003-2019年 是216.7。
 径流量(108m3）的2019年 是273.2。 径流量(108m3）的2020年 是272.9。 径流量(108m3）的距平百分率1 是0.59。 径流量(108m3）的距平百分率2 是0.26。 径流量(108m3）的距平百分率3 是0。 输沙量(104t)的三峡蓄水前 是449。 输沙量(104t)的2003-2
019年 是9.42。 输沙量(104t)的2019年 是6.38。 输沙量(104t)的2020年 是6.74。 输沙量(104t)的距平百分率1 是-0.98。 输沙量(104t)的距平百分率2 是-0.28。 输沙量(104t)的距平百分率3 是0.06。 项目 是5月。 径流量(108m3）的三峡蓄水前 是310.
4。 径流量(108m3）的2003-2019年 是349.3。 径流量(108m3）的2019年 是439.3。 径流量(108m3）的2020年 是285.2。 径流量(108m3）的距平百分率1 是-0.08。 径流量(108m3）的距平百分率2 是-0.18。 径流量(108m3）的距平百分率3 是-0.35。 输沙量
(104t)的三峡蓄水前 是2110。 输沙量(104t)的2003-2019年 是32.4。 输沙量(104t)的2019年 是23.3。 输沙量(104t)的2020年 是8.04。 输沙量(104t)的距平百分率1 是-1。 输沙量(104t)的距平百分率2 是-0.75。 输沙量(104t)的距平百分率3 是-0.65。 
项目 是6月。 径流量(108m3）的三峡蓄水前 是466.5。 径流量(108m3）的2003-2019年 是450.4。 径流量(108m3）的2019年 是514.8。 径流量(108m3）的2020年 是548.7。 径流量(108m3）的距平百分率1 是0.18。 径流量(108m3）的距平百分率2 是0.22。 
径流量(108m3）的距平百分率3 是0.07。 输沙量(104t)的三峡蓄水前 是5230。 输沙量(104t)的2003-2019年 是116。 输沙量(104t)的2019年 是61.9。 输沙量(104t)的2020年 是91.5。 输沙量(104t)的距平百分率1 是-0.98。 输沙量(104t)的距平百分率2  
是-0.21。 输沙量(104t)的距平百分率3 是0.48。 项目 是7月。 径流量(108m3）的三峡蓄水前 是804。 径流量(108m3）的2003-2019年 是722.7。 径流量(108m3）的2019年 是669.9。 径流量(108m3）的2020年 是921.9。 径流量(108m3）的距平百分率1 是0
.15。 径流量(108m3）的距平百分率2 是0.28。 径流量(108m3）的距平百分率3 是0.38。 输沙量(104t)的三峡蓄水前 是15500。 输沙量(104t)的2003-2019年 是1400。 输沙量(104t)的2019年 是200。 输沙量(104t)的2020年 是779。 输沙量(104t)的距平百
分率1 是-0.95。 输沙量(104t)的距平百分率2 是-0.44。 输沙量(104t)的距平百分率3 是2.9。 项目 是8月。 径流量(108m3）的三峡蓄水前 是734.1。 径流量(108m3）的2003-2019年 是624.5。 径流量(108m3）的2019年 是671.5。 径流量(108m3）的2020 
年 是1064。 径流量(108m3）的距平百分率1 是0.45。 径流量(108m3）的距平百分率2 是0.7。 径流量(108m3）的距平百分率3 是0.58。 输沙量(104t)的三峡蓄水前 是12400。 输沙量(104t)的2003-2019年 是1020。 输沙量(104t)的2019年 是482。 输沙量(
104t)的2020年 是3320。 输沙量(104t)的距平百分率1 是-0.73。 输沙量(104t)的距平百分率2 是2.25。 输沙量(104t)的距平百分率3 是5.89。 项目 是9月。 径流量(108m3）的三峡蓄水前 是657。 径流量(108m3）的2003-2019年 是525.1。 径流量(108m3 
）的2019年 是410.3。 径流量(108m3）的2020年 是678.1。 径流量(108m3）的距平百分率1 是0.03。 径流量(108m3）的距平百分率2 是0.29。 径流量(108m3）的距平百分率3 是0.65。 输沙量(104t)的三峡蓄水前 是8630。 输沙量(104t)的2003-2019年 是7
45。 输沙量(104t)的2019年 是45.9。 输沙量(104t)的2020年 是425。 输沙量(104t)的距平百分率1 是-0.95。 输沙量(104t)的距平百分率2 是-0.43。 输沙量(104t)的距平百分率3 是8.26。 项目 是10月。 径流量(108m3）的三峡蓄水前 是483.2。 径流量
(108m3）的2003-2019年 是347。 径流量(108m3）的2019年 是386.5。 径流量(108m3）的2020年 是509.2。 径流量(108m3）的距平百分率1 是0.05。 径流量(108m3）的距平百分率2 是0.47。 径流量(108m3）的距平百分率3 是0.32。 输沙量(104t)的三峡蓄 
水前 是3450。 输沙量(104t)的2003-2019年 是66.5。 输沙量(104t)的2019年 是29.7。 """
    polish_caption = await polish_chain.ainvoke({"text": caption})
    print(polish_caption)
if __name__ == '__main__':
    asyncio.run(test())

