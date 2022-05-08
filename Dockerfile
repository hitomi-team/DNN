FROM python:3.9.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /dnn-bot
WORKDIR /dnn-bot

COPY requirements.txt /dnn-bot
RUN pip install -r requirements.txt

COPY . /dnn-bot

