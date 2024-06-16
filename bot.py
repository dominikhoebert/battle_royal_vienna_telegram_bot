import json
# https://github.com/eternnoir/pyTelegramBotAPI
import telebot  # pip install pyTelegramBotAPI
from loguru import logger
import csv
import random

logger.add('logs/logs.log', format="{time} {level} {message}", level="INFO", rotation="01:00")

max_map_level = 4
current_map_level = 1

permissions = [False, False, False, False, False, False, False, False]
commands = ['/config', '/poi', '/respawn', '/points', '/addpoints', '/removepoints', '/map', '/permissions']


# timer = []


def read_secrets():
    with open('data/secrets.json') as f:
        return json.load(f)


def read_poi():
    pois = {}
    for i in range(1, max_map_level + 1):
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


def read_maps():
    maps = {}
    reader = csv.DictReader(open('data/maps.csv', 'r', encoding='utf-8'))
    for row in reader:
        maps[int(row['level'])] = row['url']
    return maps


pois = read_poi()
maps = read_maps()
secrets = read_secrets()
bot = telebot.TeleBot(secrets['bot_token'])
game_master = int(secrets['game_master'])
logger.info('Bot started')


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    if message.from_user.id == game_master:
        bot.reply_to(message, "Available commands: /config, /poi, /respawn, "
                              "/points, /addpoints, /removepoints, /map, /permissions")


@bot.message_handler(commands=['config', 'm'])
def config(message):
    if permissions[0] or message.from_user.id == game_master:
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
    if permissions[1] or message.from_user.id == game_master:
        poi_choice = random.choice(pois[current_map_level])
        logger.info(f"POI: {poi_choice['map']}, {poi_choice['title']}, {poi_choice['url']}")
        bot.reply_to(message, f"New POI: {poi_choice['title']}\n"
                              f"{poi_choice['url']}\n"
                              f"Take a Selfie for a Point! 📸")


@bot.message_handler(commands=['respawn'])
def respawn(message):
    if permissions[2] or message.from_user.id == game_master:
        poi_choice = random.choice(pois[current_map_level])
        logger.info(f"Respawn: {poi_choice['map']}, {poi_choice['title']}, {poi_choice['url']}")
        bot.reply_to(message, f"Respawn at: {poi_choice['title']}\n"
                              f"{poi_choice['url']}\n"
                              f"Take a Selfie to Respawn! 📸\n You are safe for 5 minutes after respawn!")


# show points table
@bot.message_handler(commands=['points', 'table'])
def points(message):
    if permissions[3] or message.from_user.id == game_master:
        ...


# adds points to player:
# add 3 points /ap dominik 3
# add one point /ap dominik
# TODO: test username autocomplete
@bot.message_handler(commands=['addpoints', 'ap'])
def add_points(message):
    if permissions[4] or message.from_user.id == game_master:
        ...


@bot.message_handler(commands=['removepoints', 'rp'])
def remove_points(message):
    if permissions[5] or message.from_user.id == game_master:
        ...


@bot.message_handler(commands=['map'])
def post_map(message):
    if permissions[6] or message.from_user.id == game_master:
        bot.send_message(message.chat.id, f"Map {current_map_level}: {maps[current_map_level]}")
        logger.info(f"Message send: Map {current_map_level}: {maps[current_map_level]}")


# set permissions for /config, /poi, /respawn, /points, /addpoints, /removepoints, /map, /permissions
# /permissions 0 0 0 0 0 0 0 0
@bot.message_handler(commands=['permissions'])
def change_permissions(message):
    if permissions[7] or message.from_user.id == game_master:
        try:
            if len(message.text.split(' ')) != 9:
                return bot.reply_to(message, "set permissions for /config, /poi, /respawn, /points, /addpoints,"
                                             " /removepoints, /map, /permissions\nexample: /permissions 0 0 0 0 0 0 0 0")

            else:
                print(message.text.split(' '))
                for i in range(1, 9):
                    permissions[i - 1] = bool(int(message.text.split(' ')[i]))
                logger.info(f"Permissions set to: {permissions}")
                permission_icons = ['✔️' if permissions[i] else '❌' for i in range(8)]
                permission_string = "\n".join([f"{commands[i]} {permission_icons[i]}" for i in range(8)])
                return bot.reply_to(message, f"Permissions set to:\n{permission_string}")
        except ValueError:
            return bot.reply_to(message, "Invalid permissions")


bot.infinity_polling()
