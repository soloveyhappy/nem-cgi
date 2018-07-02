import sha3
import hashlib


def sha3_256(data):
    return sha3.sha3_256(data).hexdigest()


def sha3_256_arr(data):
    s = sha3.sha3_256(data[0])
    for i in data[1:]:
        s.update(i)
    return s.hexdigest()


def md5(data):
    return hashlib.md5(data).hexdigest()


def keccak_256(data):
    return sha3.keccak_256(data).hexdigest()
