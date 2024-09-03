from .data_types import *
from .Investor import Investor
from .Transaction import Transaction
from .Order import Order
from .HeldAsset import HeldAsset
from .Strategy import Strategy

class BrokerAccount(object):
    def __init__(self, brokerage_name: str, owner: Investor, algorithmic: bool,
                    secrets: dict | None = None, transactions: list[Transaction] = [], strategies: list[Strategy] = []):
        self.brokerage_name = brokerage_name
        self.owner = owner
        self.algorithmic = algorithmic
        self.secrets = secrets
        self.transactions = transactions
        self.strategies = strategies
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
