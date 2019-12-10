# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 10:32:39 2019

@author: lvi
"""

import hashlib
import secrets
import jwt
import json

key = "pas213" + "sallT"
key = str.encode(key)

h = hashlib.sha256()
h.update(key)
hex_hash = h.hexdigest()
print(hex_hash)

print(secrets.token_urlsafe(24))


encoded = jwt.encode({'test': 'yes'}, 'NS8V26K7aRTP5wDXwVxkR4iBy1oEiNud', algorithm='HS256')
print(encoded)
edit_encoded = encoded[:-1]
print(edit_encoded)
decoded = jwt.decode(encoded, 'NS8V26K7aRTP5wDXwVxkR4iBy1oEiNud', algorithm='HS256')
print(decoded)



asd = (1,2,3)
qwe = (4,)

keys = ('a','b','c','d')
bb = dict(zip(keys, asd+qwe))

print(bb)
