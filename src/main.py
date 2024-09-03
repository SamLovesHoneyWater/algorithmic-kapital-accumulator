from models import *

me = Investor("Sam H")
acc = BrokerAccount("Alpaca", me, True)

def get_toy_quote(ticker: str) -> tuple[Price, Price]:
    if ticker == "LYFT":
        return Price(12.1), Price(12.2)
    elif ticker == "UBER":
        return Price(68.9), Price(69.2)
    else:
        raise ValueError("Invalid ticker")

const_strat = Strategy("Const", acc, [Asset(AssetType.equity, "LYFT", get_toy_quote), Asset(AssetType.equity, "UBER", get_toy_quote)])
acc.strategies.append(const_strat)
