FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get upgrade -y && \
    apt-get update -y && \
    apt-get install graphviz -y

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
