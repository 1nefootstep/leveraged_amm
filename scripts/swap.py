from brownie import accounts, config, Token, LevCPAMM, network
from scripts.helpers import get_account


def swap(token = Token[-2], amount = 10000):
    account = get_account()
    amm = LevCPAMM[-1]
    amm.swap(token, amount, {"from": account})
    

def main():
    swap()
