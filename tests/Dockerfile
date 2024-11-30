FROM --platform=linux/amd64 python:3.10.2-buster

WORKDIR /code

RUN groupadd -r web && useradd -r -g web web

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/code

RUN pip install --upgrade pip

ENV TZ=Europe/Moscow
RUN apt install tzdata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Копирование и установка зависимостей прокета
COPY ./tests/functional/requirements.txt /code/tests/functional/requirements.txt
RUN pip install -r /code/tests/functional/requirements.txt

# Копирование эндрипоинта и дать права на выполнения
COPY ./tests/entrypoint.sh /web/entrypoint.sh
RUN chmod +x /web/entrypoint.sh

# Копирование проекта
COPY ./tests /code/tests

USER web

ENTRYPOINT ["/web/entrypoint.sh"]