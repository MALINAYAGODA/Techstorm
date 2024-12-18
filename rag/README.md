# Rag_service
- В main.py запускаем сервер на FastAPI
- Файл creat_table запускаем только при создании таблицы для clickhouse
- Файл save_datadase.py сохраняет в clickhouse данные data_tatneft.csv
- Файл find_nearest_neighbors.py ищет вопрос в векторной базе данных
- Файл save_emb.py сохраняет новый документы в БД
- data_tatneft.csv - данные собранные о Tatneft
# ClickHouse
1) Скачан docker desktop + создана БД ClickHouse: https://www.youtube.com/watch?v=W22Dp3rGkis
2) При создании ClickHouse в консоли Ubuntu пишем: docker run --name clickhouse -p 8123:8123 -e CLICKHOUSE_ADMIN_PASSWORD=1234 -d bitnami/clickhouse:latest
# Шаги для запуска бота
1) Запустить докер 
2) Запустить creat_table.py
3) Запусать save_datadase.py
4) Запустить main.py
5) запустить бота tg_bot.py

Теперь ваш бот будет работать здесь: [t.me/ai_tatneft_clickhouse_bot](https://t.me/ai_tatneft_clickhouse_bot)