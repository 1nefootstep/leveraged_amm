// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "./CPAMM.sol";

struct Position {
    uint256 otherTokenAmount; // in other token
    uint256 positionValue; // in collateraltoken
    bool isActive;
}

contract LevCPAMM is CPAMM {
    uint32 public maxLeverage;
    uint16 public constant leverageRatio = 1000; // to add dp to maxLeverage
    IERC20 public collateralToken;
    mapping(address => uint256) public positionValueOf;
    mapping(address => mapping(uint256 => Position)) public userPositions;
    mapping(address => uint256) public lastPositionIndexOf;
    mapping(address => uint256) public collateralOf;

    constructor(
        address _token0,
        address _token1,
        address _collateralToken,
        uint32 _maxLeverage
    ) CPAMM(_token0, _token1) {
        require(
            _collateralToken == _token0 || _collateralToken == _token1,
            "collateral needs to be one of the token pair"
        );
        require(_maxLeverage >= leverageRatio, "maxLeverage needs to be >=1");
        collateralToken = IERC20(_collateralToken);
        maxLeverage = _maxLeverage;
    }

    function _collateralTokenToOtherPair(uint256 _amount)
        private
        view
        returns (uint256)
    {
        (uint256 rCollateral, uint256 rOther) = collateralToken == token0
            ? (reserve0, reserve1)
            : (reserve1, reserve0);
        return (_amount * rOther) / rCollateral;
    }

    function _otherPairToCollateralToken(uint256 _amount)
        private
        view
        returns (uint256)
    {
        (uint256 rCollateral, uint256 rOther) = collateralToken == token0
            ? (reserve0, reserve1)
            : (reserve1, reserve0);
        return (_amount * rCollateral) / rOther;
    }

    function maxLeverageOf(address _user) public view returns (uint256) {
        return (collateralOf[_user] * maxLeverage) / leverageRatio;
    }

    function remainingPositionOf(address _user) public view returns (uint256) {
        uint256 userMaxLeverage = maxLeverageOf(_user);
        uint256 userCurrLeverage = positionValueOf[_user];
        return userMaxLeverage - userCurrLeverage;
    }

    function simulatePositionAddedInOtherToken(
        uint256 _amount,
        uint32 _leverage
    ) public view returns (uint256) {
        return
            _collateralTokenToOtherPair((_amount * _leverage) / leverageRatio);
    }

    function calculateCollateralNeeded(
        uint256 _amountInOtherPair,
        uint32 _leverage
    ) public view returns (uint256) {
        return
            (_otherPairToCollateralToken(_amountInOtherPair) * leverageRatio) /
            _leverage;
    }

    function addCollateral(uint256 _amount) external {
        collateralToken.transferFrom(msg.sender, address(this), _amount);
        uint256 collateralBal = collateralToken.balanceOf(address(this));
        uint256 collateralReserve = collateralToken == token0
            ? reserve0
            : reserve1;
        uint256 dCollateral = collateralBal - collateralReserve;
        collateralOf[msg.sender] += dCollateral;
    }

    function removeCollateral(uint256 _amount) external {
        require(collateralOf[msg.sender] >= _amount, "insufficient collateral");
        uint256 positionValue = positionValueOf[msg.sender];
        uint256 maxPositionInCollateralTokenAfter = ((collateralOf[msg.sender] -
            _amount) * maxLeverage) / leverageRatio;
        require(
            maxPositionInCollateralTokenAfter >= positionValue,
            "active positions greater than collateral * maxLeverage"
        );

        collateralOf[msg.sender] -= _amount;
        collateralToken.transfer(msg.sender, _amount);
    }

    function addPosition(uint256 _amountInOtherPair) external {
        uint256 positionToAddInCollateralToken = _otherPairToCollateralToken(
            _amountInOtherPair
        );
        require(
            remainingPositionOf(msg.sender) >= positionToAddInCollateralToken,
            "exceeds max leverage"
        );
        userPositions[msg.sender][lastPositionIndexOf[msg.sender]] = Position(
            _amountInOtherPair,
            positionToAddInCollateralToken,
            true
        );
        lastPositionIndexOf[msg.sender] += 1;
        positionValueOf[msg.sender] += positionToAddInCollateralToken;
    }

    function closePosition(uint256 idx) external {
        require(
            userPositions[msg.sender][idx].isActive,
            "position does not exist or has closed already"
        );
        userPositions[msg.sender][idx].isActive = false;
        positionValueOf[msg.sender] -= userPositions[msg.sender][idx]
            .positionValue;
        // TODO?: somehow settle profits/loss from this position
    }
}
