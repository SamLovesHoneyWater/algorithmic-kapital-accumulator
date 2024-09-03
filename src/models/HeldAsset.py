from .data_types import *
from .Asset import Asset
from .Transaction import Transaction

class HeldAsset(object):
    def __init__(self, asset: Asset, quantity: Quantity, transactions: list[Transaction] = []):
        self.asset = asset
        self.quantity = quantity
        self.transactions = transactions
