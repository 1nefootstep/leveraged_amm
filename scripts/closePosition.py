from brownie import accounts, config, Token, LevCPAMM, network
from scripts.helpers import get_account

# this idx is the position id that is generated when a
# new position is created
# it increases monotonically by 1 on every new position
def closePosition(idx = 0):
    account = get_account()
    amm = LevCPAMM[-1]
    
    amm.closePosition(idx, {"from": account})
    

def main():
    closePosition()
