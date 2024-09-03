from typing import NewType
from enum import Enum

class AssetType(Enum):
    equity = 'equity'
    option = 'option'
    savings = 'savings'
