from .data_types import *
from .Order import Order

# Transaction object, not used
class Transaction(object):
    def __init__(self, order: Order, strategy_name: str, unit_price: Price | None, fulfilled_at: datetime | None):
        self.order = order
        self.strategy_name = strategy_name
        if order.unit_price is None and unit_price is not None:
            self.order.unit_price = unit_price
        elif order.unit_price is not None and unit_price is None:
            pass
        else:
            assert order.unit_price == unit_price, "unit_price for transaction must match order.unit_price"
        self.fulfilled_at = fulfilled_at
        raise NotImplementedError("No use for Transaction object for now.")