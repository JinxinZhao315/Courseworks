import sys
header = sys.stdin.buffer.read1(6)

while len(header) != 0:
    len_str = ''
    if header == b'Size: ' :
        digit = sys.stdin.buffer.read1(1)
        while digit != b'B':
            len_str = len_str + digit.decode();
            digit = sys.stdin.buffer.read1(1)
        payload = sys.stdin.buffer.read1(int(len_str))
        sys.stdout.buffer.write(payload) 
        sys.stdout.buffer.flush()
        header = sys.stdin.buffer.read1(6)
        
