FROM python:3.8.18

#RUN conda create -n new_env_name python=3.8.18
#
#RUN echo "conda activate new_env_name" >> ~/.bashrc
#
#SHELL ["/bin/bash", "--login", "-c"]
#
#RUN conda activate new_env_name &&
# Set environment variables
ENV OPENAI_API_KEY EMPTY
# 大模型的部署路径
ENV OPENAI_API_BASE http://124.70.207.36:7002/v1
# 大模型的名字
ENV MODEL_NAME qwen1.5-14b-chat

WORKDIR .

COPY table2text/ ./table2text/

COPY requirements.txt ./

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

RUN pyarmor gen -O code/ ./table2text/*

RUN rm -rf ./table2text

EXPOSE 8005

WORKDIR ./code

#ENTRYPOINT ["python","run.py","-OPENAI_API_KEY","-OPENAI_API_BASE"]
