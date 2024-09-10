from alpaca.data.live.stock import StockDataStream
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import (
    StockBarsRequest,
    StockTradesRequest,
    StockQuotesRequest
)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import json, os
import numpy as np
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Import objects and types
from models import *

# Get broker secrets from environment variables
alpaca_api_key = os.environ.get("ALPACA_API_KEY")
alpaca_api_secret = os.environ.get("ALPACA_API_SECRET")
alpaca_paper_key = os.environ.get("ALPACA_PAPER_KEY")
alpaca_paper_secret = os.environ.get("ALPACA_PAPER_SECRET")

# Initialize important objects
me = Investor("Sam H")
live_acc = BrokerAccount("Alpaca", me, True, secrets={"key": alpaca_api_key, "secret": alpaca_api_secret}, paper=False)
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

# Initialize the asset(s) we want to trade with
symbol = "QQQ"
asset = Asset(AssetType.stock, symbol, get_stock_quote)

now = datetime.now(ZoneInfo("America/New_York"))
print(f"Current time: {now.replace(tzinfo=None)}")

# Get historical market data
req = StockBarsRequest(
    symbol_or_symbols = [symbol],
    timeframe=TimeFrame(amount = 15, unit = TimeFrameUnit.Minute), # specify timeframe
    start = now - timedelta(days = 20),                          # specify start datetime, default=the beginning of the current day.
    # end_date=None,                                        # specify end datetime, default=now
    #limit = 2,                                               # specify limit
)
data_quotes: DataFrame
data_quotes = stock_historical_data_client.get_stock_bars(req).df # type: ignore  # Ignore type because mypy records a wrong signature for the method.
print(f"Got historical quotes data with shape {data_quotes.shape}")

# Initialize policy
market_make_err = Price(2.5)
market_make_exit = Price(6.)
pi = PolicyLR(paper_acc, asset, market_make_err, market_make_exit, data_quotes)

# Generate orders according to algorithm
orders = pi.market_make()
print(f"Got {symbol} orders: {orders}")

#for order in orders:
#    paper_acc.submit_order(order)
