import yfinance as yf

from typing import Tuple
from pandas import DataFrame as pandasDF

def get_stock_data(ticker: str) -> Tuple[float, float, float]:
    '''
    Get the current closing price and volume for the stock

    Parameters
    ----------
    ticker : str
        The ticker we are considering

    Returns
    -------
    price : float
        The current price of the stock
    volume : float
        The current volume of the stock
    low : float
        The current low of the day
    '''
    
    try:
        df = yf.download(
            ticker,
            interval = '1d',
            period = '1d',
            progress = False,
            threads = False,
        )
                
        return (
            df['Close'].values[-1],
            df['Volume'].values[-1],
            df['Low'].values[-1],
        )
    
    # In this case, either the ticker is wrong, or the data cannot be downloaded
    except:
        return 0, 0, 0

def clean_watchlist(df: pandasDF,
                    clean_cols: list):
    '''
    Clean the watchlist by removing duplicate entries, and then save the
    watchlist back to a csv file

    Parameters
    ----------
    df : pandasDF
        The current watchlist
    clean_cols : list
        A list of all columns to clean

    Returns
    -------
    None
    '''
    
    (
     df
     .sort_values(by = ['date'],
                  ascending = False,
                  )
     .groupby('ticker')
     .agg({key: 'first' for key in clean_cols})
     .drop_duplicates()
     .reset_index()
     .to_csv('watchlist.csv', index = False)
     )
    
    return 

def get_status_message(ticker: str,
                       vol_ratio: float,
                       price_gap: float,
                       status: int,
                       price: float,
                       low: float,
                       lines: str) -> Tuple[str, int]:
    '''
    Once a breakout occurs, use a switch case to send out a message depending
    on the volume traded so far.

    Parameters
    ----------
    ticker : str
        The ticker for the stock
    vol_ratio : float
        The ratio of the average volume, to the volume traded today
    price_gap : float
        The percentage the breakout price is above the watch price
    status : int
        The current status flag for the ticker
    price : float
        The current stock price
    low : float
        The current low of the day
    lines : str
        A set of dashes to end the message with

    Returns
    -------
    msg, new_status : Tuple[str, int]
        The message to print and new status for the ticker
    '''
    
    base_msg = (
        ticker + ' has broken out with ' + str(vol_ratio) +  'x average volume'
    )
    price_msg = 'The price is ' + str(price_gap) + '% above the watching price'
    lod_msg = (
        'Current low : ' + str(round(low, 2)) + ' (' + 
        str(round(100*(price/low-1), 2)) + '%)'
    )
                
    if status == 0 and vol_ratio < 0.5:
        new_status = 1
        vol_msg = 'Perhaps worth waiting?'
    elif status <= 1 and vol_ratio > 0.5 and vol_ratio < 1:
        new_status = 2
        vol_msg = 'Perhaps worth considering?'
    elif status <= 2 and vol_ratio > 1 and vol_ratio < 1.5:
        new_status = 3
        vol_msg = 'Woah, bigger than average volume! Buy now or remain poor.'
    elif status <= 3 and vol_ratio > 1.5:
        new_status = 4
        vol_msg = 'Holy shit, that is some serious volume...'
    else:
        vol_msg = ''
        new_status = status
        
    msg = (
        base_msg + '\n' +
        price_msg + '\n' + 
        vol_msg + '\n' +
        lod_msg + 
        lines
    )
    
    return msg, new_status