from .data_types import *
from .Asset import Asset
from .Transaction import Transaction

# Held Asset object, not used
class HeldAsset(object):
    def __init__(self, asset: Asset, quantity: Quantity, transactions: list[Transaction] = []):
        self.asset = asset
        self.quantity = quantity
        self.transactions = transactions
        raise NotImplementedError("No use for HeldAsset object for now.")
