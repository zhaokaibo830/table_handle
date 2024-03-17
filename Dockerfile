FROM continuumio/miniconda3
WORKDIR .

COPY table_handle/ ./table_handle/

COPY requirements.txt ./

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

RUN pyarmor gen -O code/ ./table_handle/*

COPY table_handle/key.json ./code/

RUN rm -rf ./table_handle

EXPOSE 8000

WORKDIR ./code

#ENTRYPOINT ["python","run.py","-OPENAI_API_KEY","-OPENAI_API_BASE"]


