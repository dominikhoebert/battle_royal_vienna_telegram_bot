
FROM python:3.11-slim-buster
LABEL authors="Dominik"

WORKDIR /bot

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY *.py ./
RUN mkdir -p /bot/data/
COPY data/poi.csv /bot/data/
COPY data/maps.csv /bot/data/

ENTRYPOINT ["python3", "bot.py"]