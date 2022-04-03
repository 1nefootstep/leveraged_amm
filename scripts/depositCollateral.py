from brownie import accounts, config, Token, LevCPAMM, network
from scripts.helpers import get_account


def deposit_collateral(amount = 10000):
    account = get_account()
    amm = LevCPAMM[-1]
    amm.addCollateral(amount, {"from": account})
    

def main():
    deposit_collateral()
