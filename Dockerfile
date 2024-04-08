FROM python:3.9

WORKDIR /aiogram-bot

ENV PYTHONPATH /aiogram-bot

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

#WORKDIR src

#CMD python3 main.py


