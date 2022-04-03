#!/usr/bin/python3
import pytest
import brownie


def test_remove_all_liquidity(token0, token1, amm, accounts):
    userShares = amm.balanceOf(accounts[0])
    amm.removeLiquidity(userShares, {"from": accounts[0]})

    assert token0.balanceOf(accounts[0]) == 1e21
    assert token1.balanceOf(accounts[0]) == 1e21


def test_remove_tiny_liquidity_balanced(token0, token1, amm, accounts):
    curr_token0 = token0.balanceOf(accounts[0])
    curr_token1 = token1.balanceOf(accounts[0])
    token0_added = 1e21 - curr_token0
    token1_added = 1e21 - curr_token1
    userShares = amm.balanceOf(accounts[0])
    txn_receipt = amm.removeLiquidity(1, {"from": accounts[0]})
    assert token0.balanceOf(accounts[0]) == curr_token0 + 1
    assert token1.balanceOf(accounts[0]) == curr_token1 + 1
    assert amm.balanceOf(accounts[0]) == userShares - 1


def test_remove_tiny_liquidity_unbalanced(token0, token1, amm, accounts):
    token0.approve(amm, 1e21, {"from": accounts[0]})
    token1.approve(amm, 1e21, {"from": accounts[0]})
    amm.swap(token0, 1e19, {"from": accounts[0]})
    
    curr_token0 = token0.balanceOf(accounts[0])
    curr_token1 = token1.balanceOf(accounts[0])
    userShares = amm.balanceOf(accounts[0])
    txn_receipt = amm.removeLiquidity(1, {"from": accounts[0]})

    assert token0.balanceOf(accounts[0]) == curr_token0 + 1
    assert token1.balanceOf(accounts[0]) == curr_token1 + 0
    assert amm.balanceOf(accounts[0]) == userShares - 1


def test_remove_half_liquidity(token0, token1, amm, accounts):
    curr_token0 = token0.balanceOf(accounts[0])
    curr_token1 = token1.balanceOf(accounts[0])
    token0_added = 1e21 - curr_token0
    token1_added = 1e21 - curr_token1
    userShares = amm.balanceOf(accounts[0])
    amm.removeLiquidity(userShares // 2, {"from": accounts[0]})

    token0_returned = token0_added // 2
    token1_returned = token1_added // 2
    assert token0.balanceOf(accounts[0]) == curr_token0 + token0_returned
    assert token1.balanceOf(accounts[0]) == curr_token1 + token1_returned


def test_total_supply_change(token0, token1, amm, accounts):
    curr_supply = amm.totalSupply()
    curr_token0 = token0.balanceOf(accounts[0])
    curr_token1 = token1.balanceOf(accounts[0])
    token0_added = 1e21 - curr_token0
    token1_added = 1e21 - curr_token1
    userShares = amm.balanceOf(accounts[0])
    shares_removed = userShares // 5
    txn_receipt = amm.removeLiquidity(shares_removed, {"from": accounts[0]})
    # (token0_returned, token1_returned) = txn_receipt.return_value
    # print(f"token0_returned: {token0_returned}, token1_returned: {token1_returned}")
    token0_returned = token0_added // 5
    token1_returned = token1_added // 5
    assert token0.balanceOf(accounts[0]) == curr_token0 + token0_returned
    assert token1.balanceOf(accounts[0]) == curr_token1 + token1_returned
    assert amm.totalSupply() == curr_supply - shares_removed


@pytest.mark.parametrize("idx", range(1, 3))
def test_remove_liquidity_no_shares(token0, token1, amm, accounts, idx):
    userShares = amm.balanceOf(accounts[idx])
    txn_receipt = amm.removeLiquidity(userShares, {"from": accounts[idx]})
    (token0_returned, token1_returned) = txn_receipt.return_value
    assert token0_returned == 0
    assert token1_returned == 0
    assert token0.balanceOf(accounts[idx]) == 0
    assert token1.balanceOf(accounts[idx]) == 0


def test_remove_more_liquidity_than_shares(amm, accounts):
    userShares = amm.balanceOf(accounts[0])
    with brownie.reverts():
        amm.removeLiquidity(userShares + 1, {"from": accounts[0]})
