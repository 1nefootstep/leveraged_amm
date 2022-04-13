#!/usr/bin/python3
import pytest
import brownie

def test_decrease_position_to_zero(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = 1e17
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})
    assert levAmm.collateralOf(accounts[0]) == _amount

    levAmm.addPosition(_amount * 4, {"from": accounts[0]})
    assert levAmm._userPositions(accounts[0])[1] == _amount * 4

    levAmm.decreasePosition(levAmm._userPositions(accounts[0])[0], {"from": accounts[0]})
    assert levAmm._userPositions(accounts[0])[0] == 0
    assert levAmm._userPositions(accounts[0])[1] <= 1


def test_decrease_position_when_already_zero(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    with brownie.reverts("position cannot be negative"):
        levAmm.decreasePosition(1, {"from": accounts[0]})


def test_decrease_position_by_half(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = 1e19
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})
    assert levAmm.collateralOf(accounts[0]) == _amount

    levAmm.addPosition(_amount * 4, {"from": accounts[0]})
    assert levAmm._userPositions(accounts[0])[1] == _amount * 4
    halfOtherToken = 17241379310344827586
    levAmm.decreasePosition(halfOtherToken, {"from": accounts[0]})
    assert levAmm._userPositions(accounts[0])[0] == halfOtherToken
    assert levAmm._userPositions(accounts[0])[1] == 18518518518518518519

def test_decrease_position_profit(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = 1e17
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})
    assert levAmm.collateralOf(accounts[0]) == _amount

    levAmm.addPosition(_amount * 4, {"from": accounts[0]})
    assert levAmm._userPositions(accounts[0])[1] == _amount * 4
    collateralTokenAddr = token0 if param == 0 else token1
    otherTokenAddr = token1 if param == 0 else token0
    levAmm.swap(collateralTokenAddr, 1e18)
    levAmm.decreasePosition(levAmm._userPositions(accounts[0])[0], {"from": accounts[0]})
    assert levAmm._userPositions(accounts[0])[0] == 0
    assert levAmm._userPositions(accounts[0])[1] == 0
    profit = levAmm.collateralOf(accounts[0]) - _amount
    assert profit == 2237751441616677