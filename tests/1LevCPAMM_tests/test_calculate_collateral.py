#!/usr/bin/python3
import pytest
import brownie
import random
import math
from decimal import Decimal


def test_calculate_collateral_price_equal(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = random.randint(1e12, 1e18)
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    assert _amount // 6 == levAmm.calculateCollateralNeeded(_amount, 6000)


def test_calculate_collateral_price_different(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = 1e15
    _amount2 = 6e16
    levAmm.swap(token0, _amount2, {"from": accounts[0]})
    if param == 0:
        # other_token_price = levAmm.reserve0() // levAmm.reserve1()
        assert Decimal(
            _amount
        ) * levAmm.reserve0() // levAmm.reserve1() * 1000 // 6666 == levAmm.calculateCollateralNeeded(
            _amount, 6666
        )
    else:
        # other_token_price = levAmm.reserve1() // levAmm.reserve0()
        assert Decimal(
            _amount
        ) * levAmm.reserve1() // levAmm.reserve0() * 1000 // 6666 == levAmm.calculateCollateralNeeded(
            _amount, 6666
        )

    # assert (
    #     _amount * other_token_price * 1000 // 6666
    #     == levAmm.calculateCollateralNeeded(_amount, 6666)
    # )
