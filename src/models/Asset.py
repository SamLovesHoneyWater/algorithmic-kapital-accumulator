from .data_types import *
from collections.abc import Callable

# Asset object, instantiate one for each asset. Do not create duplicate instantiations for the same asset.
class Asset(object):
    def __init__(self, asset_type: AssetType, asset_name: str, quote_fn: Callable[[str], tuple[Price, Price]]):
        self.asset_type = asset_type
        self.asset_name = asset_name
        self.quote_fn = quote_fn  # Function that gets the best current bid/ask for a given asset name
    def get_quote(self) -> tuple[Price, Price]:
        return self.quote_fn(self.asset_name)

if __name__ == '__main__':
    def get_toy_price(asset_name):
        return Price(12.1), Price(12.2)

    lyft = Asset(AssetType.stock, "LYFT", get_toy_price)
    print(lyft.get_quote())
