
# configuration for database, here we use clickhouse
# dbconf = {
#     "user": "default",
#     "password": "123456",
#     "server_host": "47.104.1.82",
#     "port": "8123",
#     "db": "default"
# }
# SQLALCHEMY_DATABASE_URI = 'clickhouse://{user}:{password}@{server_host}:{port}/{db}'.format(**dbconf)

# configuration for JSON Handling
JSON_AS_ASCII = False 
JSONIFY_MIMETYPE = "application/json;charset=utf-8"
JSON_SORT_KEYS = False

# configuration for flaskserver
FLASK_RUN_HOST = '0.0.0.0'
# FLASK_RUN_PORT = 6008
FLASK_RUN_PORT = 8810
USE_WSGI_SERVER = False


# configuration for LLM API address autdodl
# urls = {}
# urls['chatglm-6b'] = ["https://u107905-8bae-dbaa1c43.neimeng.seetacloud.com:6443"]


