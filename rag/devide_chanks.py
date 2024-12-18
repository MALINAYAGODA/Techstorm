from langchain_community.document_loaders import TextLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from yandex_chain import YandexLLM, YandexEmbeddings
import pandas as pd

YANDEX_FOLDER_ID = 'b1gtk869ka7gcnf3975l'
YANDEX_API_KEY = 'AQVN1JHtr7B7ujYaO5flAuI7fQ-cF-aIFRwukgDZ'
embeddings = YandexEmbeddings(folder_id=YANDEX_FOLDER_ID, api_key=YANDEX_API_KEY)

df = pd.read_csv("D:/atom_prj/kazan/db_data/data_tatneft.csv")
for row in df.iterrows():
    id = row[0]
    link = row[1]
    text = row[2]

    document = Document(page_content=text)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents([document])
    text_embeddings = [embeddings.embed_query(text.page_content) for text in texts]
    




# Преобразование текстов в эмбеддинги
text_embeddings = [embeddings.embed_query(text.page_content) for text in texts]
# Вывод эмбеддингов
for i, embedding in enumerate(text_embeddings):
    print(texts[i])
    print("----")
    print(f"Эмбеддинг для чанка {i+1}: {embedding}")
    print("<->"*7)