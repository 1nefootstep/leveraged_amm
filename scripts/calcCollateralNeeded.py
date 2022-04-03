from brownie import accounts, config, Token, LevCPAMM, network
from scripts.helpers import get_account

def calcCollateralNeeded(amount = 1000, leverage = 7000):
    account = get_account()
    amm = LevCPAMM[-1]
    
    print(amm.calculateCollateralNeeded(amount, leverage))
    

def main():
    calcCollateralNeeded()
