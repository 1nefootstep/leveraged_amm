#!/usr/bin/python3
import pytest
import brownie
import random


def test_add_position(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = random.randint(1e12, 1e18)
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})
    assert levAmm.collateralOf(accounts[0]) == _amount

    levAmm.addPosition(
        _amount * 4 * levAmm.reserve0() // levAmm.reserve1(), {"from": accounts[0]}
    )
    assert levAmm.positionValueOf(accounts[0]) == _amount * 4
    otherTokenValue, positionValue, isActive = levAmm.userPositions(accounts[0], 0)
    assert otherTokenValue == _amount * 4 * levAmm.reserve0() // levAmm.reserve1()
    assert positionValue == _amount * 4
    assert isActive


def test_insufficient_collateral(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = random.randint(1e12, 1e18)
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})

    assert levAmm.collateralOf(accounts[0]) == _amount

    with brownie.reverts("exceeds max leverage"):
        levAmm.addPosition(
            _amount * levAmm.reserve0() // levAmm.reserve1() * 11, {"from": accounts[0]}
        )


def test_insufficient_collateral_due_to_active_positions(
    token0, token1, levAmm, accounts
):
    levAmm, param = levAmm
    _amount = random.randint(1e12, 1e18)
    if param == 0:
        other_token_unit = _amount * levAmm.reserve1() // levAmm.reserve0()
    else:
        other_token_unit = _amount * levAmm.reserve0() // levAmm.reserve1()
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})

    levAmm.addPosition(other_token_unit * 3, {"from": accounts[0]})
    levAmm.addPosition(other_token_unit * 3, {"from": accounts[0]})
    levAmm.addPosition(other_token_unit * 3, {"from": accounts[0]})
    assert levAmm.positionValueOf(accounts[0]) == _amount * 9

    with brownie.reverts("exceeds max leverage"):
        levAmm.addPosition(
            _amount * levAmm.reserve0() // levAmm.reserve1() * 3, {"from": accounts[0]}
        )


def test_insufficient_collateral_due_to_active_positions_and_price_change(
    token0, token1, levAmm, accounts
):
    levAmm, param = levAmm
    _amount = 1e18
    # token1.approve(levAmm, 1e21, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})
    if param == 0:
        other_token_unit = _amount * levAmm.reserve1() // levAmm.reserve0()
    else:
        other_token_unit = _amount * levAmm.reserve0() // levAmm.reserve1()
    levAmm.addPosition(other_token_unit * 3, {"from": accounts[0]})
    levAmm.addPosition(other_token_unit * 3, {"from": accounts[0]})
    levAmm.addPosition(other_token_unit * 3, {"from": accounts[0]})
    assert levAmm.positionValueOf(accounts[0]) == _amount * 9
    if param == 0:
        levAmm.swap(token0, 1e20)
    else:
        levAmm.swap(token1, 1e20)
    with brownie.reverts("exceeds max leverage"):
        levAmm.addPosition(other_token_unit, {"from": accounts[0]})


def test_sufficient_collateral_due_to_price_change(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = 1e18
    if param == 0:
        other_token_unit = _amount * levAmm.reserve1() // levAmm.reserve0()
    else:
        other_token_unit = _amount * levAmm.reserve0() // levAmm.reserve1()

    token0.approve(levAmm, 1e21, {"from": accounts[0]})
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    levAmm.addCollateral(_amount, {"from": accounts[0]})
    levAmm.addPosition(other_token_unit * 3, {"from": accounts[0]})
    levAmm.addPosition(other_token_unit * 3, {"from": accounts[0]})
    levAmm.addPosition(other_token_unit * 3, {"from": accounts[0]})
    assert levAmm.positionValueOf(accounts[0]) == _amount * 9
    if param == 0:
        levAmm.swap(token1, 5e18)
    else:
        levAmm.swap(token0, 5e18)

    levAmm.addPosition(other_token_unit + 1, {"from": accounts[0]})

    assert levAmm.positionValueOf(accounts[0]) == 9961168781237985390
