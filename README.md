# 部署注意事项
## 部署
### Dockerfile文件

```bash
FROM python:3.8.18

ENV OPENAI_API_KEY EMPTY
# 大模型的部署路径
ENV OPENAI_API_BASE http://124.70.213.108:7009/v1
# 大模型的名字
ENV MODEL_NAME qwen1.5-14b-chat

WORKDIR .

COPY table2text/ ./table2text/

COPY requirements.txt ./

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

RUN pyarmor gen -O code/ ./table2text/*

RUN rm -rf ./table2text

EXPOSE 8006

WORKDIR ./code

```

注意配置大模型所对应的环境变量和端口

如果不是容器化部署，则需要在run.py如下代码中配置环境变量和端口

![image-20240707152452016](imgs/1.png)



![image-20240707152632048](imgs/2.png)

## 路由

```
/api/table2text  #接收json
/api/table2text_excel #接收excel文件
/api/table2text_json_file #接收json文件
```