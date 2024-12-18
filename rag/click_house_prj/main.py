import sys

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import clickhouse_connect
import typing as tp
from yandex_chain import YandexEmbeddings
import numpy as np
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

YANDEX_FOLDER_ID = 'b1gtk869ka7gcnf3975l'
YANDEX_API_KEY = 'AQVN1JHtr7B7ujYaO5flAuI7fQ-cF-aIFRwukgDZ'

client = clickhouse_connect.get_client(host='127.0.0.1', username='default', password='1234')
embeddings = YandexEmbeddings(folder_id=YANDEX_FOLDER_ID, api_key=YANDEX_API_KEY)
app = FastAPI()



class RequestModel(BaseModel):
    documnt_text: str
    link_text: list


class RequestModel_get(BaseModel):
    arr: list
    k_neighbors: int


class ResponseModel(BaseModel):
    response: str


class ResponseListModel(BaseModel):
    list_text: list


def find_top_set(responses, k):
    outputs = []
    answers = []
    for i in responses:
        if i[1] not in answers:
            answers.append(i[1])
            outputs.append(i)
            if len(outputs) == k:
                break
    return outputs


# encoder = Encoder("intfloat/multilingual-e5-small")  # download_model_e5-small-v2


@app.get("/")
async def home():
    return {"error": "Work"}


@app.post("/save/", response_model=ResponseModel)
async def encode(request_body: RequestModel):
    try:
        real_text = request_body.documnt_text
        link = request_body.link_text
        document = Document(page_content=real_text)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = [doc.page_content for doc in text_splitter.split_documents([document])]
        encoded_text = [np.array(embeddings.embed_query(text), dtype=np.float32) for text in texts]
        client.insert('ann_index_tatneft', list(zip([link]*len(texts), encoded_text, texts)))
        return {"response": "save"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/get_neighbors/", response_model=ResponseListModel)
async def give_neighbors(request_body: RequestModel_get):
    # try:
        real_text = request_body.arr
        k = request_body.k_neighbors
        encoded_text = [np.array(embeddings.embed_query(text), dtype=np.float32) for text in real_text]
        output_res = []
        # можно улучшить-ускорить
        for i in encoded_text:
            encoded_text_str = ", ".join(map(str, i))
            query = f"""
            SELECT
                Link,
                Text,
                score
            FROM
                (
                SELECT
                    Link,
                    Text,
                    L2Distance(embedding, [{encoded_text_str}]) AS score
                FROM ann_index_tatneft
                ORDER BY score ASC
                LIMIT {k}
                )
            """
            results = client.query(query).result_rows
            output_res.append(find_top_set(results, k))

        return {"list_text": output_res}  # output_res
    # except Exception as e:
    #    return {"error": [str(e)]}
# сделаю @app.post("/get_NN/", response_model=ResponseModel) для получения ближайшей к запросу строки
# uvicorn RAG_project_clickhouse.main:app --reload
if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8001)
# http://localhost:8001/docs - чтобы войти в пульт управление