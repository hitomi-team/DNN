FROM python:3.9.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /dnn-bot
WORKDIR /dnn-bot
COPY . /dnn-bot/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
