from brownie import accounts, config, Token, LevCPAMM, network
from scripts.helpers import get_account

def remainingValue():
    account = get_account()
    amm = LevCPAMM[-1]
    
    print(amm.remainingPositionOf(account))
    

def main():
    remainingValue()
