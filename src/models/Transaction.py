from .data_types import *
from .Order import Order

class Transaction(object):
    def __init__(self, order: Order, strategy_name: str, fulfilled_at: datetime):
        self.order = order
        self.strategy_name = strategy_name
        self.fulfilled_at = fulfilled_at