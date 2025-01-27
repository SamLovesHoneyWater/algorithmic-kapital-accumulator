from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import (
    StockQuotesRequest
)
import os, time
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
import logging
from dotenv import load_dotenv

from typing import cast

# Import objects and types
from models import *
from utils import *
from data_feed import get_live_data
from printing_logger import myLogger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='deployment.log',  # Log file name
    filemode='a'         # Append mode (default is 'a', for append)
)
base_logger = logging.getLogger(__name__)
logger = myLogger(base_logger, "warning")
logger.info("\n\n\n\nStarting new run...\n\tFile:\tdeployment.py\n\tTime (ET):\t" + str(datetime.now(ZoneInfo("America/New_York"))) + "\n\n")

# Access environment variables as if they came from the actual environment
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

alpaca_api_key = os.environ.get("ALPACA_API_KEY")
alpaca_api_secret = os.environ.get("ALPACA_API_SECRET")
alpaca_paper_key = os.environ.get("ALPACA_PAPER_KEY")
alpaca_paper_secret = os.environ.get("ALPACA_PAPER_SECRET")

# Initialize important objects
me = Investor("Sam H")
#live_acc = BrokerAccount("Alpaca", me, True, secrets={"key": alpaca_api_key, "secret": alpaca_api_secret}, paper=False)
paper_acc = BrokerAccount("Alpaca", me, True, secrets={"key": alpaca_paper_key, "secret": alpaca_paper_secret}, paper=True)
stock_historical_data_client = StockHistoricalDataClient(alpaca_paper_key, alpaca_paper_secret, url_override=None)


# quote_fn for stock type assets. See Asset.py
def get_stock_quote(symbol):
    req = StockQuotesRequest(
        symbol_or_symbols = [symbol],
    )
    res = stock_historical_data_client.get_stock_latest_quote(req)
    data = res[symbol]
    return Price(data.bid_price), Price(data.ask_price)

now = datetime.now(ZoneInfo("America/New_York"))
print(f"Current time: {now.replace(tzinfo=None)}")

# Initialize the asset(s) we want to trade with
symbols = ["META", "IBM", "TSLA", "MSFT"]
assets = {symbol: Asset(AssetType.stock, symbol, get_stock_quote) for symbol in symbols}
print(symbols)

principle = 1000
per_stock_quota = principle / len(symbols)

saved_45 = False
bought = []
sold = []
timestamps = []
close_prices: dict[str, float | None] = {}
data: dict[str, list[float | None]] = {}
quantity_bought: dict[str, float] = {}
highest_prices: dict[str, float] = {}
for symbol in symbols:
    data[symbol] = []
    close_prices[symbol] = None
    quantity_bought[symbol] = 0
    highest_prices[symbol] = 0

