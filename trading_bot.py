import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from alpaca_trade_api.rest import REST, TimeFrame
from alpaca_trade_api import AsyncRest
import requests
import pandas as pd
import alpaca_trade_api as tradeapi
import talib
import time
import datetime
import pytz
import yfinance as yf
from alpaca_trade_api.rest import APIError

load_dotenv("api.env")

API_KEY = os.environ.get('APCA_API_KEY_ID')
SECRET_KEY = os.environ.get('APCA_API_SECRET_KEY')
BASE_URL = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(API_KEY, SECRET_KEY, base_url=BASE_URL)

SYMBOLS = ['AAPL', 'MSFT', 'NVDA', 'AMD', 'JNJ', 'PFE', 'MRK', 'MRNA', 'JPM', 'BAC', 'GS', 'HOOD', 'AMZN', 'HD', 'TSLA', 'GME', 'XOM', 'CVX', 'COP', 'PLUG']
RSI_PERIOD = 14
RSI_BUY_THRESHOLD = 32
RSI_SELL_THRESHOLD = 65
STOP_LOSS_THRESHOLD = 0.985


def fetch_stock_data(symbol):
    stock = yf.Ticker(symbol)
    stock_data = stock.history(interval='1m', period='7d')
    stock_data.sort_index(inplace=True)
    #print(stock_data)
    return stock_data


def calculate_rsi(data, period):
    close_prices = data['Close'].values
    rsi = talib.RSI(close_prices, timeperiod=period)
    return rsi[-1]


def buy_stock(symbol, quantity):
    try:
        api.submit_order(
            symbol=symbol,
            qty=quantity,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
    except Exception as e:
        print(f'Greška prilikom kupovine: {e}')


def sell_stock(symbol, quantity):
    try:
        api.submit_order(
            symbol=symbol,
            qty=quantity,
            side='sell',
            type='market',
            time_in_force='gtc'
        )
    except Exception as e:
        print(f'Greška prilikom prodaje: {e}')


def is_market_open():
    try:
        clock = api.get_clock()
        return clock.is_open
    except requests.exceptions.ConnectionError as e:
        print(f'Greška u vezi s API-jem: {e}')
        return False


def sell_all_positions():
    positions = api.list_positions()
    for position in positions:
        api.submit_order(
            symbol=position.symbol,
            qty=position.qty,
            side='sell',
            type='market',
            time_in_force='gtc'
        )

def check_time_and_sell():
    now = datetime.datetime.now(pytz.timezone('America/New_York'))
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    time_left = market_close - now

    if time_left <= datetime.timedelta(minutes=5):
        sell_all_positions()
        return True
    return False

def check_stop_loss(position):
    current_price = float(position.current_price)
    avg_entry_price = float(position.avg_entry_price)

    if current_price / avg_entry_price <= STOP_LOSS_THRESHOLD:
        sell_stock(position.symbol, position.qty)
        print("Aktiviran je stop-loss, prodajem dionice.")
        return True
    return False

if __name__ == '__main__':
    while True:
        if not is_market_open():
            print("Tržište je zatvoreno, čekam...")
            time.sleep(60)
            continue

        for SYMBOL in SYMBOLS:
            stock_data = fetch_stock_data(SYMBOL)
            rsi = calculate_rsi(stock_data, RSI_PERIOD)
            print(f'RSI za {SYMBOL}: {rsi}')

            position = None
            try:
                position = api.get_position(SYMBOL)
            except APIError as e:
                if 'position does not exist' not in str(e):
                    print(f'Greška prilikom dohvaćanja pozicije: {e}')

            if rsi <= RSI_BUY_THRESHOLD and position is None:
                print(f"Kupujem dionice {SYMBOL}.")
                buy_stock(SYMBOL, 1)
            elif rsi >= RSI_SELL_THRESHOLD and position is not None:
                print(f"Prodajem dionice {SYMBOL}.")
                sell_stock(SYMBOL, position.qty)
            if position is not None and check_stop_loss(position):
                print("Stop-loss aktiviran.")

        for i in range(60, 0, -1):
            print(f"\rSljedeća provjera za sve dionice za {i} sekundi.", end='', flush=True)
            time.sleep(1)
        print()
        if check_time_and_sell():
            print("Tržište se zatvara za 5 minuta, prodajem sve pozicije.")
            break



