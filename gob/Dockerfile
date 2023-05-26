FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN apt-get update \
    && apt-get -y install libpq-dev gcc

RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "gob.wsgi:application", "--bind", "0:8000" ]

LABEL author='Kamanin Y.N.' version=1.0
