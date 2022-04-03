#!/usr/bin/python3

import pytest


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass


@pytest.fixture(scope="module")
def token0(Token, accounts):
    return Token.deploy("Wrapped ETH", "WETH", 18, 1e21, {"from": accounts[0]})


@pytest.fixture(scope="module")
def token1(Token, accounts):
    return Token.deploy("USD Coin", "USDC", 18, 1e21, {"from": accounts[0]})


@pytest.fixture(scope="module")
def amm(CPAMM, token0, token1, accounts):
    # deploy AMM
    ammToReturn = CPAMM.deploy(token0, token1, {"from": accounts[0]})
    # add initial liquidity
    sender_balance0 = token0.balanceOf(accounts[0])
    amount0 = sender_balance0 // 4
    sender_balance1 = token1.balanceOf(accounts[0])
    amount1 = sender_balance1 // 4
    token0.approve(ammToReturn, amount0, {"from": accounts[0]})
    token1.approve(ammToReturn, amount1, {"from": accounts[0]})
    ammToReturn.addLiquidity(amount0, amount1)
    
    return ammToReturn
