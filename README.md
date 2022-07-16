# market_watcher

A simple discord bot which can watch the market for buy criteria (here, if a ticker breaches a user-defined price threshold). 

## How to use
Firstly, you need to have a discord server with a bot added to it; you can do this by following [this guide](https://discordpy.readthedocs.io/en/stable/discord.html) or [my medium article](https://medium.com/@dannygrovesn7/i-programmed-a-humorous-discord-bot-to-watch-the-financial-markets-for-me-b8585f8659e3) on this topic.

Once that is set-up, the bot is run from the `discord_bot.py` script, this needs to be configured with both the `BOT_ID` (bot token), and `CHANNEL_ID` which you can get by right-clicking the discord channel you wish to send messages into.

**Note**: If you are using an IDE like Spyder, then you need to set the runtime so that it runs from the console. This can be done by pressing `ctrl+F6` and selecting the "Execute in an external system terminal".

Any commands can be called by using `>command_name arg1 arg2 arg3 ... argn` from the discord channel the bot is sending messages into.

## Implemented commands
- `>add ticker buy_price avg_vol` - add a new ticker to the watchlist
- `>change_price ticker price` - change the watch price for a ticker on the watchlist
- `>remove ticker` - remove a ticker from the watchlist
- `>nuke_watchlist` - clean the whole watchlist of entries
- `>reset_status` - reset the status flag across all entries in the watchlist
- `>print_watchlist` - send the contents of the watchlist to the discord channel
- `>watchlist_tickers` - send all tickers on the watchlist to the discord channel
- `>watchlist_ticker ticker` - print the info of a single ticker on the watchlist
- `>current_lod` - current low of the day for any ticker
- `>watch_market` - perform the market watching task

## Some side notes
1. I personally use a modified version of this bot to watch for breakout candidates, using algorithmically drawn trend lines to deduce buy-in prices ([see my medium article](https://medium.com/@dannygrovesn7/creating-stock-market-trend-lines-in-35-lines-of-python-865906d5ecef)). The bot is deployed on my raspberry-pi since it doesn't require much computing power; I set up a cron-job to start the bot when the Pi boots up.
2. This script is very bare-bones and quite simple, the purpose is to give a starting place for anyone wishing to develop further
3. The watchlist.csv file does not contain any buy-prices + volume I am considering; this is merely an example.
4. If you use this in different and exciting ways, or have ideas of how to improve, please get in touch!
