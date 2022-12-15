# !/usr/bin/env python3
import os
import sys
from Cryptodome.Hash import SHA256

if len(sys.argv) < 3:
    print("Usage: python3 ", os.path.basename(__file__), "key_file_name document_file_name")
    sys.exit()

key_file_name   = sys.argv[1]
file_name       = sys.argv[2]

# get the authentication key from the file
with open(key_file_name, "rb") as f:
    auth_key = f.read()

# read the input file
input_f = open(file_name, "rb")

# First 32 bytes is the message authentication code
# TODO
mac_from_file = input_f.read(32)

# Use the remaining file content to generate the message authentication code
# TODO
input_content = input_f.read()
h = SHA256.new()
h.update(input_content + auth_key)
mac_generated = h.digest()
input_f.close()

if mac_from_file == mac_generated:
    print ('yes')
else:
    print ('no')
