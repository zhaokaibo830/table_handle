# -*- coding:utf-8 -*-
import traceback
from flask import Flask, jsonify, request, make_response
from gevent import pywsgi
from funcs.load_vectorstore import start
from funcs.load_vectorstore import start_table
import json
import config


app = Flask(__name__)
app.config.from_object(config)

all_faiss_index_table = start_table()
all_faiss_index, llm = start()



# print(all_faiss_index)

@app.route('/api/v2/report_qa', methods=['post'])
def report_qa():
    get_data = request.get_data()
    print(type(get_data))
    print(get_data)
    get_data = json.loads(get_data)
    query = get_data['question']
    print("question:", query)

    out = {}
    out['error'] = ""
    out['queryStatus'] = 1
    out['data'] = {}

    out['data']['image'] = ""
    out['data']['page'] = []
    out['data']["file"] = ""
    out['data']['file_path'] = ""

    try:
        if "#" not in query:
            out['data']["answer"] = "问题格式不正确，#之前是问题类别，现在可以提问的类别有气田开发年报、油田开发年报和钻井地质设计报告，#后面是具体问题"
            raise ValueError(
                "问题格式不正确，#之前是问题类别，现在可以提问的类别有气田开发年报、油田开发年报和钻井地质设计报告，#后面是具体问题")
        query_class, query_content = query.split("#", 1)[0], query.split("#", 1)[1]
        print("query_content:", query_content)
        if query_class == "油田开发年报":
            if "年" not in query_content:
                out['data']["answer"] = "对年报提问您应该明确是哪一年。例如2022年......."
                raise ValueError("对年报提问您应该明确是哪一年。例如2022年.......")
            if query_content.split('年', 1)[0] + '年' not in all_faiss_index[query_class]:
                out['data']["answer"] = "知识库中没有您所提问年份的油田年报"
                raise ValueError("知识库中没有您所提问年份的油田年报")
            faiss_index, result_source = all_faiss_index["油田开发年报"][query_content.split('年', 1)[0] + '年']
            faiss_index_table, result_source_table = all_faiss_index_table["油田开发年报"][
                query_content.split('年', 1)[0] + '年']
            Q = query_content.split('年', 1)[1]

        elif query_class == "气田开发年报":
            if "年" not in query_content:
                out['data']["answer"] = "对年报提问您应该明确是哪一年。例如2022年......."
                raise ValueError("对年报提问您应该明确是哪一年。例如2022年.......")
            if query_content.split('年', 1)[0] + '年' not in all_faiss_index[query_class]:
                out['data']["answer"] = "知识库中没有您所提问年份的气田年报"
                raise ValueError("知识库中没有您所提问年份的气田年报")
            faiss_index, result_source = all_faiss_index["气田开发年报"][query_content.split('年', 1)[0] + '年']
            faiss_index_table, result_source_table = all_faiss_index_table["气田开发年报"][
                query_content.split('年', 1)[0] + '年']
            Q = query_content.split('年', 1)[1]

        elif query_class == "钻井地质设计报告":
            if "井" not in query_content:
                out['data']["answer"] = "对钻井地质报告的提问您应该明确对哪一口井提问，例如乾11-34井......。"
                raise ValueError("对钻井地质报告的提问您应该明确对哪一口井提问，例如乾11-34井......。")
            if query_content.split('井', 1)[0] + '井' not in all_faiss_index[query_class]:
                out['data']["answer"] = "知识库中没有您所提问的相关井号。"
                raise ValueError("知识库中没有您所提问的相关井号。")
            faiss_index, result_source = all_faiss_index["钻井地质设计报告"][query_content.split('井', 1)[0] + '井']
            faiss_index_table, result_source_table = all_faiss_index_table["钻井地质设计报告"][
                query_content.split('井', 1)[0] + '井']
            Q = query_content.split('井', 1)[1]
        else:
            out['data']["answer"] = "您提问的类别目前不存在，现在可以提问的类别有气田开发年报、油田开发年报和钻井地质设计报告。"
            raise ValueError("您提问的类别目前不存在，现在可以提问的类别有气田开发年报、油田开发年报和钻井地质设计报告。")

        print("问题：", Q)
        docs = faiss_index.similarity_search(Q, k=2)
        docs_table = {}
        for i in range(len(docs)):
            docs_table[i] = faiss_index_table.similarity_search(docs[i].page_content, k=1)
            out['data']['page'].append(docs_table[i][0].metadata["page_number"])
        out['data']['page'] = list(set(out['data']['page']))

        text = ""
        for doc in docs:
            text += doc.page_content
        print("text:", text)
        question = "\n请根据给定的信息帮我回答下面的问题。\n" + Q
        output = llm.predict(text + question)

        print("output长度", len(output))

        out['data']["answer"] = output

        out['data']["file"] = result_source.replace("[描述后]", "")

        out['data']['file_path'] = '/' + query_class + '/' + out['data']['file'] + '.pdf'

        out['queryStatus'] = 0

        print("output内容：", output)

    except Exception as e:
        out['error'] = traceback.format_exc()
        out['data']["answer"] = "大模型服务已关闭，结果仅供测试，请联系管理员。"

        out['data']["file"] = "2021年气田开发年报"

        out['data']['file_path'] = '/' + "气田开发年报" + '/' + out['data']['file'] + '.pdf'
        out['data']['page'] = [4, 5]

        out['queryStatus'] = 0

        print(e)
    return jsonify(out)


if __name__ == '__main__':

    if config.USE_WSGI_SERVER:
        server = pywsgi.WSGIServer((config.FLASK_RUN_HOST, config.FLASK_RUN_PORT), app)
    else:
        app.run(debug=True, host=config.FLASK_RUN_HOST, port=config.FLASK_RUN_PORT)
    # server = pywsgi.WSGIServer(('127.0.0.1',8810),app)
    # server.serve_forever()
