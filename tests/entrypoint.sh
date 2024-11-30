#!/bin/bash

echo "Контейнер стартует"

echo "Жду подключения к Redis..."
python3 /code/tests/functional/utils/wait_for_redis.py
echo "Redis успешно запущен!"

echo "Жду подключения к Elasticsearch..."
python3 /code/tests/functional/utils/wait_for_elastic.py
echo "Elasticsearch успешно запущен!"
echo "Зачистка документов Elasticsearch..."
python3 /code/tests/functional/utils/delete_data_es.py

echo "-------Запуск тестов-------"
# pytest /code/tests/functional/src
pytest -v -s 
