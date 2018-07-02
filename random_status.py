#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys, os, cgi, json, binascii, re
from hash_wrapper import sha3_256
from nem_wrapper2 import get_trans, get_block_at, HttpException

try:
    if os.environ["REQUEST_METHOD"] != "POST":
        sys.stdout.write(b"Status: 405 Method Not Allowed\n\nOnly POST method is allowed\n")
        sys.exit(0)

    if os.environ["CONTENT_TYPE"] != "application/x-www-form-urlencoded":
        sys.stdout.write(
            b"Status: 415 Unsupported Media Type\n\nOnly x-www-form-urlencoded content type is supported\n")
        sys.exit(0)
except Exception:
    sys.stdout.write(b"Status: 500 Internal Server Error\n\n")
    sys.exit(0)


arguments = cgi.FieldStorage()
tx_hash = arguments.getvalue("tx_hash")

if tx_hash is None:
    sys.stdout.write(
        b"Status: 400 Bad Request \n\nTransaction hash must be not empty\n")
    quit(0)

txobj = None
try:
    txobj = get_trans(tx_hash)
    if txobj is None:
        raise Exception("TX_GET_ERROR")
except HttpException as ex:
    print("Content-type:application/json\r\n\r\n")
    print(json.dumps({"status": "NOT_CONFIRMED"}))
    quit(0)
except Exception as e:
    print("Content-type:application/json\r\n\r\n")
    print("Status: 500 Internal Server Error\n\n")
    print(json.dumps({"error": str(e)}))
    quit(0)

userid = None
try:
    message = binascii.unhexlify(txobj["transaction"]["message"]["payload"]).decode("utf-8")
    match = re.search("RAND:.+:.+", message)
    if not match:
        raise ValueError
    rnd = message.split(":")
    userid = rnd[1]
except ValueError:
    print("Content-type:application/json\r\n\r\n")
    print("Status: 500 Internal Server Error\n\n")
    print(json.dumps({"error": "WRONG_MESSAGE_FORMAT"}))
    quit(0)
except Exception as e:
    print("Content-type:application/json\r\n\r\n")
    print("Status: 500 Internal Server Error\n\n")
    print(json.dumps({"error": str(e)}))
    quit(0)

height = txobj["meta"]["height"]
try:
    block = get_block_at(int(height) + 1)
    block_hash = block["prevBlockHash"]["data"]
    sha3h = sha3_256((block_hash + userid).encode("utf-8"))
    uh = binascii.unhexlify(sha3h)
    n = 0
    for byte in uh[-8:]:
        n = n << 8 | byte
    print("Content-type:application/json\r\n\r\n")
    print(json.dumps({"status": "SUCCESS", "number": n, "hash": sha3h, "height": height, "block_hash": block_hash, "userid": userid}))
except HttpException as e:
    print("Content-type:application/json\r\n\r\n")
    print(json.dumps({"status": "BLOCK_HEIGHT_NOT_READY"}))
except Exception as e:
    print("Content-type:application/json\r\n\r\n")
    print("Status: 500 Internal Server Error\n\n")
    print(json.dumps({"status": str(e)}))
