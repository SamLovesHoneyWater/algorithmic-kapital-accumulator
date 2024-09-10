from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    GetAssetsRequest, 
    MarketOrderRequest, 
    LimitOrderRequest, 
    StopOrderRequest, 
    StopLimitOrderRequest, 
    TakeProfitRequest, 
    StopLossRequest, 
    TrailingStopOrderRequest, 
    GetOrdersRequest, 
    ClosePositionRequest
)
from alpaca.trading.enums import (
    TimeInForce, 
    OrderClass
)

from .data_types import *
from .Investor import Investor
from .Transaction import Transaction
from .Order import Order
from .HeldAsset import HeldAsset
from .Strategy import Strategy

# Brokerage Account object, instantiate one for each account. One owner can have multiple accounts.
class BrokerAccount(object):
    def __init__(self, brokerage_name: str, owner: Investor, algorithmic: bool,
                    secrets: dict | None = None, paper: bool = False,
                    transactions: list[Transaction] = [], strategies: list[Strategy] = [], tz: str = "America/New_York"):
        self.brokerage_name = brokerage_name
        self.owner = owner
        self.algorithmic = algorithmic
        self.secrets = secrets
        self.paper = paper
        self.transactions = transactions
        self.strategies = strategies
        self.tz = tz  # Timezone, default EST
        self.trade_client: TradingClient | None = None
        if brokerage_name == "Alpaca":
            if secrets is None:
                raise ValueError(f"Alpaca account requires secrets, got {secrets}")
            else:
                self.trade_client = TradingClient(api_key=secrets["key"], secret_key=secrets["secret"], paper=paper)

    def submit_order(self, order: Order) -> None:
        if not self.algorithmic:
            raise Exception(f"Cannot submit order to non-algorithmic broker '{self.brokerage_name}', account owner: {self.owner.investor_name}.")
        elif self.trade_client is None:
            raise Exception(f"Cannot submit order: trading client not found for account at broker '{self.brokerage_name}'.")
        if self.brokerage_name == "Alpaca":
            req: MarketOrderRequest | LimitOrderRequest
            if order.order_type == OrderType.LIMIT:
                req = LimitOrderRequest(
                    symbol = order.asset.asset_name,
                    qty = order.quantity,
                    side = order.order_side,
                    type = order.order_type,
                    time_in_force = TimeInForce.DAY,
                    limit_price = order.unit_price
                )
            elif order.order_type == OrderType.MARKET:
                req = MarketOrderRequest(
                    symbol = order.asset.asset_name,
                    qty = order.quantity,
                    side = order.order_side,
                    type = order.order_type,
                    time_in_force = TimeInForce.DAY,
                )
            else:
                raise NotImplementedError(f"Unsupported order type: {order.order_type}")
            res = self.trade_client.submit_order(req)
        else:
            raise ValueError(f"Cannot submit order to unrecognized algorithmic broker '{self.brokerage_name}'.")
        return

    def get_total_liquidable_value(self) -> Capital:
        raise NotImplementedError
    def get_actions(self) -> list[Order]:
        raise NotImplementedError
    def get_active_orders(self) -> list[Order]:
        raise NotImplementedError
    def get_held_assets(self) -> list[HeldAsset]:
        raise NotImplementedError

if __name__ == '__main__':
    me = Investor("Sam H")
    acc = BrokerAccount("Alpaca", me, True)
