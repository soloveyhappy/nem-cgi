# -*- coding: utf-8 -*-

from http.client import HTTPConnection
import json
import os
import sys
import math
import time
import config as config_lib
from logger import Logger
from binascii import hexlify
from fees import currentFeeFactor, calculate_message, calculate_minimum
from utils import nem_network

config = config_lib.config["nem"]

# os.path.join(os.path.dirname(sys.argv[0]), os.pardir, "var", "log", "free-tickets-nem.log")
logger = Logger(os.path.join(os.path.dirname(sys.argv[0]), "x-game.log"))


class HttpException(Exception):
    def __init__(self, code, description):
        self.code = code
        self.description = description

    def __str__(self):
        return "NIS API HTTP error {0}: {1}".format(self.code, self.description)


def send_request(path, method="GET", data=""):
    h = HTTPConnection(config["host"], config["port"])
    headers = {}
    if method == "POST":
        headers["Content-type"] = "application/json"
    h.request(method, path, data, headers)
    r = h.getresponse()
    bytes_string = r.read()
    obj = json.loads(bytes_string.decode("utf-8"))
    if r.status != 200:
        message = obj["message"] if "message" in obj else r.reason
        raise HttpException(r.status, message)
    return obj


def block_count():
    try:
        return send_request("/chain/height")["height"]
    except:
        return None


def balance(address):
    try:
        r = send_request("/account/get?address={0}".format(address))
        return r["account"]["balance"]/1000000.0
    except:
        return 0.0


def get_trans(tx_hash):
    return send_request("/transaction/get/?hash={0}".format(tx_hash))


def get_block_at(height):
    return send_request("/block/at/public", "POST", json.dumps({"height": height}))


def send(message, address=config["address"]):
    nem_amount = 0
    hex_message = hexlify(message.encode("utf-8")).decode()
    fee = currentFeeFactor * calculate_minimum(nem_amount / 1000000)
    msg_fee = calculate_message(hex_message)
    total_fee = math.floor((msg_fee + fee) * 1000000)
    transfer = {}
    transfer["timeStamp"] = int(time.time()) - 1427587585
    transfer["deadline"] = int(time.time()) - 1427587585 + 3600 * 2
    transfer["amount"] = nem_amount
    transfer["fee"] = total_fee
    transfer["recipient"] = address
    transfer["type"] = 257
    transfer["message"] = {"payload": hex_message, "type": 1}
    transfer["version"] = nem_network(config["network"])  # TODO mainnet = 0x68000001 testnet = 0x98000001||| testnet = -1744830464 + 1; mainnet = 1744830464 + 1
    transfer["signer"] = config["publickey"]
    transaction = json.dumps({"transaction": transfer, "privateKey": config["privatekey"]})
    r = send_request("/transaction/prepare-announce", "POST", transaction)
    res = {"tx": r["transactionHash"]["data"]}
    if r["code"] != 1:
        res["error"] = r["message"]
    return res



