# -*- coding:utf-8 -*-
import shutil
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import TextLoader, UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
import os
import json
from langchain.embeddings import OpenAIEmbeddings

os.environ['OPENAI_API_KEY']="EMPTY"
os.environ['OPENAI_API_BASE']="http://124.70.207.36:7002/v1"

def init_knowledge_vector_store():
    embedding = OpenAIEmbeddings(model="text-davinci-003")
    # embedding = HuggingFaceEmbeddings(model_name=r'/root/reportQA/huggingface/infgrad/stella-large-zh')
    print('------正在嵌入txt文档，生成知识向量库-------\n')
    txt_faiss_map = {}
    index_total_num = 1
    txt_path = r'/root/report_qa_new/test3_400docs_v3/plain_text'
    vs_path = r'/root/report_qa_new/test3_400docs_v3/pregenerated_faiss'
    for i, dir_name in enumerate(os.listdir(txt_path)):
        count = 1
        if True:
            for file_name in os.listdir(os.path.join(txt_path, dir_name)):
                print(f"正在嵌入{dir_name}文件夹下的第{count}个文件：")
                count += 1

                faiss_name = str(index_total_num) + '_txt'
                txt_faiss_map[file_name] = faiss_name

                path = txt_path + "/" + dir_name + "/" + file_name
                loader = TextLoader(path, autodetect_encoding=True)
                documents = loader.load()
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=100)
                texts = text_splitter.split_documents(documents)
                faiss_index = FAISS.from_documents(texts, embedding)
                if dir_name == "钻井地质设计报告":
                    faiss_index.save_local(folder_path=vs_path + '/' + 'zuanjing',  index_name=faiss_name)
                elif dir_name == "油田开发年报":
                    faiss_index.save_local(folder_path=vs_path + '/' + 'youtian',  index_name=faiss_name)
                elif dir_name == "气田开发年报":
                    faiss_index.save_local(folder_path=vs_path + '/' + 'qitian',  index_name=faiss_name)
                index_total_num += 1



    with open(r'/root/report_qa_new/test3_400docs_v3/' + 'txt_faiss_map.json', 'w', encoding='utf-8', ) as f:
        json.dump(txt_faiss_map, f, ensure_ascii=False)


def init_knowledge_vector_store_pdf():
    embedding = OpenAIEmbeddings(model="text-davinci-003")
    # embedding = HuggingFaceEmbeddings(model_name=r'D:/学校/2.项目/4.长庆报告问答-智能机器人微件/DocumentQA/LocalModels/infgrad/stella-large-zh')
    print('------正在嵌入pdf文档，生成知识向量库-------\n')
    pdf_faiss_map = {}
    index_total_num = 1

    pdf_path = r'/root/report_qa_new/test3_400docs_v3/PDF'
    vs_path = r'/root/report_qa_new/test3_400docs_v3/pregenerated_faiss'
    for i, dir_name in enumerate(os.listdir(pdf_path)):
        count = 1
        if True:
            for file_name in os.listdir(os.path.join(pdf_path, dir_name)):
                print(f"正在嵌入{dir_name}文件夹下的第{count}个文件：")
                count += 1

                faiss_name = str(index_total_num) + '_pdf'
                pdf_faiss_map[file_name] = faiss_name

                path = pdf_path + "/" + dir_name + "/" + file_name
                loader = UnstructuredPDFLoader(path, mode="elements")
                print("开始生成documents")
                documents = loader.load()
                print("开始生成faiss_index")
                faiss_index = FAISS.from_documents(documents, embedding)
                if dir_name == "钻井地质设计报告":
                    faiss_index.save_local(folder_path=vs_path + '/' + 'zuanjing', index_name=faiss_name)
                elif dir_name == "油田开发年报":
                    faiss_index.save_local(folder_path=vs_path + '/' + 'youtian', index_name=faiss_name)
                elif dir_name == "气田开发年报":
                    faiss_index.save_local(folder_path=vs_path + '/' + 'qitian', index_name=faiss_name)
                index_total_num += 1

    with open(r'/root/report_qa_new/test3_400docs_v3/' + 'pdf_faiss_map.json', 'w', encoding='utf-8', ) as f:
        json.dump(pdf_faiss_map, f, ensure_ascii=False)




def create_txt_map():
    txt_faiss_map = {}
    index_total_num = 1
    txt_path = r'/root/report_qa_new/test3_400docs_v3/plain_text'
    for i, dir_name in enumerate(os.listdir(txt_path)):
        for file_name in os.listdir(os.path.join(txt_path, dir_name)):
            faiss_name = str(index_total_num) + '_txt'
            txt_faiss_map[file_name] = faiss_name
            index_total_num +=1
    with open(r'/root/report_qa_new/test3_400docs_v3/' + 'txt_faiss_map.json', 'w', encoding='utf-8', ) as f:
        json.dump(txt_faiss_map, f, ensure_ascii=False)



if __name__ == '__main__':
    init_knowledge_vector_store()
    init_knowledge_vector_store_pdf()
    #create_txt_map()