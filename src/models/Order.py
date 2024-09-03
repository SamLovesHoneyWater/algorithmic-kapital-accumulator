from .data_types import *
from .Asset import Asset

class Order(object):
    def __init__(self, asset: Asset, order_type: OrderType, quantity: Quantity, unit_price: Price, created_at: datetime):
        self.asset = asset
        self.order_type = order_type
        self.quantity = quantity
        self.unit_price = unit_price
        self.created_at = created_at

if __name__ == '__main__':
    def get_toy_price(ticker):
        if ticker == "LYFT":
            return Price(12.1), Price(12.2)
        else:
            raise ValueError("Invalid ticker")

    lyft = Asset(AssetType.equity, "LYFT", get_toy_price)
    print(lyft.get_quote())
    order = Order(lyft, OrderType.LIMIT, Quantity(100), Price(12.1), datetime.now())
    print(order)
        