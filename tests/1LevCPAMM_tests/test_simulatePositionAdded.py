#!/usr/bin/python3
import pytest
import brownie
import random
import math
from decimal import Decimal

def test_simulate_position_price_equal(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = random.randint(1e12, 1e18)
    # token1.approve(levAmm, _amount, {"from": accounts[0]})
    assert Decimal(_amount) * 5 == levAmm.simulatePositionAddedInOtherToken(_amount, 5000)


def test_simulate_position_price_different(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    _amount = 1e15
    _amount2 = 6e16
    levAmm.swap(token0, _amount2, {"from": accounts[0]})
    if param == 0:
        assert (
            Decimal(_amount) * 5555 * levAmm.reserve1() // levAmm.reserve0() // 1000 
            == levAmm.simulatePositionAddedInOtherToken(_amount, 5555)
        )
    else:
        assert (
            Decimal(_amount) * 5555 * levAmm.reserve0() // levAmm.reserve1() // 1000 
            == levAmm.simulatePositionAddedInOtherToken(_amount, 5555)
        )


