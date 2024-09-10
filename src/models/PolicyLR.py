import numpy as np
from sklearn.linear_model import LinearRegression # type: ignore  # Ignore type becuse mypy does not have a signature for the module
import matplotlib.pyplot as plt
from zoneinfo import ZoneInfo
from datetime import timedelta

from .data_types import *

from .BrokerAccount import BrokerAccount
from .Asset import Asset
from .Order import Order

# Market making with linear regression
class PolicyLR(object):
    def __init__(self, broker_account: BrokerAccount, asset: Asset, market_make_err: Price, market_make_exit: Price , data_quotes: DataFrame):
        self.broker_account = broker_account
        self.asset = asset
        assert asset.asset_type == AssetType.stock  # Only support stock for now
        self.symbol = asset.asset_name
        self.market_make_err = market_make_err  # Price deviation (from price prediction) that we think we can profit from
        self.market_make_exit = market_make_exit  # Price deviation at which we will NOT trade because the deviation is too large
        self.length = len(data_quotes)  # Number of data points
        tzinfo = ZoneInfo(broker_account.tz)
        self.start_time = data_quotes.index[0][1].astimezone(tzinfo)  # Timestamp of first data point
        self.end_time = data_quotes.index[-1][1].astimezone(tzinfo)  # Timestamp of last data point

        self.get_linear_fit(data_quotes)  # Get model

    # Produce a linear model that fits the data
    def get_linear_fit(self, data_quotes: DataFrame):
        X_time = data_quotes.index.values
        X = np.arange(0, self.length).reshape(-1, 1)
        y = np.array(data_quotes["vwap"].values)  # We predict "Volume-weighted average price"

        self.model = LinearRegression()
        self.model.fit(X, y)

        # Predict near future
        X_extend = np.arange(0, self.length * 1.5).reshape(-1, 1)
        y_pred = self.model.predict(X_extend)

        # Visualize the model for human inspection
        self.graph_prediction(y, y_pred)
        self.graph_distribution(y, y_pred)
        plt.show()

    # Given an array of times, predict prices at those times
    def predict(self, X: NDArray) -> NDArray:
        y_pred = self.model.predict(X)
        return y_pred

    # Graph historical prices and future predictions
    def graph_prediction(self, y: NDArray, y_pred: NDArray):
        plt.figure(figsize=(13, 7))
        X = np.arange(0, len(y)).reshape(-1, 1)
        X_pred = np.arange(0, len(y_pred)).reshape(-1, 1)
        plt.scatter(X, y, color='blue', label='Actual Prices')
        plt.plot(X_pred, y_pred, color='red', label='Predicted Prices')
        plt.xlabel('Time')
        plt.ylabel('mid Price')
        plt.title(f'{self.asset.asset_name} Stock Price Prediction from {self.start_time.replace(tzinfo=None)} to {self.end_time.replace(tzinfo=None)}')
        plt.legend()

    # Graph the distribution of the error between the actual and predicted prices (Looks like Gaussian = good)
    def graph_distribution(self, y: NDArray, y_pred: NDArray):
        plt.figure(figsize=(13, 7))
        plt.hist(y - y_pred[:len(y)], bins=30, color='blue', alpha=0.5, label='delta')
        plt.xlabel('error')
        plt.ylabel('Frequency')
        plt.title(f'{self.asset.asset_name} Stock Price Distribution')
        plt.legend()
    
    # Generate market-making orders
    def market_make(self) -> list[Order]:
        order_size = 10
        bid, ask = self.asset.get_quote()
        cur_time = datetime.now(ZoneInfo(self.broker_account.tz))
        time_frame = timedelta(days=1)
        time_difference = cur_time - self.end_time
        if time_difference > time_frame:
            raise Exception("Data is too old") # Do not trade if the data is too old
        price_pred = self.predict(np.array([[self.length]]))[0]
        if ask < price_pred - self.market_make_exit:
            ask_order = Order(self.asset, OrderSide.SELL, OrderType.MARKET, Quantity(order_size), bid, cur_time)
            return [ask_order]  # The price is too low, sell to prevent further loss
        elif bid > price_pred + self.market_make_exit:
            return []  # We do not understand why the price is so high, do not trade
        else:
            # Price is within range, make a market
            our_bid = Price(price_pred - self.market_make_err)  # Price to buy
            our_ask = Price(price_pred + self.market_make_err)  # Price to sell
            bid_order = Order(self.asset, OrderSide.BUY, OrderType.LIMIT, Quantity(order_size), our_bid, cur_time)
            ask_order = Order(self.asset, OrderSide.SELL, OrderType.LIMIT, Quantity(order_size), our_ask, cur_time)
            return [bid_order, ask_order]
