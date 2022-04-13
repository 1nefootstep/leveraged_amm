#!/usr/bin/python3
import pytest
import brownie
import random


def test_add_collateral(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    collateralToAdd = random.randint(1e12, 1e20)
    # token1.approve(levAmm, collateralToAdd, {"from": accounts[0]})
    levAmm.addCollateral(collateralToAdd, {"from": accounts[0]})

    assert levAmm.collateralOf(accounts[0]) == collateralToAdd

def test_add_zero_collateral(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    collateralToAdd = 0
    # token1.approve(levAmm, collateralToAdd, {"from": accounts[0]})
    levAmm.addCollateral(collateralToAdd, {"from": accounts[0]})

    assert levAmm.collateralOf(accounts[0]) == collateralToAdd


def test_add_collateral_without_approval(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    collateralToAdd = random.randint(1e12, 1e20)
    token0.approve(levAmm, 0, {"from": accounts[0]})
    token1.approve(levAmm, 0, {"from": accounts[0]})
    with brownie.reverts():
        levAmm.addCollateral(collateralToAdd, {"from": accounts[0]})


def test_add_collateral_without_sufficient_token(token0, token1, levAmm, accounts):
    levAmm, param = levAmm
    collateralToAdd = random.randint(1e12, 1e20)
    # token1.approve(levAmm, collateralToAdd, {"from": accounts[0]})
    with brownie.reverts():
        levAmm.addCollateral(collateralToAdd, {"from": accounts[1]})
