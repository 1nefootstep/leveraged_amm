#!/usr/bin/python3
import pytest
import brownie
import random


def test_max_leverage_of_after_adding(token1, levAmm, accounts):
    levAmm, param = levAmm
    collateralToAdd = random.randint(1e12, 1e20)
    # token1.approve(levAmm, collateralToAdd, {"from": accounts[0]})
    levAmm.addCollateral(collateralToAdd, {"from": accounts[0]})

    assert levAmm.collateralOf(accounts[0]) == collateralToAdd
    assert levAmm.maxLeverageOf(accounts[0]) == collateralToAdd * 10


def test_max_leverage_of_after_removing(token1, levAmm, accounts):
    levAmm, param = levAmm
    collateralToAdd = 9e16
    collateralToRemove = 4e16
    # token1.approve(levAmm, collateralToAdd, {"from": accounts[0]})
    levAmm.addCollateral(collateralToAdd, {"from": accounts[0]})

    assert levAmm.collateralOf(accounts[0]) == collateralToAdd
    assert levAmm.maxLeverageOf(accounts[0]) == collateralToAdd * 10

    levAmm.removeCollateral(collateralToRemove, {"from": accounts[0]})
    assert levAmm.collateralOf(accounts[0]) == collateralToAdd - collateralToRemove
    assert (
        levAmm.maxLeverageOf(accounts[0]) == (collateralToAdd - collateralToRemove) * 10
    )
