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


@pytest.fixture(scope="module", params=[0, 1])
def levAmm(LevCPAMM, token0, token1, accounts, request):
    # deploy AMM
    if (request.param == 1):
        ammToReturn = LevCPAMM.deploy(token0, token1, token1, 10000, {"from": accounts[0]})
    else:
        ammToReturn = LevCPAMM.deploy(token0, token1, token0, 10000, {"from": accounts[0]})
    # add initial liquidity
    sender_balance0 = token0.balanceOf(accounts[0])
    amount0 = 2.5e20
    sender_balance1 = token1.balanceOf(accounts[0])
    amount1 = 2.5e20
    token0.approve(ammToReturn, 1e21, {"from": accounts[0]})
    token1.approve(ammToReturn, 1e21, {"from": accounts[0]})
    ammToReturn.addLiquidity(amount0, amount1)

    return (ammToReturn, request.param)
