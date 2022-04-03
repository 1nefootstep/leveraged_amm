#!/usr/bin/python3
import pytest
import brownie


def test_swap0(token0, token1, CPAMM, accounts):
    # deploy AMM
    amm = CPAMM.deploy(token0, token1, {"from": accounts[0]})
    # add initial liquidity
    token0.approve(amm, 1e21, {"from": accounts[0]})
    token1.approve(amm, 1e21, {"from": accounts[0]})
    amm.addLiquidity(10000, 1000)
    balance0 = token0.balanceOf(accounts[0])
    balance1 = token1.balanceOf(accounts[0])
    r0 = amm.reserve0()
    r1 = amm.reserve1()
    expected_in0 = 6000
    expected_out1 = 375

    txn_receipt = amm.swap(token0, expected_in0, {"from": accounts[0]})
    assert txn_receipt.return_value == expected_out1
    assert token0.balanceOf(accounts[0]) == balance0 - expected_in0
    assert token1.balanceOf(accounts[0]) == balance1 + expected_out1
    assert amm.reserve0() == r0 + expected_in0
    assert amm.reserve1() == r1 - expected_out1

def test_swap1(token0, token1, CPAMM, accounts):
    # deploy AMM
    amm = CPAMM.deploy(token0, token1, {"from": accounts[0]})
    # add initial liquidity
    token0.approve(amm, 1e21, {"from": accounts[0]})
    token1.approve(amm, 1e21, {"from": accounts[0]})
    amm.addLiquidity(10000, 1000)
    balance0 = token0.balanceOf(accounts[0])
    balance1 = token1.balanceOf(accounts[0])
    r0 = amm.reserve0()
    r1 = amm.reserve1()
    expected_in1 = 500
    expected_out0 = 3333

    txn_receipt = amm.swap(token1, expected_in1, {"from": accounts[0]})
    assert txn_receipt.return_value == expected_out0
    assert token0.balanceOf(accounts[0]) == balance0 + expected_out0
    assert token1.balanceOf(accounts[0]) == balance1 - expected_in1
    assert amm.reserve0() == r0 - expected_out0
    assert amm.reserve1() == r1 + expected_in1

def test_two_swap(token0, token1, CPAMM, accounts):
    # deploy AMM
    amm = CPAMM.deploy(token0, token1, {"from": accounts[0]})
    # add initial liquidity
    token0.approve(amm, 1e21, {"from": accounts[0]})
    token1.approve(amm, 1e21, {"from": accounts[0]})
    amm.addLiquidity(10000, 1000)
    balance0 = token0.balanceOf(accounts[0])
    balance1 = token1.balanceOf(accounts[0])
    r0 = amm.reserve0()
    r1 = amm.reserve1()
    expected_in1 = 500
    expected_out0 = 3333

    txn_receipt = amm.swap(token1, expected_in1, {"from": accounts[0]})
    assert txn_receipt.return_value == expected_out0
    assert token0.balanceOf(accounts[0]) == balance0 + expected_out0
    assert token1.balanceOf(accounts[0]) == balance1 - expected_in1
    assert amm.reserve0() == r0 - expected_out0
    assert amm.reserve1() == r1 + expected_in1

    balance0 = token0.balanceOf(accounts[0])
    balance1 = token1.balanceOf(accounts[0])
    r0 = amm.reserve0()
    r1 = amm.reserve1()
    expected_in0 = 777
    expected_out1 = 156

    txn_receipt = amm.swap(token0, expected_in0, {"from": accounts[0]})
    assert txn_receipt.return_value == expected_out1
    assert token0.balanceOf(accounts[0]) == balance0 - expected_in0
    assert token1.balanceOf(accounts[0]) == balance1 + expected_out1
    assert amm.reserve0() == r0 + expected_in0
    assert amm.reserve1() == r1 - expected_out1

def test_invalid_token(token0, token1, amm, accounts):
    token0.approve(amm, 1e21, {"from": accounts[0]})
    token1.approve(amm, 1e21, {"from": accounts[0]})
    
    with brownie.reverts("invalid token"):
        amm.swap(amm, 7e15, {"from": accounts[0]})
    
