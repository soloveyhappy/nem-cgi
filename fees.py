# -*- coding: utf-8 -*-

import math

currentFeeFactor = 0.05


def calculate_minimum(num_nem):
    fee = math.floor(max(1, num_nem / 10000))
    return 25 if fee > 25 else fee


def calculate_message(message):
    if (message is None) or len(message) == 0:
        return 0.0
    length = len(message) / 2
    return currentFeeFactor * (math.floor(length / 32) + 1)
