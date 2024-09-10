from .data_types import *
from .Asset import Asset

# Custom Order object, instantiate for each order submitted.
# Note: this is different from the Order type of the Alpaca SDK object
class Order(object):
    def __init__(self, asset: Asset, order_side: OrderSide, order_type: OrderType, quantity: Quantity, unit_price: Price | None, created_at: datetime):
        self.asset = asset
        self.order_side = order_side  # BUY | SELL
        self.order_type = order_type  # LIMIT | MARKET | ...
        self.quantity = quantity
        if unit_price is not None:
            self.unit_price = round(unit_price, 2)
        self.created_at = created_at
    
    def __str__(self):
        return f"Order({self.asset.asset_name}, {self.order_side}, {self.order_type}, {self.quantity}, {self.unit_price}, {self.created_at})"
    
    def __repr__(self):
        return str(self)

if __name__ == '__main__':
    def get_toy_price(symbol):
        if symbol == "LYFT":
            return Price(12.1), Price(12.2)
        else:
            raise ValueError("Invalid symbol")

    lyft = Asset(AssetType.stock, "LYFT", get_toy_price)
    print(lyft.get_quote())
    order = Order(lyft, OrderSide.BUY, OrderType.LIMIT, Quantity(100), Price(12.1), datetime.now())
    print(order)
        