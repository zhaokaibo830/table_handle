from langchain.llms.base import LLM
from typing import List, Optional
import requests
import json
from fastapi import status, HTTPException

class Vicuna(LLM):
    max_token: int = 2048
    temperature: float = 0.8
    top_p = 0.9
    tokenizer: object = None
    model: object = None
    history_len: int = 1024
    url_llm: str = ''

    def __init__(self, url):
        super().__init__()
        self.url_llm = url+'llm'

    @property
    def _llm_type(self) -> str:
        return "Vicuna"

    def llm(self, prompt: str):
        try:
            content1 = json.dumps({"text": prompt})
            response = requests.request("POST", self.url_llm, data=content1)
            res = json.loads(response.text, strict=False)
            return res['response']
        except:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="服务器已关闭，请联系服务器管理员")

    def _call(self, prompt: str, stop: Optional[List[str]] = None):
        response = self.llm(prompt)
        return response