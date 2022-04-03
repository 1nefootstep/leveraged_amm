from brownie import accounts, config, Token, LevCPAMM, network
from scripts.helpers import get_account


def token_approvals():
    account = get_account()
    amm = LevCPAMM[-1]
    token0 = Token[-2]
    token1 = Token[-1]
    token0.approve(amm, 1e21, {"from": account})
    token1.approve(amm, 1e21, {"from": account})


def add_liquid(token0_amt=1e14, token1_amt=1e15):
    account = get_account()
    amm = LevCPAMM[-1]
    amm.addLiquidity(token0_amt, token1_amt, {"from": account})


def main():
    token0_amount = 1e14
    token1_amount = 1e15
    print(f"approving amm for token 0 and token 1...")
    token_approvals()
    print(f"adding {token0_amount}/{token1_amount} liquidity...")
    add_liquid()
