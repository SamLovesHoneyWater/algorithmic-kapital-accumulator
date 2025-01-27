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
import matplotlib.pyplot as plt

# Import objects and types
from models import *
from utils import *

# Get broker secrets from environment variables
alpaca_api_key = os.environ.get("ALPACA_API_KEY")
alpaca_api_secret = os.environ.get("ALPACA_API_SECRET")
alpaca_paper_key = "PKC5JCNZ7WY5W2BA8BUY" #os.environ.get("ALPACA_PAPER_KEY")
alpaca_paper_secret = "t7wDZSy9QfhymvzxbfybZc4Gs6lcg0BdNC5fvKwX" #os.environ.get("ALPACA_PAPER_SECRET")
print(alpaca_paper_key, alpaca_paper_secret)

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
symbols = ["TSLA", "GOOGL", "NFLX", "F"]
#asset = Asset(AssetType.stock, symbol, get_stock_quote)
# Define custom start and end times for each symbol based on their earnings release dates
earnings_dates = {
    "TSLA": datetime(2024, 10, 23, tzinfo=ZoneInfo("America/New_York")),
    "GOOGL": datetime(2024, 10, 29, tzinfo=ZoneInfo("America/New_York")),
    "NFLX": datetime(2024, 10, 17, tzinfo=ZoneInfo("America/New_York")),
    "F": datetime(2024, 10, 28, tzinfo=ZoneInfo("America/New_York"))
}

for symbol in []:#["KALU", "ASGN", "SPR", "DB", "AMTB", "VLRS", "NLY", "T", "AMP"]:
    symbols.append(symbol)
    earnings_dates[symbol] = datetime(2024, 10, 23, tzinfo=ZoneInfo("America/New_York"))

res = []
#start_time = now - timedelta(days = 7)
#end_time = now
timeframe = 1
all_data = {}
buy_points = {}

for _, symbol in enumerate(symbols):
    buy_points[symbol] = []

    # Get the custom start and end times for the symbol
    start_time = earnings_dates[symbol] - timedelta(days=1)
    end_time = earnings_dates[symbol] + timedelta(days=1)

    # Get historical market data
    data_bars: DataFrame
    req_dict = {
        "req_type": "StockBarsRequest",
        "symbols": [symbol],
        "timeframe": TimeFrame(amount = timeframe, unit = TimeFrameUnit.Minute),
        "start": start_time,
        "end": end_time,
        "limit": None
    }
    req_hash = hash_dict(req_dict)
    cache = load_dataframe_from_cache(req_hash)
    if cache is not None:
        data_bars = cache
        print(f"INFO - Using data from cache for {symbol}")
    else:
        req_succeed = False
        print(f"INFO - Downloading historical bars data for {symbol}...")
        try:
            req = StockBarsRequest(
                symbol_or_symbols = req_dict["symbols"],
                timeframe = req_dict["timeframe"],
                start = req_dict["start"],
                end_date = req_dict["end"],
                limit = req_dict["limit"],
            )
            req_succeed = True
        except:
            print(f"WARNING - Failed to download historical bars data for {symbol}, skipping the asset.")
            continue
        if req_succeed:
            data_bars = stock_historical_data_client.get_stock_bars(req).df # type: ignore  # Ignore type because mypy records a wrong signature for the method.
            data_bars.reset_index(level="symbol", drop=True, inplace=True)
            data_bars['timestamp'] = data_bars.index
            data_bars.index = range(len(data_bars))
            save_dataframe_to_cache(data_bars, req_hash)
            data_bars = load_dataframe_from_cache(req_hash)
    print(f"INFO - Got historical quotes data with shape {data_bars.shape}")
    
    data_bars.rename(columns={'close': 'price'}, inplace=True)
    data = data_bars[['timestamp', 'price']]
    #data['ma'] = data['price'].rolling(window=5).mean()
    
    X_time = data["timestamp"].values
    y = np.array(data["price"].values)

    stock = 0
    capital = 100
    cur_price = data.iloc[-1]['price']
    print(f"INFO - Simulating trading for {symbol}")
    for i in range(1, len(data)):
        cur_price = data.iloc[i]['price']
        prev_price_1m = data.iloc[i-1]['price']
        prev_price_4m = data.iloc[i-4]['price'] if i >= 4 else prev_price_1m

        pct_change_1m = (cur_price - prev_price_1m) / prev_price_1m * 100
        pct_change_4m = (cur_price - prev_price_4m) / prev_price_4m * 100

        if stock == 0 and (pct_change_1m >= 0.5 or pct_change_4m >= 99.):
            buy_points[symbol].append((data.iloc[i]['timestamp'], cur_price))
            stock = capital / cur_price
            capital = 0
    
    if stock > 0:
        price = Price(cur_price)
        capital = stock * price
        stock = 0
    
    print(f"INFO - Capital after trading {symbol}: {capital}")
    res.append(round(float(capital - 100), 2))
    print()

    all_data[symbol] = data
    do_display = False
    if do_display:
        plt.figure(figsize=(14, 7))
        plt.plot(data['timestamp'], data['price'], label='Price')
        plt.xlabel('Timestamp')
        plt.ylabel('Value')
        plt.title(f'{symbol} Stock Price')
        plt.legend()
        plt.grid(True)
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(nbins=10))
        plt.xticks(rotation=45)
        plt.tight_layout()

        for point in buy_points[symbol]:
            plt.plot(point[0], point[1], 'ro', markersize=10)

        plt.show()
        
avg_gain = sum(res) / len(res)
print(f"Average gain across all symbols: {avg_gain:.2f}%")

num_rows = (len(symbols) + 2) // 3  # Calculate number of rows needed (3 plots per row)
fig, axes = plt.subplots(num_rows, 3, figsize=(20, 10*num_rows))
axes = axes.flatten()  # Flatten 2D array of axes into 1D

for i, symbol in enumerate(symbols):
    if symbol not in all_data.keys():
        continue
    axes[i].plot(all_data[symbol]['timestamp'], all_data[symbol]['price'], label='Price')
    axes[i].set_xlabel('Timestamp')
    axes[i].set_ylabel('Value')
    axes[i].set_title(f'{symbol} Stock Price')
    axes[i].text(0.02, 0.98, f'Net Gain: {res[i]}%', transform=axes[i].transAxes, verticalalignment='top', fontsize=10)
    axes[i].legend()
    axes[i].grid(True)
    axes[i].xaxis.set_major_locator(plt.MaxNLocator(nbins=5))
    axes[i].tick_params(axis='x', rotation=45)
    
    for point in buy_points[symbol]:
        axes[i].plot(point[0], point[1], 'ro', markersize=10)

# Hide any unused subplots
for j in range(i+1, len(axes)):
    axes[j].set_visible(False)

plt.subplots_adjust(hspace=0.5, wspace=0.3)
#plt.tight_layout()
plt.show()
