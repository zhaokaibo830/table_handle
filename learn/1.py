import uvicorn
from fastapi import FastAPI, File, UploadFile
import json
app = FastAPI()


@app.post("/table/tabletotext")
def tabletotext(file: UploadFile = File(...)):
    # table_dict = file.file.read()
    f = open("11.json", 'wb')
    data = file.file.read()
    f.write(data)
    f.close()
    with open("11.json", "r", encoding='utf-8') as f:
        table_dict = json.load(f)
    return table_dict["trs"]


if __name__ == "__main__":
    uvicorn.run(port=8000, app=app, host="0.0.0.0")
