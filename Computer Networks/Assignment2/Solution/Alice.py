import sys
from socket import *
from zlib import crc32

MAX_BYTE_LEN = 64
HEADER_LEN = 5 # Checksum = 4 bytes, Seq = 1 byte
PAYLOAD_LEN = 59

# Read input from stdin into msg_byte_arr
def read_input():
    byte_num = PAYLOAD_LEN
    msg_byte_arr = bytearray()
    while byte_num > 0:
        curr_msg = sys.stdin.buffer.read1(byte_num)
        if len(curr_msg) == 0:
            break
        msg_byte_arr.extend(curr_msg)
        byte_num -= len(curr_msg)
    return msg_byte_arr

# Network initialization
a_port = int(sys.argv[1])
a_socket = socket(AF_INET, SOCK_DGRAM)
a_socket.settimeout(5e-2)
seq = 0
msg_byte_arr = read_input()

while True:
    try:
        # Add header to msg to form full packet
        if len(msg_byte_arr) == 0:
            break
        seq_bytes = (seq).to_bytes(1, sys.byteorder)
        checksum_seg = seq_bytes + msg_byte_arr
        checksum = crc32(checksum_seg).to_bytes(4, sys.byteorder)
        full_pkt = checksum + checksum_seg

        # Send full packet to unreliNet
        a_socket.sendto(full_pkt, ("127.0.0.1", a_port))
        # print("pkt sent")

        # Receive packet
        received_pkt, received_addr = a_socket.recvfrom(MAX_BYTE_LEN)
        # print("ack received")

        # Verify checksum of received packet
        is_checksum_ok = False
        received_checksum = int.from_bytes(received_pkt[:4], sys.byteorder)
        try:
            calculated_checksum = crc32(received_pkt[4:])
            is_checksum_ok = calculated_checksum == received_checksum
        except:
            is_checksum_ok = False

        if is_checksum_ok:
            # Parse received pkt
            received_seq = int.from_bytes(received_pkt[4:5], sys.byteorder)
            if received_seq == seq:
                msg_byte_arr = read_input()
                seq = 1 - seq
    except timeout:
        # Resend the packet by going back to the top of while loop
        pass

a_socket.close()