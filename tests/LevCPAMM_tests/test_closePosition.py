#!/usr/bin/python3
import pytest
import brownie
import random


def test_close_position(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = random.randint(1e12, 1e18)
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})
    assert levAmm.collateralOf(accounts[0]) == _amount

    levAmm.addPosition(
        _amount * 4 * levAmm.reserve0() // levAmm.reserve1(), {"from": accounts[0]}
    )
    assert levAmm.positionValueOf(accounts[0]) == _amount * 4

    levAmm.closePosition(0, {"from": accounts[0]})
    _, _, isActive = levAmm.userPositions(accounts[0], 0)
    assert levAmm.positionValueOf(accounts[0]) == 0
    assert not isActive


def test_close_non_existent_position(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    with brownie.reverts("position does not exist or has closed already"):
        levAmm.closePosition(0, {"from": accounts[0]})


def test_close_already_closed_position(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = random.randint(1e12, 1e18)
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})
    assert levAmm.collateralOf(accounts[0]) == _amount

    levAmm.addPosition(
        _amount * 4 * levAmm.reserve0() // levAmm.reserve1(), {"from": accounts[0]}
    )
    assert levAmm.positionValueOf(accounts[0]) == _amount * 4

    levAmm.closePosition(0, {"from": accounts[0]})
    _, _, isActive = levAmm.userPositions(accounts[0], 0)
    assert levAmm.positionValueOf(accounts[0]) == 0
    assert not isActive

    with brownie.reverts("position does not exist or has closed already"):
        levAmm.closePosition(0, {"from": accounts[0]})
