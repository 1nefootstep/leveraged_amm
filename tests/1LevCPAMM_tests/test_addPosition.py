#!/usr/bin/python3
import pytest
import brownie
from decimal import Decimal
import random


def test_add_position(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = 1e18
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})
    assert levAmm.collateralOf(accounts[0]) == _amount
    buyWithCollateralToken = _amount * 4
    # amountOut = (reserveOut * _amountIn) / (reserveIn + _amountIn);
    expectedAmountOut = (Decimal(2.5e20) * Decimal(4e18)) // (
        Decimal(2.5e20) + Decimal(4e18)
    )
    # expectedAmountOut = Decimal(1e21) - Decimal(1e42) // (Decimal(1e21) + Decimal(4e18))
    levAmm.addPosition(buyWithCollateralToken, {"from": accounts[0]})
    otherTokenValue, collateralValue = levAmm._userPositions(accounts[0])
    assert collateralValue == buyWithCollateralToken
    assert otherTokenValue == expectedAmountOut


def test_insufficient_collateral(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = random.randint(1e12, 1e18)
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})

    assert levAmm.collateralOf(accounts[0]) == _amount

    with brownie.reverts("exceeds max leverage"):
        levAmm.addPosition(_amount * 11, {"from": accounts[0]})


def test_insufficient_collateral_due_to_active_positions(
    token0, token1, levAmm, accounts
):
    levAmm, param = levAmm
    # _amount = random.randint(1e12, 1e18)
    _amount = 1e18
    # if param == 0:
    #     other_token_unit = _amount * levAmm.reserve1() // levAmm.reserve0()
    # else:
    #     other_token_unit = _amount * levAmm.reserve0() // levAmm.reserve1()
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})

    levAmm.addPosition(_amount * 3, {"from": accounts[0]})
    levAmm.addPosition(_amount * 3, {"from": accounts[0]})
    levAmm.addPosition(_amount * 3, {"from": accounts[0]})
    
    assert levAmm._userPositions(accounts[0])[0] == 8687258687258687257
    assert levAmm._userPositions(accounts[0])[1] == _amount * 9
    
    print(levAmm.remainingPositionOf(accounts[0]))
    with brownie.reverts("exceeds max leverage"):
        levAmm.addPosition(Decimal(_amount) + 1, {"from": accounts[0]})
