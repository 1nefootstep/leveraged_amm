from brownie import accounts, config, Token, LevCPAMM, network
from scripts.helpers import get_account


def withdraw_collateral(amount = 10000):
    account = get_account()
    amm = LevCPAMM[-1]
    amm.removeCollateral(amount, {"from": account})
    

def main():
    withdraw_collateral()
