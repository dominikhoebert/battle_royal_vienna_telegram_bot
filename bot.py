import json
import telebot
from loguru import logger
import csv
import random

logger.add('logs/logs.log', format="{time} {level} {message}", level="INFO", rotation="01:00")

map_level = 4
current_map_level = 1

timer = []


def read_secrets():
    with open('secrets.json') as f:
        return json.load(f)['bot_token']


def read_poi():
    pois = {}
    for i in range(1, map_level + 1):
        pois[i] = []
    reader = csv.DictReader(open('data/poi.csv', 'r', encoding='utf-8'))
    for row in reader:
        try:
            row_map_level = int(row['map'])
        except ValueError:
            continue
        for i in range(1, row_map_level + 1):
            pois[i].append(row)
    return pois


pois = read_poi()
bot = telebot.TeleBot(read_secrets())
logger.info('Bot started')


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Available commands: /config, /poi, /respawn")


@bot.message_handler(commands=['config', 'm'])
def countdown(message):
    global current_map_level
    try:
        if len(message.text.split(' ')) < 2:
            bot.reply_to(message, f"Current map level: {current_map_level}")
            return
        last_map_level = current_map_level
        current_map_level = int(message.text.split(' ')[1])
        logger.info(f"Map level changed from {last_map_level} to {current_map_level}")
        bot.reply_to(message, f"Map level set to {current_map_level}")
    except ValueError:
        logger.debug(f"Invalid map level: {message}")
        bot.reply_to(message, f"Invalid map level")


# @bot.message_handler(commands=['countdown', 'c'])
# def countdown(message):
#     global timer
#     try:
#         if len(message.text.split(' ')) < 2:
#             if len(timer) == 0:
#                 bot.reply_to(message, f"No countdown")
#                 return
#             for t in timer:
#                 bot.reply_to(message, f"{t['title']}: {t['time']} minutes")
#             return
#         time = int(message.text.split(' ')[1])
#         title = message.text.split(' ')[2] if len(message.text.split(' ')) > 2 else "NoName"
#         new_timer = {'time': time, 'title': title}
#         timer.append(new_timer)
#         logger.info(f"New Countdown {new_timer['title']}: {new_timer['time']} minutes")
#         bot.reply_to(message, f"New Countdown {new_timer['title']}: {new_timer['time']} minutes")
#         return
#     except ValueError:
#         logger.debug(f"Invalid countdown: {message}")
#         bot.reply_to(message, f"Invalid countdown")


@bot.message_handler(commands=['poi'])
def poi(message):
    poi_choice = random.choice(pois[current_map_level])
    logger.info(f"POI: {poi_choice['map']}, {poi_choice['title']}, {poi_choice['url']}")
    bot.reply_to(message, f"New POI: {poi_choice['title']}\n"
                          f"{poi_choice['url']}\n"
                          f"Take a Selfie for a Point! 📸")


@bot.message_handler(commands=['respawn'])
def respawn(message):
    poi_choice = random.choice(pois[current_map_level])
    logger.info(f"Respawn: {poi_choice['map']}, {poi_choice['title']}, {poi_choice['url']}")
    bot.reply_to(message, f"Respawn at: {poi_choice['title']}\n"
                          f"{poi_choice['url']}\n"
                          f"Take a Selfie to Respawn! 📸\n You are safe for 5 minutes after respawn!")

# show points table
@bot.message_handler(commands=['points', 'table'])
def points(message):
    ...

# adds points to player:
# add 3 points /ap dominik 3
# add one point /ap dominik
# TODO: test username autocomplete
@bot.message_handler(commands=['addpoints', 'ap'])
def addpoints(message):
    ...

@bot.message_handler(commands=['removepoints', 'rp'])
def removepoints(message):
    ...

@bot.message_handler(commands=['map'])
def map(message):
    # loop over maps directory
    # reply map with current_map_level  
    ...

@bot.message_handler(commands=['permissions'])
def change_permissions(message):
    ...

bot.infinity_polling()
