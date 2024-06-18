import json
# https://github.com/eternnoir/pyTelegramBotAPI
import telebot  # pip install pyTelegramBotAPI
from loguru import logger
import csv
from threading import Timer
import time

from bot_timer import BotTimer
from pois import read_pois

logger.add('logs/logs.log', format="{time} {level} {message}", level="INFO", rotation="01:00")

max_map_level = 5
current_map_level = 1

permissions = [False, False, False, False, False, False, False, False]
commands = ['/config', '/poi', '/respawn', '/score', '/addpoints', '/removepoints', '/map', '/permissions']

scores = {}


def read_secrets():
    with open('data/secrets.json') as f:
        return json.load(f)


def read_poi():
    return read_pois('data/poi.csv')


def read_maps():
    maps = {}
    reader = csv.DictReader(open('data/maps.csv', 'r', encoding='utf-8'))
    for row in reader:
        maps[int(row['level'])] = row['url']
    return maps


pois = read_poi()
maps = read_maps()
secrets = read_secrets()
bot = telebot.TeleBot(secrets['bot_token'], parse_mode='HTML')
try:
    game_master = int(secrets['game_master'])
except ValueError:
    print("Invalid game_master in secrets.json")
    exit()
logger.info('Bot started')


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    if message.from_user.id == game_master:
        bot.send_message(message.chat.id, "Available commands: /config, /poi, /respawn, "
                                          "/score, /addpoints, /removepoints, /map, /permissions, /reset")
        logger.info(f"Message send: Available commands: /config, /poi, /respawn, "
                    "/score, /addpoints, /removepoints, /map, /permissions, /reset")


@bot.message_handler(commands=['config', 'm'])
def config(message):
    if permissions[0] or message.from_user.id == game_master:
        global current_map_level
        try:
            if len(message.text.split(' ')) < 2:
                bot.reply_to(message, f"Current map level: {current_map_level}")
                logger.info(f"Message send: Current map level: {current_map_level}")
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
        poi_choice = pois.get_random_poi(current_map_level)
        logger.info(f"POI: {poi_choice.map}, {poi_choice.title}, {poi_choice.url}")
        bot.send_message(message.chat.id, f"New POI: {poi_choice.title}\n"
                                          f"{poi_choice.url}\n"
                                          f"Take a Selfie for a Point! 📸")


@bot.message_handler(commands=['respawn'])
def respawn(message):
    if permissions[2] or message.from_user.id == game_master:
        poi_choice = pois.get_random_poi(current_map_level)
        logger.info(f"Respawn: {poi_choice.map}, {poi_choice.title}, {poi_choice.url}")
        bot.reply_to(message, f"Respawn at: {poi_choice.title}\n"
                              f"{poi_choice.url}\n"
                              f"Take a Selfie to Respawn! 📸\n You are safe for 5 minutes after respawn!")


# show points table
@bot.message_handler(commands=['points', 'table', 'score'])
def points(message):
    if permissions[3] or message.from_user.id == game_master:
        text = "<pre>| Player        | Score |\n|---------------|-------|\n"
        text += "\n".join([f"| {player.ljust(13)[:13]} | {str(score).rjust(5)} |" for player, score in scores.items()])
        text += "</pre>"
        bot.send_message(message.chat.id, text, parse_mode='HTML')
        logger.info(f"Message send: Points Table:\n{text[5:-6]}")


# adds points to player:
# add 3 points /ap dominik 3
# add one point /ap dominik
@bot.message_handler(commands=['addpoints', 'ap'])
def add_points(message):
    if permissions[4] or message.from_user.id == game_master:
        parts = message.text.split(' ')
        if len(parts) < 2 or len(parts) > 3:
            bot.reply_to(message, "Invalid command: no player name")
            logger.debug(f"Invalid command: no player name: {message}")
            return
        if len(parts) == 2:
            points_to_add = 1
        if len(parts) == 3:
            try:
                points_to_add = int(parts[2])
            except ValueError:
                bot.reply_to(message, "Invalid command: points not a number")
                logger.debug(f"Invalid command: points not a number: {message}")
                return
        player = parts[1]
        if player not in scores:
            scores[player] = 0
        scores[player] += points_to_add
        logger.info(f"{points_to_add} Points added to {player}: {scores[player]}")
        bot.reply_to(message, f"{points_to_add} Points added to {player}: {scores[player]}")


