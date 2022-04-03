#!/usr/bin/python3
import pytest
import brownie
import random

def test_remove_all_collateral(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    if (param == 0):
        collateralToken = token0
    else:
        collateralToken = token1
    balance = collateralToken.balanceOf(accounts[0])
    levAmm.addCollateral(50, {"from": accounts[0]})

    assert levAmm.collateralOf(accounts[0]) == 50
    assert collateralToken.balanceOf(accounts[0]) == balance - 50

    balance = collateralToken.balanceOf(accounts[0])
    levAmm.removeCollateral(50, {"from": accounts[0]})
    assert levAmm.collateralOf(accounts[0]) == 0
    assert collateralToken.balanceOf(accounts[0]) == balance + 50


def test_remove_more_collateral_than_there_is(levAmm, accounts):
    levAmm, param = levAmm
    _amount = random.randint(1e12, 1e18)
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})
    assert levAmm.collateralOf(accounts[0]) == _amount

    with brownie.reverts("insufficient collateral"):
        levAmm.removeCollateral(_amount + 1, {"from": accounts[0]})


def test_remove_collateral_with_positions_failure(token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = random.randint(1e12, 1e18)
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})
    assert levAmm.collateralOf(accounts[0]) == _amount
    levAmm.addPosition(
        _amount * 6 * levAmm.reserve0() // levAmm.reserve1(), {"from": accounts[0]}
    )
    assert levAmm.positionValueOf(accounts[0]) == _amount * 6

    with brownie.reverts("active positions greater than collateral * maxLeverage"):
        levAmm.removeCollateral(_amount, {"from": accounts[0]})

    with brownie.reverts("active positions greater than collateral * maxLeverage"):
        levAmm.removeCollateral(_amount // 2, {"from": accounts[0]})

