from brownie import accounts, config, Token, LevCPAMM, network
from scripts.helpers import get_account

# actual leverage is divided by 1000 for decimals
def addPosition(amount = 500, leverage = 8000):
    account = get_account()
    amm = LevCPAMM[-1]
    amt_in_other_pair = amm.simulatePositionAddedInOtherToken(amount, leverage)
    
    amm.addPosition(amt_in_other_pair, {"from": account})
    

def main():
    addPosition()
