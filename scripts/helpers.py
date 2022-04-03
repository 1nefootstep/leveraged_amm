from brownie import accounts, config, Token, LevCPAMM, network


def get_account():
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])
