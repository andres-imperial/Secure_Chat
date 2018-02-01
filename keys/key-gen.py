import sys
import os
from Crypto.PublicKey import RSA
from Crypto import Random

random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
pkey = key.publickey()

with open('darth-public-key.txt', 'w') as oFile:
    oFile.write(pkey.exportKey())

with open('darth-private-key.txt', 'w') as oFile:
    oFile.write(key.exportKey())

with open('darth-key.txt', 'r') as iFile:
    okey = RSA.importKey(iFile.read(),)
    print okey
