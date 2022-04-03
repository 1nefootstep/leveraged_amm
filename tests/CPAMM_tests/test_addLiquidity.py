#!/usr/bin/python3
import pytest
import brownie
import random


def test_add_liquidity_before_approval(token0, token1, amm, accounts):
    token0.transfer(accounts[1], 1e17, {"from": accounts[0]})
    token1.transfer(accounts[1], 1e17, {"from": accounts[0]})
    userBalance0 = token0.balanceOf(accounts[1])
    userBalance1 = token1.balanceOf(accounts[1])

    with brownie.reverts():
        amm.addLiquidity(userBalance0, userBalance1, {"from": accounts[1]})


def test_add_liquidity_more_than_approval(token0, token1, amm, accounts):
    token0.transfer(accounts[1], 1e17, {"from": accounts[0]})
    token1.transfer(accounts[1], 1e17, {"from": accounts[0]})
    userBalance0 = token0.balanceOf(accounts[1])
    userBalance1 = token1.balanceOf(accounts[1])
    token0.approve(amm, 1e16, {"from": accounts[1]})
    token1.approve(amm, 1e16, {"from": accounts[1]})

    with brownie.reverts():
        amm.addLiquidity(userBalance0, userBalance1, {"from": accounts[1]})


@pytest.mark.parametrize("run_num", range(1))
def test_add_single_sided_liquidity(token0, token1, CPAMM, accounts, run_num):
    # deploy AMM
    ammToReturn = CPAMM.deploy(token0, token1, {"from": accounts[0]})
    # add initial liquidity
    sender_balance0 = token0.balanceOf(accounts[0])
    amount = sender_balance0 // 4
    token0.approve(ammToReturn, 1e21, {"from": accounts[0]})
    token1.approve(ammToReturn, 1e21, {"from": accounts[0]})

    with brownie.reverts("shares = 0"):
        if run_num == 0:
            ammToReturn.addLiquidity(amount, 0)
        else:
            ammToReturn.addLiquidity(0, amount)


def test_add_tiny_liquidity(token0, token1, amm, accounts):
    token0.transfer(accounts[1], 100, {"from": accounts[0]})
    token1.transfer(accounts[1], 100, {"from": accounts[0]})
    token0.approve(amm, 100, {"from": accounts[1]})
    token1.approve(amm, 100, {"from": accounts[1]})
    userBalance0 = token0.balanceOf(accounts[0])
    userBalance1 = token1.balanceOf(accounts[0])
    token0.approve(amm, userBalance0, {"from": accounts[0]})
    token1.approve(amm, userBalance1, {"from": accounts[0]})
    amm.swap(token0, userBalance0, {"from": accounts[0]})
    r0 = amm.reserve0()
    r1 = amm.reserve1()
    # reserve0 * d1 == reserve1 * d0
    d1 = r1 * 10 // r0

    with brownie.reverts():
        amm.addLiquidity(10, d1, {"from": accounts[1]})


@pytest.mark.parametrize("idx", range(3))
def test_add_balanced_liquidity(token0, token1, amm, accounts, idx):
    token0.transfer(accounts[1], 1e17, {"from": accounts[0]})
    token1.transfer(accounts[1], 1e17, {"from": accounts[0]})
    userBalance0 = token0.balanceOf(accounts[1])
    userBalance1 = token1.balanceOf(accounts[1])
    token0.approve(amm, userBalance0, {"from": accounts[1]})
    token1.approve(amm, userBalance1, {"from": accounts[1]})

    tokensToAdd = random.randint(1e10, 1e17)
    amm.addLiquidity(tokensToAdd, tokensToAdd, {"from": accounts[1]})

    assert token0.balanceOf(accounts[1]) == userBalance0 - tokensToAdd
    assert token1.balanceOf(accounts[1]) == userBalance1 - tokensToAdd


def test_add_unbalanced(token0, token1, amm, accounts):
    token0.transfer(accounts[1], 1e15, {"from": accounts[0]})
    token1.transfer(accounts[1], 1e14, {"from": accounts[0]})
    userBalance0 = token0.balanceOf(accounts[1])
    userBalance1 = token1.balanceOf(accounts[1])
    token0.approve(amm, userBalance0, {"from": accounts[1]})
    token1.approve(amm, userBalance1, {"from": accounts[1]})
    with brownie.reverts("x / y != dx / dy"):
        amm.addLiquidity(userBalance0, userBalance1, {"from": accounts[1]})
