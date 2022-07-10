'''
Discord bot to check for breakouts.
'''

# Project imports
import utils

# Other imports
import pandas as pd
import yfinance as yf
from datetime import datetime, date
from discord.ext import commands, tasks


# For type hinting
from pandas import DataFrame as pandasDF

# Discord controls
bot = commands.Bot(command_prefix='>')

# Dataframe colum references
METRIC_COLS = ['price', 'volume']
CLEAN_COLS = ['price', 'volume', 'date', 'status']
WATCHLIST_COLS = ['ticker', 'price', 'volume', 'date', 'status']

# Other global variables
LINES = '\n--------------------\n'
BOT_ID = 'INSERT'
CHANNEL_ID = INSERT # As integer, not string!
DATE_STR = date.today().strftime('%Y-%m-%d')

# Bot commands --------------------------------------------------------------
@bot.command()
async def add(ctx,
              ticker: str,
              buy_price: str,
              avg_vol: str):
    '''
    Add a ticker to the watchlist

    Parameters
    ----------
    ticker : str
        The ticker to add
    buy_price : str
        The buy-in price for the stock
    avg_vol : str
        The average volume for the stock

    Returns
    -------
    None
    '''
    
    # Grab the current watchlist
    df_watch = pd.read_csv('watchlist.csv')
    
    # Form a dataframe for the stock data we wish to add, note that the current
    # time is applied so that we can keep the most recent data
    curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_add = pandasDF({
        'ticker': [ticker.upper()],
        'price': [buy_price],
        'volume': [avg_vol],
        'date': [curr_time],
        'status': [0],
    })
    
    # Concat the new entry with the watchlist, and perform cleaning
    utils.clean_watchlist(
        pd.concat(
            [df_watch, df_add],
            axis = 0,
        ),
        CLEAN_COLS
    )
    
    await ctx.send('Yum yum, another ticker added to the watchlist!')
    

@bot.command()
async def change_price(ctx,
                       ticker: str,
                       price: str):
    '''
    Update the price for a ticker
    
    Parameters
    ----------
    ticker: str
        The ticker to update
    price: str
        The price to update
    '''

    # Load in the watchlist for altering
    df = pd.read_csv('watchlist.csv')
    df.loc[df['ticker'] == ticker.upper(), 'price'] = float(price)
    df.to_csv('watchlist.csv', index = False)
    
    await ctx.send(f'The watch price has been changed for {ticker} :)')


@bot.command()
async def remove(ctx,
                 ticker: str):
    '''
    Remove a single ticker from the watchlist
    
    Paramaters
    ----------
    ticker: str
        The ticker to remove from the watchlist
    '''
    
    # Load in the watchlist for altering
    df = pd.read_csv('watchlist.csv')
    
    # Filter the df and save the new watchlist
    (
     df[df['ticker'] != ticker]
     .to_csv('watchlist.csv', index = False)
     )
    
    await ctx.send('And he\'s outta here!')


@bot.command()
async def nuke_watchlist(ctx):
    '''
    Delete all entries in the watchlist
    '''
    df = pandasDF({key: [] for key in WATCHLIST_COLS})
    df.to_csv('watchlist.csv', index = False)
    
    await ctx.send('Muhaha! The watchlist has been destroyed!')
    

@bot.command()
async def reset_status(ctx):
    '''
    Reset the status of all tickers on the watchlist
    '''
    
    df = pd.read_csv('watchlist.csv')
    df.loc[:, 'status'] = 0
    df.to_csv('watchlist.csv', index = False)
    
    await ctx.send('Watching status reset across all tickers :)')
        

@bot.command()
async def print_watchlist(ctx):
    '''
    Print out the current watchlist + parameters
    '''
    
    df = pd.read_csv('watchlist.csv')
    
    # Initialise an empty string to place the message on
    msg = ''

    for n in range(0, df.shape[0]):
        msg = (
            msg + 
            'Ticker : ' + str(df.loc[n, 'ticker']) + '\n' + 
            'Buy price : ' + str(df.loc[n, 'price']) + '\n' + 
            'Avg volume : ' + str(df.loc[n, 'volume']) + 
            LINES
        )
        
    await ctx.send(msg)


