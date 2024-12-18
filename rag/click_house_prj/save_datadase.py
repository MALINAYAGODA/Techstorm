from langchain_community.document_loaders import TextLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from yandex_chain import YandexLLM, YandexEmbeddings
import pandas as pd
import numpy as np
import time
import sys
sys.path.append("../KAZAN_BOT_2")

import pandas as pd
import clickhouse_connect
from tqdm import tqdm

YANDEX_FOLDER_ID = 'b1gtk869ka7gcnf3975l'
YANDEX_API_KEY = 'AQVN1JHtr7B7ujYaO5flAuI7fQ-cF-aIFRwukgDZ'
embeddings = YandexEmbeddings(folder_id=YANDEX_FOLDER_ID, api_key=YANDEX_API_KEY)

# Подключение к ClickHouse
client = clickhouse_connect.get_client(host='127.0.0.1', username='default', password='1234')

df = pd.read_csv("data_tatneft.csv")
for row in df.iterrows():
    start_time = time.time()
    id = row[0]
    link = row[1]["URL"]
    text = row[1]["TEXT"]

    document = Document(page_content=text)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = [doc.page_content for doc in text_splitter.split_documents([document])]
    text_embeddings = [np.array(embeddings.embed_query(text), dtype=np.float32) for text in texts]
    client.insert('ann_index_tatneft', list(zip([link]*len(texts), text_embeddings, texts)))
    print(f"Пакет #{id} сохранен", time.time() - start_time)
print("Данные успешно сохранены в ClickHouse.")

    