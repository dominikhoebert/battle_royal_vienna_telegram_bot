import json
# https://github.com/eternnoir/pyTelegramBotAPI
import telebot  # pip install pyTelegramBotAPI
from loguru import logger
import csv
import os
import yaml

from bot_timer import BotTimer, PreparedTimer
from pois import read_pois

logger.add('logs/logs.log', format="{time} {level} {message}", level="INFO", rotation="01:00")

max_map_level = 5
current_map_level = 1

permissions = 0

scores = {}
timers = []


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
    if permissions == 2 or message.from_user.id == game_master:
        bot.send_message(message.chat.id, "Available commands: /start /help /config /poi /respawn /score /timer "
                                          "/addpoints /removepoints /map /permissions /reset /play /pause /resume")
        logger.info(f"Message send: Start message")


help_message = """Commands

- /start - See all commands
- /help - See all commands and description
- /config map-level - Set the map level (1-5; 1 is the biggest)
- /config - Get the map level
- /poi - Send a random Point of Interest for the current map level
- /respawn - Send a random Point of Interest to respawn at
- /score - Send the score table
- /timer name minutes command - Creates a timer with a name and for a certain number of minutes and run commands (`map` or `config`)
- /timer name minutes - Creates a timer with a name and for a certain number of minutes
- /timer name - Gets the remaining time of the timer
- /timer - Gets the remaining time of all timers
- /addpoints player points - Add points to a player for the score table
- /addpoints player - Add 1 point to a player for the score table
- /removepoints player points - Remove points from a player for the score table
- /removepoints player - Remove 1 point from a player for the score table
- /deletescore playername - Remove Player from Score Table
- /map - Send the current map
- /permissions level  - Set the permissions for the commands (0 game master only; 1 poi, respawn, addpoints for players, 2 unrestriced)
- /reset - Reset the game (map level, cooldowns, points table)
- /play gamename - Start a game using a .yaml gameplan
- /pause - Pause all timers
- /resume - Resume all timers"""


@bot.message_handler(commands=['help'])
def help(message):
    if permissions == 2 or message.from_user.id == game_master:
        bot.reply_to(message, help_message, parse_mode='MARKDOWN')
        logger.info(f"Message send: Help message")


@bot.message_handler(commands=['config', 'm'])
def config(message):
    if permissions == 2 or message.from_user.id == game_master:
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


@bot.message_handler(commands=['poi'])
def poi(message):
    if permissions >= 1 or message.from_user.id == game_master:
        poi_choice = pois.get_random_poi(current_map_level)
        logger.info(f"POI: {poi_choice.map}, {poi_choice.title}, {poi_choice.url}")
        bot.send_message(message.chat.id, f"New POI: {poi_choice.title}\n"
                                          f"{poi_choice.url}\n"
                                          f"Take a Selfie for a Point! 📸")
        if poi_choice.lat is not None:
            bot.send_venue(message.chat.id, poi_choice.lat, poi_choice.long, title=poi_choice.title,
                           address=poi_choice.address)


@bot.message_handler(commands=['respawn'])
def respawn(message):
    if permissions >= 1 or message.from_user.id == game_master:
        poi_choice = pois.get_random_poi(current_map_level)
        logger.info(f"Respawn: {poi_choice.map}, {poi_choice.title}, {poi_choice.url}")
        bot.reply_to(message, f"Respawn at: {poi_choice.title}\n"
                              f"{poi_choice.url}\n"
                              f"Take a Selfie to Respawn! 📸\n You are safe for 5 minutes after respawn!")


# show points table
@bot.message_handler(commands=['points', 'table', 'score'])
def points(message):
    if permissions == 2 or message.from_user.id == game_master:
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
    if permissions >= 1 or message.from_user.id == game_master:
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
    if permissions == 2 or message.from_user.id == game_master:
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
    if permissions == 2 or message.from_user.id == game_master:
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
    if permissions == 2 or message.from_user.id == game_master:
        bot.send_message(message.chat.id, f"Map {current_map_level}: {maps[current_map_level]}")
        logger.info(f"Message send: Map {current_map_level}: {maps[current_map_level]}")


# permission levels: 0 game master only; 1 poi, respawn, addpoints for players; 2 unrestriced
@bot.message_handler(commands=['permissions'])
def change_permissions(message):
    global permissions
    if permissions == 2 or message.from_user.id == game_master:
        try:
            command = message.text.split(' ')
            if len(command) != 2:
                bot.reply_to(message, "Invalid permissions")
                logger.info(f"Invalid permissions: {message}")
                return
            else:
                permissions = int(command[1])
                return bot.reply_to(message, f"Permissions set to: {permissions}")
        except ValueError:
            return bot.reply_to(message, "Invalid permissions")


@bot.message_handler(commands=['reset'])
def reset(message):
    if permissions == 2 or message.from_user.id == game_master:
        global scores
        scores = {}
        global current_map_level
        current_map_level = 1

        global pois
        pois = read_poi()
        global maps
        maps = read_maps()
        global timers
        for timer in timers:
            timer.pause()
        timers = []

        logger.info("Full reset: scores, map level, pois, maps, timers")
        bot.reply_to(message, f"Full reset: scores, map level, pois, maps, timers")


