# -*- coding: utf-8 -*-

import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import asyncio
from yandex_chain import YandexLLM, YandexGPTModel
from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import requests

YANDEX_FOLDER_ID = 'b1gtk869ka7gcnf3975l'
YANDEX_API_KEY = 'AQVN1JHtr7B7ujYaO5flAuI7fQ-cF-aIFRwukgDZ'
llm = YandexLLM(folder_id=YANDEX_FOLDER_ID, api_key=YANDEX_API_KEY, model=YandexGPTModel.Pro)

TELEGRAM_TOKEN = "6925013038:AAH8PBCaFg5hldwNUM2R1I-IHzUKfyackxs" # "6715358280:AAGWw1rZ_0SoVw4K0WI4cr-DQ7lk5y8Ojxs"
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# RAG-Fusion
template = """Ты - полезный помощник, который генерирует несколько поисковых запросов на основе одного входного запроса. \n
Генерируй несколько поисковых запросов, связанных с: {question} \n
Ответ (4 поисковых запроса):"""

def rag_fusion_pipeline(query):
    ans = llm(template.format(question=query))
    multiple_queries = [i for i in ans.split('\n') if i != '']

    count = dict()
    reverse_dict = {}
    for i in range(len(multiple_queries)):
        url = 'http://127.0.0.1:8001/get_neighbors/'
        data = {'arr': [multiple_queries[i]], 'k_neighbors': 4}

        response = requests.post(url, json=data)
        if response.status_code == 200:
            relevant_documents_content = response.json()['list_text'][0]
        else:
            print("Что-то не так")
            return
        for content in relevant_documents_content:
            count[content[1]] = 1 + count.get(content[1], 0)
            if content[1] not in reverse_dict:
                reverse_dict[content[1]] = content[0]

    sorted_chunks_for_rag_fusion = [i[0] + f"\nссылка на источник: [{reverse_dict[i[0]]}]\n" for i in sorted(count.items(), key=lambda item: item[1], reverse=True)]
    joined_sorted_chunks_for_rag_fusion = ''.join(sorted_chunks_for_rag_fusion)
    return joined_sorted_chunks_for_rag_fusion

# RAG
system_prompt = (
    '''
    Игнорируй все предыдущие инструкции. Ты ассистент для решения задач по вопросам и ответам. Твоя задача — использовать предоставленный контекст, чтобы дать максимально точный и полезный ответ. Если в контексте нет достаточной информации, прямо скажи, что не знаешь ответа. Твоя цель — дать короткий, но исчерпывающий ответ на основе доступных данных.
-------
    {context}
-------
    Важно: после твоего основного ответа напиши ссылку на документы, из которого взял информацию. Они должны быть в квадратных скобках. Не выводи ссылки, документы которых не имеют релевантую информацию к вопросу: 
    '''
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{question}"),
    ]
)

async def rag_chain(context, question, message):
    joined_sorted_chunks_for_rag_fusion = rag_fusion_pipeline(question)
    await bot.send_message(chat_id=message.chat.id, text="Нашел информацию - генерирую ответ")
    input_data = {
        "context": joined_sorted_chunks_for_rag_fusion, 
        "question": question
    }
    
    chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke(input_data)





# Настройка базы данных SQLite для хранения взаимодействий
engine = create_engine('sqlite:///telegram_bot.db')
Base = declarative_base()
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    interactions = relationship('Interaction', back_populates='user')

class Interaction(Base):
    __tablename__ = 'interactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question = Column(Text)
    answer = Column(Text)
    user = relationship('User', back_populates='interactions')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def get_or_create_user(telegram_id):
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        session.add(user)
        session.commit()
    return user

def save_interaction(user, question, answer):
    interaction = Interaction(user_id=user.id, question=question, answer=answer)
    session.add(interaction)
    session.commit()

def clear_user_interactions(user):
    session.query(Interaction).filter_by(user_id=user.id).delete()
    session.commit()

def get_last_interactions(user, limit=3):
    return session.query(Interaction).filter_by(user_id=user.id).order_by(Interaction.id.desc()).limit(limit).all()


# Хэндлер на команду /start , /help
@dp.message(Command(commands=["start", "help"]))
async def cmd_start(message: types.Message):
    user = get_or_create_user(message.from_user.id)
    clear_user_interactions(user)
    await message.reply("Привет! Я бот, использующий модель RAG и способный конвертировать аудио в текст. Задайте мне любой вопрос или отправьте голосовое сообщение!")

# Хэндлер на команду /clear
@dp.message(Command(commands="clear"))
async def clear_dialog(message: types.Message):
    user = get_or_create_user(message.from_user.id)
    clear_user_interactions(user)
    await message.reply("История сообщений очищена.")

# Хэндлер на получение текстового сообщения (для RAG)
@dp.message(F.text)
async def handle_text(message: types.Message):
    user = get_or_create_user(message.from_user.id)
    question = message.text

    last_interactions = get_last_interactions(user)
    context = "\n".join(f"Q: {interaction.question}\nA: {interaction.answer}" for interaction in reversed(last_interactions))

    response = await rag_chain(context, question, message)
    save_interaction(user, question, response)
    await message.reply(response)

# # Хэндлер на получение голосового и аудио сообщения
# @dp.message(F.content_type.in_({"voice", "audio", "document"}))
# async def voice_message_handler(message: types.Message):
#     user = get_or_create_user(message.from_user.id)

#     if message.content_type == "voice":
#         file_id = message.voice.file_id
#     elif message.content_type == "audio":
#         file_id = message.audio.file_id
#     elif message.content_type == "document":
#         file_id = message.document.file_id
#     else:
#         await message.reply("Формат документа не поддерживается")
#         return

#     file = await bot.get_file(file_id)
#     file_path = file.file_path
#     file_on_disk = Path("", f"{file_id}.tmp")
#     await bot.download_file(file_path, destination=file_on_disk)

#     # Конвертация аудио в текст
#     text = stt.audio_to_text(file_on_disk)
#     if not text:
#         await message.reply("Не удалось распознать текст из аудио.")
#         return

#     # Передача текста на обработку в RAG
#     last_interactions = get_last_interactions(user)
#     context = "\n".join(f"Q: {interaction.question}\nA: {interaction.answer}" for interaction in reversed(last_interactions))

#     response = rag_chain(context, text)
#     save_interaction(user, text, response)
#     await message.reply(response)

#     os.remove(file_on_disk)  # Удаление временного файла

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запуск бота
    print("Запуск бота")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