@bot.message_handler(commands=['removepoints', 'rp'])
def remove_points(message):
    if permissions[5] or message.from_user.id == game_master:
        parts = message.text.split(' ')
        if len(parts) < 2 or len(parts) > 3:
            bot.reply_to(message, "Invalid command: no player name")
            logger.debug(f"Invalid command: no player name: {message}")
            return
        if len(parts) == 2:
            points_to_remove = 1
        if len(parts) == 3:
            try:
                points_to_remove = int(parts[2])
            except ValueError:
                bot.reply_to(message, "Invalid command: points not a number")
                logger.debug(f"Invalid command: points not a number: {message}")
                return
        player = parts[1]
        if player not in scores:
            scores[player] = 0
        scores[player] -= points_to_remove
        logger.info(f"{points_to_remove} Points removed from {player}: {scores[player]}")
        bot.reply_to(message, f"{points_to_remove} Points removed from {player}: {scores[player]}")


@bot.message_handler(commands=['deletescore', 'dp'])
def delete_score(message):
    if message.from_user.id == game_master:
        parts = message.text.split(' ')
        if len(parts) != 2:
            bot.reply_to(message, "Invalid command: no player name")
            logger.debug(f"Invalid command: no player name: {message}")
            return
        player = parts[1]
        if player in scores:
            del scores[player]
            logger.info(f"Score deleted for {player}")
            bot.reply_to(message, f"Score deleted for {player}")
        else:
            logger.info(f"Score not found for {player}")
            bot.reply_to(message, f"Score not found for {player}")


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


@bot.message_handler(commands=['reset'])
def reset(message):
    if message.from_user.id == game_master:
        global scores
        scores = {}
        global current_map_level
        current_map_level = 1

        global pois
        pois = read_poi()
        global maps
        maps = read_maps()

        logger.info(f"Map level reset to {current_map_level}")
        bot.reply_to(message, f"Map level reset to {current_map_level}")


# Function to send a notification
def notify(user_id, timer_name, command):
    bot.send_message(user_id, f"{timer_name}")
    logger.info(f"Timer {timer_name} expired.")
    if command is not None:
        global current_map_level
        if command[0] == 'map':
            bot.send_message(user_id, f"Map {current_map_level}: {maps[current_map_level]}")
            logger.info(f"Timer {timer_name}: Message send: Map {current_map_level}: {maps[current_map_level]}")
        if command[0] == 'config':
            current_map_level += 1
            bot.send_message(user_id, f"Current map level: {current_map_level}")
            logger.info(f"Timer {timer_name}: Map level changed to {current_map_level}")


timers = []


# Command to set a new timer
@bot.message_handler(commands=['timer'])
def set_timer(message):
    if message.from_user.id == game_master:
        try:
            command = message.text.split()
            if len(command) >= 3:  # /timer name duration [map] [config]
                timer_name = command[1]
                if timer_name in timers:
                    timers[timer_name].pause()
                    timers.remove(timers[timer_name])
                interval = int(command[2])
                config = current_map_level + 1 if "config" in command else None
                timers.append(BotTimer(timer_name, interval, message.chat.id, timer_function,
                                       map=True if "map" in command else False, config=config))
                bot.reply_to(message, f"Timer for {timer_name} set for {interval} minutes.")
                logger.info(f"Timer for {timer_name} set for {interval} minutes.")
            elif len(command) == 2:  # /timer name
                timer_name = command[1]
                found = False
                for timer in timers:
                    if timer == timer_name:
                        remaining_time = timer.get_remaining_time()
                        bot.reply_to(message, f"Timer for {timer_name} has {remaining_time} minutes remaining.")
                        logger.info(f"Timer for {timer_name} has {remaining_time} minutes remaining.")
                        found = True
                        continue
                if not found:
                    bot.reply_to(message, f"No active timer found for {timer_name}.")
                    logger.info(f"No active timer found for {timer_name}.")
            elif len(command) == 1:
                for timer in timers:
                    remaining_time = timer.get_remaining_time()
                    bot.send_message(message.from_user.id, f"Timer for {timer} has {remaining_time} minutes remaining.")
                    logger.info(f"Timer for {timer} has {remaining_time} minutes remaining.")
        except ValueError:
            bot.reply_to(message, "Please provide the duration in minutes as an integer.")
            logger.debug(f"Invalid timer: {message}")


def timer_function(bot_timer):
    print(f"Timer {bot_timer.name} finished")


bot.infinity_polling()