test_symbol = "META"
assert test_symbol in symbols
logger.info(f"Starting trading with principle {principle} and per stock quota {per_stock_quota}")
logger.info(f"Testing buying {test_symbol}")
order = Order(assets[test_symbol], OrderSide.BUY, OrderType.LIMIT, Quantity(3//2), Price(100), datetime.now(ZoneInfo("America/New_York")))
paper_acc.submit_order(order)
'''
time.sleep(15)
logger.info(f"Testing selling {test_symbol}")
order = Order(assets[test_symbol], OrderSide.SELL, OrderType.LIMIT, Quantity(3//2), Price(1), datetime.now(ZoneInfo("America/New_York")))
live_acc.submit_order(order)
'''

logger.warning("Remember to turn on extended_hours in BrokerAccount.py")
logger.warning("Remember to change the time of closing price from 9:29 to 15:59")

while True:
    # Get live data for the symbols
    try:
        live_data = get_live_data(symbols)
    except Exception as e:
        logger.error(f"Failed to get live data: {e}")
        time.sleep(0.02)
        continue
    
    # Check parsing success rate of OCR data
    ticker_err_rate = sum([not success for success, _ in live_data]) / len(live_data)
    price_err_rate = sum([price is None for _, price in live_data]) / len(live_data)
    if ticker_err_rate > .9 or price_err_rate > 0.3:
        logger.warning(f"OCR error rate too high: {ticker_err_rate, price_err_rate}")
        time.sleep(0.02)
        continue
    
    timestamp = datetime.now(ZoneInfo("America/New_York"))
    orders = []
    logger.info(f"Got live data: {live_data}")
    for symbol, price in live_data:
        if symbol is not None:
            # Update data
            data[symbol].append(price)

            # Only buy 9:30 - 10:00 and 16:00 - 16:30
            if not ((timestamp.hour == 9 and timestamp.minute >= 30 and timestamp.minute <= 60) or 
                (timestamp.hour == 16 and timestamp.minute >= 0 and timestamp.minute <= 30)):
                continue

            # Don't buy if already sold
            if symbol in sold:
                continue

            # Buy if signal is strong
            close_price: float | None = close_prices[symbol]
            if price is not None and close_price is not None:
                if not (symbol in bought) and price > float(close_price) * 1.008:
                    buy_quantity = per_stock_quota // price
                    logger.info(f"Buying {symbol} at {price}")
                    try:
                        orders.append(Order(assets[symbol], OrderSide.BUY, OrderType.LIMIT, Quantity(buy_quantity), Price(price * 1.4), datetime.now(ZoneInfo("America/New_York"))))
                        bought.append(symbol)
                        quantity_bought[symbol] = buy_quantity
                    except Exception as e:
                        logger.error(f"Failed to buy {symbol}: {e}")
                elif symbol in bought and not (symbol in sold):
                    # Update highest price
                    highest_prices[symbol] = max(highest_prices[symbol], price)

                    # Stop loss if price is lower than closing price
                    if price < float(close_price) * 0.992:
                        logger.info(f"Selling {symbol} at {price}, triggered stop loss")
                        sell_quantity = quantity_bought[symbol]
                        try:
                            orders.append(Order(assets[symbol], OrderSide.SELL, OrderType.LIMIT, Quantity(sell_quantity), Price(price * 0.6), datetime.now(ZoneInfo("America/New_York"))))
                            sold.append(symbol)
                        except Exception as e:
                            logger.error(f"Failed to sell {symbol}: {e}")

                    # Trailing stop: sell if price is 1% lower than highest price since bought
                    if price < highest_prices[symbol] * .988:
                        logger.info(f"Selling {symbol} at {price}, triggered by trailing stop")
                        sell_quantity = quantity_bought[symbol]
                        try:
                            orders.append(Order(assets[symbol], OrderSide.SELL, OrderType.LIMIT, Quantity(sell_quantity), Price(price * 0.6), datetime.now(ZoneInfo("America/New_York"))))
                            sold.append(symbol)
                        except Exception as e:
                            logger.error(f"Failed to sell {symbol}: {e}")

    timestamps.append(timestamp)

    for order in orders:
        try:
            paper_acc.submit_order(order)
        except Exception as e:
            logger.error(f"Failed to submit order: {e}")

    # Save the price as closing price at 15:59:55
    if timestamp.hour == 15 and timestamp.minute == 59 and 53 <= timestamp.second <= 57:
    #if timestamp.hour == 9 and timestamp.minute == 29 and 53 <= timestamp.second <= 57:
        for symbol in symbols:
            if close_prices[symbol] is not None:
                continue
            window = 30
            if len(data[symbol]) >= window:
                window_data = cast(list[float], data[symbol][-window:])
                if None not in window_data:
                    avg_price = np.mean(window_data)
                    close_prices[symbol] = float(avg_price)
            elif len(data[symbol]) > 0:
                close_prices[symbol] = data[symbol][-1]
            if close_prices[symbol] is None:
                logger.warning(f"Failed to get closing price for {symbol}, using None")
        logger.info(f"Closing prices at the end of the previous market stage are: {close_prices}")

    if timestamp.minute == 45 and not saved_45:
        try:
            df = pd.DataFrame({(symbol, "price"): prices for symbol, prices in data.items()}, index=timestamps)
            df.to_csv('data.csv', mode='a')
            saved_45 = True
            # Clear data train
            for symbol in symbols:
                data[symbol] = []
            timestamps = []
            logger.info("Successfully saved data")
        except Exception as e:
            logger.error(f"Failed to save data, encountered an error: {e}")
    elif saved_45 and timestamp.minute == 50:
        saved_45 = False  # This flag prevents saving the data multiple times