# Command to set a new timer
@bot.message_handler(commands=['timer'])
def set_timer(message):
    if permissions == 2 or message.from_user.id == game_master:
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
                        bot.reply_to(message, f"Timer for {timer_name} has {remaining_time:.1f} minutes remaining.")
                        logger.info(f"Timer for {timer_name} has {remaining_time:.1f} minutes remaining.")
                        found = True
                        continue
                if not found:
                    bot.reply_to(message, f"No active timer found for {timer_name}.")
                    logger.info(f"No active timer found for {timer_name}.")
            elif len(command) == 1:
                if len(timers) == 0:
                    bot.reply_to(message, "No active timers.")
                    logger.info("No active timers.")
                else:
                    for timer in timers:
                        remaining_time = timer.get_remaining_time()
                        bot.send_message(message.from_user.id,
                                         f"Timer for {timer.name} has {remaining_time:.1f} minutes remaining.")
                        logger.info(f"Timer for {timer.name} has {remaining_time:.1f} minutes remaining.")
        except ValueError:
            bot.reply_to(message, "Please provide the duration in minutes as an integer.")
            logger.debug(f"Invalid timer: {message}")


def timer_function(bot_timer: BotTimer):
    bot.send_message(bot_timer.user_id, f"{bot_timer.name}")
    logger.info(f"Timer {bot_timer.name} expired.")
    global current_map_level
    if bot_timer.config is not None:
        current_map_level = bot_timer.config
        bot.send_message(bot_timer.user_id, f"Current map level: {current_map_level}")
        logger.info(f"Timer {bot_timer.name}: Map level changed to {current_map_level}")
    if bot_timer.map:
        bot.send_message(bot_timer.user_id, f"Map {current_map_level}: {maps[current_map_level]}")
        logger.info(f"Timer {bot_timer.name}: Message send: Map {current_map_level}: {maps[current_map_level]}")
    if bot_timer.message is not None:
        bot.send_message(bot_timer.user_id, f"{bot_timer.message}")
        logger.info(f"Timer {bot_timer.name}: Message send: {bot_timer.message}")
    if bot_timer.next_prepared_timer is not None:
        next_bot_timer = bot_timer.next_prepared_timer.create_bot_timer()
        timers.append(next_bot_timer)
        logger.info(f"Timer {bot_timer.name}: Next timer started: {next_bot_timer.name}")
    timers.remove(bot_timer)


@bot.message_handler(commands=['play'])
def play_game(message):
    if permissions == 2 or message.from_user.id == game_master:
        # read in command[1]
        command = message.text.split(' ')
        if len(command) == 2:
            # find command[1].yaml or .yml in data folder
            directory = os.fsencode("data")
            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                if (filename.endswith(".yaml") or filename.endswith(".yml")) and filename.startswith(command[1]):
                    # read in file
                    first_timer = create_timers_from_file(filename, message.chat.id)
                    timers.append(first_timer)
                    bot.send_message(message.chat.id, f"Game started: {command[1]}")
                    print(timers)
                    return
            bot.send_message(message.chat.id, "File not found: " + command[1])
            logger.debug(f"File not found: {command[1]}")
        else:
            bot.send_message(message.chat.id, "Invalid command: /play <filename>")
            logger.debug(f"Invalid command: {message}")
            return


def create_timers_from_file(filename, user_id):
    # read in file
    with open(f'data/{filename}', 'r') as file:
        game_plan_yaml = yaml.safe_load(file)
        if 'game' not in game_plan_yaml:
            bot.send_message(user_id, "Invalid game plan file")
            logger.debug(f"Invalid game plan file, 'game' not found: {filename}")
            return
        game = game_plan_yaml['game']
        start_message = game.get('name', "") + " " + game.get('description', "")
        bot.send_message(user_id, start_message)
        logger.info(f"Game started: {start_message}")
        try:
            timers_plan = game_plan_yaml['game']['timer']
        except KeyError:
            bot.send_message(user_id, "No timers found in file")
            logger.debug(f"No timers found in file: {filename}")
            return
        # create prepared timers
        previous_timer = None
        first_timer = None
        timer_count = 0
        for timer in timers_plan:
            try:
                name = next(iter(timer))
                interval = timer[name]
                message = timer.get('message', None)
                map = timer.get('map', False)
                config = timer.get('config', None)
                next_prepared_timer = timer.get('next_prepared_timer', None)
                prepared_timer = PreparedTimer(name, interval, user_id, timer_function, message, map, config)
                timer_count += 1
            except KeyError:
                print("Invalid timer")
                bot.send_message(user_id, "Invalid timer in file")
                logger.debug(f"Invalid timer in file: {filename}")
                return
            if first_timer is None:
                first_timer = prepared_timer
            if previous_timer is not None:
                previous_timer.next_prepared_timer = prepared_timer
            previous_timer = prepared_timer
        bot.send_message(user_id, f"{timer_count} timers created")
        logger.info(f"{timer_count} timers created")
        # create bot timers
        # start timers
        return first_timer.create_bot_timer()


@bot.message_handler(commands=['pause'])
def pause_game(message):
    if permissions == 2 or message.from_user.id == game_master:
        # pause all timers
        for timer in timers:
            timer.pause()
        bot.send_message(message.chat.id, "Game paused")
        logger.info("Game paused. All timers paused")


@bot.message_handler(commands=['resume'])
def pause_game(message):
    if permissions == 2 or message.from_user.id == game_master:
        # resume all timers
        for timer in timers:
            timer.resume()
        bot.send_message(message.chat.id, "Game resumed")
        logger.info("Game resumed. All timers resumed")


bot.infinity_polling()
