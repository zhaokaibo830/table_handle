from configs.model_config import LLM_URLS
import requests

class Available_url():
    def __init__(self):
        for url in LLM_URLS:
            try:
                response = requests.request("GET", url)
                if response.status_code != 200: continue
                break
            except:
                continue
        self.url = url


if __name__ == '__main__':
    print(Available_url().url)