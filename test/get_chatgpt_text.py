import base64
import requests
import os

# OpenAI API Key
api_key = "sk-Mj4ShXvqWIAEexqoQfBqdwjAKvFeOcVGiiXn2heC3b9bukw4"
model_name = "gpt-4o"
url = "https://api.chatanywhere.com.cn/v1/chat/completions"


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_chatgpt_text(path):
    for i, table_path in enumerate(os.listdir(path)):
        if i != 0:
            continue
        # Path to your image
        image_path = os.path.join(path, table_path, "img.png")
        # Getting the base64 string
        base64_image = encode_image(image_path)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请用一段话详细的描述此图片"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }

        response = requests.post(url, headers=headers, json=payload)

        print(response.json())
        with open(os.path.join(path, table_path, "chatgpt_text.txt"), 'w') as file:
            # 写入内容到文件
            file.write(response.json()["choices"][0]["message"]["content"])

if __name__ == '__main__':
    get_chatgpt_text(r"C:\Users\A\Desktop\表格数据集")
