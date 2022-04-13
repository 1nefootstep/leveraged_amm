// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "./CPAMM.sol";

struct Position {
    uint256 otherTokenAmount; // in other token
    uint256 collateralValue; // in collateraltoken
}

contract LevCPAMM is CPAMM {
    uint32 public maxLeverage;
    uint16 public constant leverageRatio = 1000; // to add dp to maxLeverage
    IERC20 public collateralToken;
    mapping(address => Position) public _userPositions;
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
        uint256 userCurrLeverage = _userPositions[_user].collateralValue;
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
        uint256 positionValue = _userPositions[msg.sender].collateralValue;
        uint256 maxPositionInCollateralTokenAfter = ((collateralOf[msg.sender] -
            _amount) * maxLeverage) / leverageRatio;
        require(
            maxPositionInCollateralTokenAfter >= positionValue,
            "active positions greater than collateral * maxLeverage"
        );

        collateralOf[msg.sender] -= _amount;
        collateralToken.transfer(msg.sender, _amount);
    }

    function _levSwap(address _tokenIn, uint256 _amountIn)
        internal
        returns (uint256 amountOut)
    {
        // this require unnecessary because fn is not external
        // require(
        //     _tokenIn == address(token0) || _tokenIn == address(token1),
        //     "invalid token"
        // );
        bool isToken0 = _tokenIn == address(token0);

        (uint256 reserveIn, uint256 reserveOut) = isToken0
            ? (reserve0, reserve1)
            : (reserve1, reserve0);

        amountOut = (reserveOut * _amountIn) / (reserveIn + _amountIn);

        (uint256 res0, uint256 res1) = isToken0
            ? (reserveIn + _amountIn, reserveOut - amountOut)
            : (reserveOut - amountOut, reserveIn + _amountIn);

        _update(res0, res1);
    }

    function addPosition(uint256 _amountInCollateralToken) external {
        require(
            remainingPositionOf(msg.sender) >= _amountInCollateralToken,
            "exceeds max leverage"
        );
        _userPositions[msg.sender].collateralValue += _amountInCollateralToken;
        _userPositions[msg.sender].otherTokenAmount += _levSwap(
            address(collateralToken),
            _amountInCollateralToken
        );
    }

    function decreasePosition(uint256 _amountInOtherPair) external {
        require(
            _userPositions[msg.sender].otherTokenAmount >= _amountInOtherPair,
            "position cannot be negative"
        );
        IERC20 _otherToken = collateralToken == token0 ? token1 : token0;
        uint256 _collateralValue = _userPositions[msg.sender].collateralValue;
        uint256 amountOut = _levSwap(address(_otherToken), _amountInOtherPair);
        _userPositions[msg.sender].otherTokenAmount -= _amountInOtherPair;
        if (_collateralValue > amountOut) {
            _userPositions[msg.sender].collateralValue =
                _collateralValue -
                amountOut;
        } else {
            _userPositions[msg.sender].collateralValue = 0;
            // add profit to collateralValue
            collateralOf[msg.sender] += amountOut - _collateralValue;
        }
    }
}
