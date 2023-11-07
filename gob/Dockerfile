FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN apt-get update && pip install --upgrade wheel


RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY . .

LABEL author='Kamanin Y.N.' version=2.0
