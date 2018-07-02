# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import math
import config as config_lib
from fees import calculate_message, calculate_minimum, currentFeeFactor
from logger import Logger
from binascii import hexlify, unhexlify
from http.client import HTTPConnection
from nem_python import TransactionBuilder
from nem_ed25519.signature import sign
from utils import nem_network

config = config_lib.config["nem"]
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
    transfer["version"] = nem_network(config["network"])  #  mainnet = 1744830464 + 1 ; testnet = -1744830464 + 1
    transfer["signer"] = config["publickey"]
    tx_hex = TransactionBuilder().encode(transfer)
    sign_raw = sign(msg=unhexlify(tx_hex.encode()), sk=config["privatekey"], pk=config["publickey"])
    sign_hex = hexlify(sign_raw).decode()
    transaction = json.dumps({"data": tx_hex, "signature": sign_hex})
    r = send_request("/transaction/announce", "POST", transaction)
    res = {"tx": r["transactionHash"]["data"]}
    if r["code"] != 1:
        res["error"] = r["message"]
    return res
