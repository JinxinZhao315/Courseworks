import zlib
import sys

file_name = sys.argv[1]

with open(file_name, "rb") as f:
    f_bytes = f.read()

checksunm = zlib.crc32(f_bytes)

print(checksunm)