@bot.command()
async def watchlist_tickers(ctx):
    '''
    Only print out the tickers from the watchlist
    '''
    
    tickers = pd.read_csv('watchlist.csv')['ticker'].tolist()
    await ctx.send(
        'Here are the tickers on your buy watchlist : \n' +
        ', '.join(tickers) + '\n' +
        'Hopefully these give us lots of moneys!'
    )


@bot.command()
async def watchlist_ticker(ctx, 
                           ticker: str):
    '''
    Print out the info from a single ticker
    '''
    try: 
        # Changed to a numpy array so indexing can be used
        df = pd.read_csv('watchlist.csv')
        df = df[df['ticker'] == ticker].values[0]

        msg = (
            'Ticker : ' + str(df[0]) + '\n' + 
            'Buy price : ' + str(df[1]) + '\n' + 
            'Avg volume : ' + str(df[2]) 
        )
            
        await ctx.send(msg)
    except:
        await ctx.send(
            'Hmm... something went wrong with giving the info for ' + 
            ticker + ', it is either not on the watchlist, orrrrr you ' + 
            'typed it in incorrectly ;)'
        )
    
@bot.command()
async def current_lod(ctx, 
                      ticker: str):
    '''
    Get the current low of the day for a ticker, so that a stop loss can be set
    '''
    try:
        df = yf.download(
            ticker,
            interval = '1d',
            period = '1d',
            progress = False,
        )
        
        price = df['Close'].values[-1]
        lod = df['Low'].values[-1]
        stop_perc = round(100*(price/lod - 1), 2)
        
        msg = (
            'Current low for ' + ticker + ' is ' + str(round(lod, 2)) +
            ', which is ' + str(stop_perc) + '% away from the current price.'
        )
        
        await ctx.send(msg)
    except:
        await ctx.send(
            'Hmm, there was a problem with getting ' + ticker + 
            '... Did you type in the name incorrectly? ;)'
        )
    
@tasks.loop(seconds = 5*60)
async def watch_market_task():
    '''
    Watch the market periodically, to check if any breakouts have occurred
    on the watchlist stocks
    '''    
    
    df = pd.read_csv('watchlist.csv')
    tickers = df['ticker'].tolist()
    
    checked_df = []
    for ticker in tickers:
        
        # Obtain the info for this ticker from the df
        df_ticker = df[df['ticker'] == ticker]
        status = df_ticker['status'].values[-1]
        watch_price = df_ticker['price'].values[-1]
        watch_vol = float(df_ticker['volume'].values[-1])
        
        # The status indicates which volume level we are at, 4 is the highest (2x avg volume)
        if status < 4:
            
            # Grab the current ticker data from yfinance
            try:
                price, volume, low = utils.get_stock_data(ticker)
            except:
                price = 0; volume = 0; low = 0
            
            # pric = 0 indicates that a problem has been hit
            if price > 0:
                
                if price > watch_price:
                    
                    try:
                        msg, new_status = utils.get_status_message(
                            ticker = ticker,
                            vol_ratio = round(volume/watch_vol, 2),
                            price_gap = round(100*(price/watch_price - 1), 2),
                            status = status,
                            price = price,
                            low = low,
                            LINES = LINES,
                        )
                    
                    except Exception as e:
                        print(f'Problem checking status for {ticker}')
                        print('Error message : ' + str(e))
                        
                    if new_status > status:                
                        
                        status = new_status
                        
                        await (
                            bot
                            .get_channel(CHANNEL_ID)
                            .send(msg)
                        )
                    
            else:
                print('Problem downloading ' + ticker)
                    
        checked_df.append([
            ticker,
            watch_price,
            watch_vol,
            df_ticker['date'].values[-1],
            status,
        ])
        
    (
     pd.Dataframe(columns = WATCHLIST_COLS, data = checked_df)
     .to_csv('watchlist.csv', index = False)
    )


@bot.command()
async def watch_market(ctx):
    '''
    The command to call the background task of watching the market
    '''
    await ctx.send('Ugh, do I have to go to work? ... Fine, let\'s get rich!!!')
    watch_market_task.start()

    
@bot.event
async def on_ready():
    msg = (
        'What is up my super handsome friend! Are you ready to make some ' +
        'serious dinero?! :D'
    )
    
    await (
        bot
        .get_channel(CHANNEL_ID)
        .send(msg)
    )

bot.run(BOT_ID)