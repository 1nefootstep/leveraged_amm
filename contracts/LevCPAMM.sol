// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "./CPAMM.sol";

struct Position {
    uint256 otherTokenAmount; // in other token
    uint256 collateralValue; // in collateraltoken
    int256 pnl; // 0
    // usdc you sell - usdc you buy (collateral value)
    // bool isActive;
}

contract LevCPAMM is CPAMM {
    uint32 public maxLeverage;
    // uint256 public constant ratio =
    uint16 public constant leverageRatio = 1000; // to add dp to maxLeverage
    IERC20 public collateralToken;
    mapping(address => uint256) public positionValueOf;
    mapping(address => mapping(uint256 => Position)) public userPositions;
    mapping(address => Position) public _userPositions;
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

    function _levSwap(address _tokenIn, uint _amountIn) internal returns (uint amountOut) {
        require(
            _tokenIn == address(token0) || _tokenIn == address(token1),
            "invalid token"
        );

        bool isToken0 = _tokenIn == address(token0);

        (uint reserveIn, uint reserveOut) = isToken0
            ? (reserve0, reserve1)
            : (reserve1, reserve0);

        // tokenIn.transferFrom(msg.sender, address(this), _amountIn);
        // uint amountIn = tokenIn.balanceOf(address(this)) - reserveIn;

        /*
        How much dy for dx?

        xy = k
        (x + dx)(y - dy) = k
        y - dy = k / (x + dx)
        y - k / (x + dx) = dy
        y - xy / (x + dx) = dy
        (yx + ydx - xy) / (x + dx) = dy
        ydx / (x + dx) = dy
        */
        // 0.3% fee
        // uint amountInWithFee = (amountIn * 997) / 1000;
        // amountOut = (reserveOut * amountInWithFee) / (reserveIn + amountInWithFee);
        amountOut = (reserveOut * _amountIn) / (reserveIn + _amountIn);

        (uint res0, uint res1) = isToken0
            ? (reserveIn + _amountIn, reserveOut - amountOut)
            : (reserveOut - amountOut, reserveIn + _amountIn);

        _update(res0, res1);
        // tokenOut.transfer(msg.sender, amountOut);
    }

    function addPosition(uint256 _amountInOtherPair) external {
        // 1 ETH = $500
        // coll = $1000
        // 10 ETH = $5000 -> $6000
        // 5000 -> 0
        // pnl 1000
        // want to buy 10 eth which needs 
        // want to buy 10 eth which needs $5000    
        uint256 positionToAddInCollateralToken = _otherPairToCollateralToken(
           _amountInOtherPair
        );
        require(
            remainingPositionOf(msg.sender) >= positionToAddInCollateralToken,
            "exceeds max leverage"
        );

        _userPositions[msg.sender].collateralValue += positionToAddInCollateralToken;
        _userPositions[msg.sender].otherTokenAmount += _amountInOtherPair;
        // _userPositions[msg.sender] += Position(
        //     _amountInOtherPair,
        //     positionToAddInCollateralToken
        // );
        _levSwap(address(collateralToken), positionToAddInCollateralToken);
        // lastPositionIndexOf[msg.sender] += 1;
        positionValueOf[msg.sender] += positionToAddInCollateralToken;
    }

    function decreasePosition(uint256 _amountInOtherPair) external {
    // function closePosition(uint256 idx) external {
        require(
            _userPositions[msg.sender].otherTokenAmount - _amountInOtherPair >= 0,
            "position cannot be negative"
        );
        
        IERC20 _otherToken = collateralToken == token0 ? token1 : token0;
        uint256 _amount_out = _levSwap(address(_otherToken), _amountInOtherPair);
        _userPositions[msg.sender].otherTokenAmount -= _amountInOtherPair;

        // 3000 - 5000 = -2000
        // 5 * 1000 / 10
        uint256 closeRatio = _amountInOtherPair * 1000 / _userPositions[msg.sender].otherTokenAmount;
        int256 pnl = _amount_out - _userPositions[msg.sender].collateralValue;
        _userPositions[msg.sender].collateralValue -= _amountInOtherPair;

        positionValueOf[msg.sender] -= _userPositions[msg.sender]
            .collateralValue;
        // TODO?: somehow settle profits/loss from this position
    }
}
