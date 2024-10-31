#!/usr/bin/env python

import base45

x = base45.b45encode(b"Hello")
print(x)
print(base45.b45decode(x))
