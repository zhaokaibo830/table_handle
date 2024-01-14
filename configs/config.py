
# configuration for flaskserver
FastAPI_RUN_HOST = '0.0.0.0'
FastAPI_RUN_PORT = 8810
USE_WSGI_SERVER = False


# homepage data query time mock
USE_MOCK_TIME = True
MINUS_DAYS_FROM_TODAY = 3

value_map = {'否': 0.001, '可能': 1, '是': 20}
score=20
score_threshold=20
n_generate_sample=3