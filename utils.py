def nem_network(name):
    if name == "testnet":
        return -1744830464 + 1
    elif name == "mainnet":
        return 1744830464 + 1
    else:
        raise Exception("Unknown network: {0}".format(name))
