FROM python:3.10-slim

WORKDIR /bot

RUN pip install aiogram

COPY . .

EXPOSE 3001

CMD ['python', 'main.py']

