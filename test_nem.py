#!/usr/bin/python
# -*- coding: utf-8 -*-

import config, binascii
from binascii import unhexlify
import sys

from nem_wrapper2 import send, get_block_at
from hash_wrapper import sha3_256


def test_send():
    send("Test", config.config["nem"]["address"])


if __name__ == '__main__':
    test_send()
