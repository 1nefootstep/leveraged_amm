# User story/rationale
This leveraged AMM was built with the following scenario:
```
### Leveraged AMM exchange module

Please design an AMM exchange that enables **leverage**. Leverage allows users to purchase other assets  (here, we also call the swapped asset **position**) more than the deposited collateral.

This exchange should

- have the logic of the above AMM exchange module (see above description)
- be able to deposit USDC (an ERC20 token). This would be the collateral of users
- be able to support leverage trading: with the deposited asset, users can swap for another asset in the AMM pool
- have one or a set of `view` function(s), which could
    - input the amount of asset A and the leverage, and it returns the amount of asset B you will get after the swap
    - input the amount of asset B you want to exchange and the leverage, and it returns the amount of asset A you should provide
- have a `view` function that returns the remaining value of the account
    - the remaining account value: deposited amount * max leverage *(*)* - position value
    - position value: the value of a position which is calculated based on deposited assets

A user story

An exchange has a ETH/USDC AMM leverage trading pool and the max leverage is 10x

- Alice deposits 50 USDC into this exchange
- Alice opens a 8x position, which means she can get $400 worth of ETH position
    - At this moment, Alice’s remaining account value is 50 * 10 - 400 = 100
- Alice opens another 2x position, she can get $100 worthy ETH position
    - At this moment, Alice’s remaining account value is 50 * 10 - (400 + 100) = 0
- Alice’s current leverage is 10x, which is already the default max leverage, so she cannot get anymore ETH position; selling ETH is possible though
```

## Built with
Brownie's token template and ![constant product amm example](https://solidity-by-example.org/defi/constant-product-amm/) from solidity-by-example.

## Installation

1. [Install Brownie](https://eth-brownie.readthedocs.io/en/stable/install.html)


## Unit Testing

To run the tests:

```bash
brownie test
```
You will need to either have the .env file ready or remove these lines to stop brownie from complaining if you just want to run the unit tests right away.

```
// REMOVE THESE FROM brownie-config.yaml
// IF YOU WANT TO RUN THE UNIT TESTS RIGHT AWAY WITHOUT PROVIDING PRIVATE KEY ON .env


wallets:
  from_key: ${PRIVATE_KEY}
```

## Testing the module

Setting up .env and the blockchain network:
For example, if testing on a local ganache, add the network to brownie with,
```bash
brownie networks add <MY_NETWORK_NAME> host=<NETWORK_ID_ON_GANACHE> chainid=1337
```
Then copy the private key of the account that would do most of the functionalities.
Make a .env file and put this inside
```bash
export PRIVATE_KEY=<MY_PRIVATE_KEY>
```

### Deploying
First deploy the contracts with:

```bash
brownie run --network <YOUR_BLOCKCHAIN_NETWORK> scripts/deploy.py
```
The parameters can be adjust accordingly... For example, the following creates the erc20 token named USD Coin, ticker USDC, 18 decimal places, and with initial supply of 1e21.
```python
usdc_addr = deploy_token("USD Coin", "USDC", 18, 1e21)
```
And for the amm, the first two arguments are the addresses of the tokens in the amm pool.
The third argument is the erc20 token that will be the collateral. Finally, the last argument is
the max leverage. The max leverage argument is multiplied by 1000, so if you want 10x leverage, 10000 is the argument.
```python
amm_addr = deploy_amm(weth_addr, usdc_addr, usdc_addr, 10000)
```

### Adding liquidity
Then add liquidity to the amm with:
```bash
brownie run --network <YOUR_BLOCKCHAIN_NETWORK> scripts/add_liquidity.py
```
The parameters like how many tokens to add for both sides of the pool can be configured within the add_liquidity.py script.

### Other functions
After adding liquidity, you can add collateral.
```bash
brownie run --network <YOUR_BLOCKCHAIN_NETWORK> scripts/depositCollateral.py
```
And then create positions,
```bash
brownie run --network <YOUR_BLOCKCHAIN_NETWORK> scripts/createPosition.py
```
You can withdraw collateral, close positions with the following:

```bash
brownie run --network <YOUR_BLOCKCHAIN_NETWORK> scripts/withdrawCollateral.py
brownie run --network <YOUR_BLOCKCHAIN_NETWORK> scripts/closePosition.py
```

There are also the view functions to simulate the position size.
```bash
brownie run --network <YOUR_BLOCKCHAIN_NETWORK> scripts/simulatePosition.py
```
and to check collateral necessary to create a position of some size
```bash
brownie run --network <YOUR_BLOCKCHAIN_NETWORK> scripts/calcCollateralNeeded.py
```

## Limitations
No forced liquidations, so the amm can get rugged.

## Actual code written
Actual code written is the LevCPAMM.sol contract, CPAMM unit tests and LevCPAMM unit tests.

## License

This project is licensed under the [MIT license](LICENSE).
