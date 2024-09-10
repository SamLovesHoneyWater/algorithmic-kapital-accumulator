# Custom numeric types for typing, think of this as giving units to numbers

from typing import NewType

Capital = NewType('Capital', float)  # Type for dollars. E.g. Capital(30) stands for $30
Quantity = NewType('Quantity', float)  # Type for quantities. E.g. Quantity(5) could mean 5 shares of stock
Price = NewType('Price', float)  # Type for prices. Capital(x) / Quantity(y) = Price(x/y). Price(15) could mean $15/stock
