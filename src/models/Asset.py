from .data_types import *
from collections.abc import Callable

class Asset(object):
    def __init__(self, asset_type: AssetType, asset_name: str, quote_fn: Callable[[str], tuple[Price, Price]]):
        self.asset_type = asset_type
        self.asset_name = asset_name
        self.quote_fn = quote_fn
    def get_quote(self) -> tuple[Price, Price]:
        return self.quote_fn(self.asset_name)

if __name__ == '__main__':
    def get_toy_price(asset_name):
        return Price(12.1), Price(12.2)

    lyft = Asset(AssetType.equity, "LYFT", get_toy_price)
    print(lyft.get_quote())
