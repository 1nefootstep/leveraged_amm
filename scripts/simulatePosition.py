from brownie import accounts, config, Token, LevCPAMM, network
from scripts.helpers import get_account

def simulatePosition(amount = 10000, leverage = 7000):
    account = get_account()
    amm = LevCPAMM[-1]
    
    print(amm.simulatePositionAddedInOtherToken(amount, leverage))
    

def main():
    simulatePosition()
