from brownie import accounts, config, Token, LevCPAMM, network
from scripts.helpers import get_account

def deploy_token(name, ticker, decimals, supply):
    account = get_account()
    token = Token.deploy(name, ticker, decimals, supply, {"from": account})
    
    return token

def deploy_amm(token0, token1, collateral_token, max_leverage):
    account = get_account()
    token = LevCPAMM.deploy(token0, token1, collateral_token, max_leverage, {"from": account})
    
    return token


def main():
    print(f'Deploying wrapped ether contract...')
    weth_addr = deploy_token("Wrapped Ether", "WETH", 18, 1e21)
    print(f'Deployed wrapped ether contract!')
    print(f'Deploying usd coin contract...')
    usdc_addr = deploy_token("USD Coin", "USDC", 18, 1e21)
    print(f'Deployed usd coin contract!')
    print(f'Deploying leverage amm contract...')
    amm_addr = deploy_amm(weth_addr, usdc_addr, usdc_addr, 10000)
    print(f'Deployed!')
