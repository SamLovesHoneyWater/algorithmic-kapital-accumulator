# Custom enum types for typing

from typing import NewType
from enum import Enum

# Used to denominate type of asset. Currently only type "stock" is in use
class AssetType(Enum):
    stock = 'stock'
    option = 'option'
    savings = 'savings'
