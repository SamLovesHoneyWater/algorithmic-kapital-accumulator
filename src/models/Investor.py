from .data_types import *

class Investor(object):
    def __init__(self, investor_name, accounts=[]):
        self.investor_name = investor_name
        self.accounts = accounts
    def get_total_liquidable_value(self) -> Capital:
        raise NotImplementedError

if __name__ == '__main__':
    me = Investor("Sam H")
