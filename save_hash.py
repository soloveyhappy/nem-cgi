#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

import json
import os
import sys
import cgi
from nem_wrapper2 import send, HttpException

arguments = cgi.FieldStorage()
hash = arguments.getvalue("hash")
filename = arguments.getvalue("filename")

try:
    if os.environ["REQUEST_METHOD"] != "POST":
        sys.stdout.write(b"Status: 405 Method Not Allowed\n\nOnly POST method is allowed\n")
        quit(0)

    if os.environ["CONTENT_TYPE"] != "application/x-www-form-urlencoded":
        sys.stdout.write(
            b"Status: 415 Unsupported Media Type\n\nOnly x-www-form-urlencoded content type is supported\n")
        quit(0)
except Exception:
    print("Status: 500 Internal Server Error\n\n")
    quit(0)

try:
    r = send("HASH:{0}:{1}".format(filename, hash))
    print("Content-type:application/json\r\n\r\n")
    print(json.dumps(r))
except HttpException as ex:
    print("Content-type:application/json\r\n\r\n")
    print("Status: 500 Internal Server Error\n\n")
    print(json.dumps({"error": ex.description}))
except Exception as e:
    print("Content-type:application/json\r\n\r\n")
    print("Status: 500 Internal Server Error\n\n")
    print(json.dumps({"error": str(e)}))
