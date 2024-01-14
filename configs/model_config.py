import os
# 服务器链接集合
LLM_URLS = ["http://region-3.seetacloud.com:31536/",
            "http://region-31.seetacloud.com:49144/",
            "https://u147750-8cae-68e09ba1.neimeng.seetacloud.com:6443/",
            "https://u167387-8cae-33af11f2.neimeng.seetacloud.com:6443/",
            "https://u147750-a9ae-fcc8aa27.neimeng.seetacloud.com:6443/",
            "https://u147750-92ae-0299e063.neimeng.seetacloud.com:6443/",
            "https://u147750-b6ae-2bf49303.neimeng.seetacloud.com:6443/",
            "https://u147750-8fae-be4d7f86.neimeng.seetacloud.com:6443/",
            "https://u147750-b6ae-0a0938b6.neimeng.seetacloud.com:6443/",
            "http://region-31.seetacloud.com:24557/"]

# LLM input history length
LLM_HISTORY_LEN = 3

NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nltk_data")