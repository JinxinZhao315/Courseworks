import sys
from socket import *
from zlib import crc32

MAX_BYTE_LEN = 64
HEADER_LEN = 5 # Checksum = 4 bytes, Seq = 1 byte
PAYLOAD_LEN = 59


# Network initialization
b_port = int(sys.argv[1])
b_socket = socket(AF_INET, SOCK_DGRAM)
b_socket.bind(("127.0.0.1", b_port))
latest_ack_seq = 0
expected_seq = 0

while True:
    # Receive packet
    received_pkt, received_addr = b_socket.recvfrom(MAX_BYTE_LEN)
    # print("pkt received")

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
        received_msg = received_pkt[5:].decode()
        latest_ack_seq = received_seq

        if received_seq == expected_seq:
            print(received_msg, end="")
            expected_seq = 1 - received_seq

        # Form ack packet
        seq_bytes = (latest_ack_seq).to_bytes(1, sys.byteorder)
        checksum = crc32(seq_bytes).to_bytes(4, sys.byteorder)
        ack_pkt = checksum + seq_bytes

        # Send ack to Alice
        b_socket.sendto(ack_pkt, received_addr)
        # print("ack sent")

# b_socket.close()
