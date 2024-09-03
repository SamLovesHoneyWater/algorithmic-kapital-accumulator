from .data_types import *
from .Order import Order
from .HeldAsset import HeldAsset
from .Transaction import Transaction
from .Asset import Asset

from . import BrokerAccount

class Strategy(object):
    def __init__(self, strategy_name: str, account: 'BrokerAccount.BrokerAccount', targets: list[Asset],
                    active_orders: list[Order] = [], transactions: list[Transaction] = [], held_assets: list[HeldAsset] = []):
        self.strategy_name = strategy_name
        self.account = account
        self.targets = targets
        self.active_orders = active_orders
        self.transactions = transactions
        self.held_assets = held_assets
    def get_actions(self) -> list[Order]:
        raise NotImplementedError
