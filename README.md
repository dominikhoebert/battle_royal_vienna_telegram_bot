# battle royal vienna telegram bot

Simple Telegram Bot sends random Point of Interrests (POIs) in Vienna to a group chat.
Intended to play a game of "Battle Royal" in Vienna.

[Rules](https://github.com/dominikhoebert/battle_royal_vienna_telegram_bot/blob/master/Battle%20Royal%20Vienna.md)

## Commands

- `/start` - See all commands
- `/config map-level` - Set the map level (1-5; 1 is the biggest)
- `/config` - Get the map level
- `/poi` - Send a random Point of Interest for the current map level
- `/respawn` - Send a random Point of Interest to respawn at
- `/score` - Send the score table
- `/timer name minutes command` - Creates a timer with a name and for a certain number of minutes and run commands (`map` or `config`)
- `/timer name minutes` - Creates a timer with a name and for a certain number of minutes
- `/timer name` - Gets the remaining time of the timer
- `/timer` - Gets the remaining time of all timers
- `/addpoints player points` - Add points to a player for the score table
- `/addpoints player` - Add 1 point to a player for the score table
- `/removepoints player points` - Remove points from a player for the score table
- `/removepoints player` - Remove 1 point from a player for the score table
- `/deletescore playername` - Remove Player from Score Table
- `/map` - Send the current map
- `/permissions 0 0 0 0 0 0 0 0 ` - Set the permissions for the commands (0 game master only; 1 all players)
- `/reset` - Reset the game (map_level, cooldowns, points table)
- `/play gamename` - Start a game using a .yaml gameplan
- `/pause` - Pause all timers
- `/resume` - Resume all timers


## TODO:

- ~~maps as routes~~
- ~~points table~~
- ~~remove player from points table~~
- ~~game master mode: only owner can do certain actions~~
- ~~map: post the map~~
- ~~timer~~
- ~~timer run command~~
- ~~prepeare gameplan~~ (~~/play~~, /pause)
- ~~pois cooldown~~
- ~~reset game~~ (~~pois cooldown~~, ~~points table~~)
- test telegram location https://core.telegram.org/bots/api#location
- https://pytba.readthedocs.io/en/latest/sync_version/index.html#telebot.TeleBot.send_location
- update /start
- update /permissions
- help
