
FROM python:3.11-slim-buster
LABEL authors="Dominik"

WORKDIR /bot

COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY entrypoint.sh .

COPY bot.py .
COPY pois.py .
COPY bot_timer.py .
COPY lat_long.py .
COPY data/poi.csv /bot/origin/
COPY data/maps.csv /bot/origin/
COPY data/test.yml /bot/origin/
COPY data/1bezirk.yml /bot/origin/
COPY data/secrets.json.sample /bot/origin/secrets.json

ENTRYPOINT ["/bin/bash", "/bot/entrypoint.sh"]
CMD ["python3", "bot.py"]