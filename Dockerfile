FROM python:3.7-slim-stretch

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y git python3-dev gcc \
    && rm -rf /var/lib/apt/lists/*
RUN pip --default-timeout=1000 install -r requirements.txt

EXPOSE 5000
COPY . /usr/app/
WORKDIR /usr/app/

CMD python styleapp.py
