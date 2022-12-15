import sys
from socket import *

key_value_store = {} # key(string): value(any binary string)
counter_store = {} # key(string): value(int)

### Key-value and counter store functions

def key_insert_update(key, value):
    if key_value_store.get(key) == None: # If key doesn't exist, Insertion
        key_value_store[key] = value
        return b"200 OK  "
    else: # If key exists, Update
        if counter_store.get(key) != None:
            return b"405 MethodNotAllowed  "
        else:
            key_value_store[key] = value
            return b"200 OK  "


def key_get(key):
    if key_value_store.get(key) == None:
        return b"404 NotFound  "
    else: # If key exists
        value = key_value_store.get(key)
        byte_str = bytearray(b'200 OK content-length ')
        byte_str.extend(str(len(value)).encode())
        byte_str.extend(b"  ")
        byte_str.extend(value)
        if counter_store.get(key) != None:
            counter_store[key] -= 1
            if counter_store[key] == 0:
                counter_delete(key) # Must delete counter first before key, else Error 405
                key_delete(key)
        # Whether key exists in counter_store or not, both return string
        return bytes(byte_str)
        


def key_delete(key):
    if key_value_store.get(key) == None:
        return b"404 NotFound  "
    else: # If key exists
        if counter_store.get(key) != None:
            return b"405 MethodNotAllowed  "
        else:
            value = key_value_store.pop(key)
            byte_str = bytearray(b'200 OK content-length ')
            byte_str.extend(str(len(value)).encode())
            byte_str.extend(b"  ")
            byte_str.extend(value)
            return bytes(byte_str)


def counter_insert_update(key, counter):
    if key_value_store.get(key) == None: 
        return b"405 MethodNotAllowed  "
    else:
        counter_store[key] = counter_store.get(key, 0) + counter
        return b"200 OK  "

def counter_get(key):
    if counter_store.get(key) == None and key_value_store.get(key) == None:
        return b"404 NotFound  "
    elif counter_store.get(key) == None and key_value_store.get(key) != None:
        return b"200 OK content-length 8  Infinity"
    elif counter_store.get(key) != None:
        counter = counter_store.get(key)
        string = "200 OK content-length {}  {}".format(len(str(counter)), counter)
        return string.encode()

def counter_delete(key):
    if counter_store.get(key) == None:
        return "404 NotFound  "
    else:
        counter = counter_store.pop(key)
        string = "200 OK content-length {}  {}".format(len(str(counter)), counter)
        return string.encode()

### Parser for request

def parse_request(byte_arr):

    # print("byte_arr before:", byte_arr)
    while len(byte_arr) > 0:
        counter = 0
        req_string = bytes(byte_arr)
        two_space_split = req_string.split(b"  ", 1)
        if len(two_space_split) < 2: # If there's no double space
            break
        header = two_space_split[0]
        content_and_rest = two_space_split[1]
        header_space_split = header.split(b" ")
        method = header_space_split[0].upper()
        # print("method:", method)
        path = header_space_split[1]
        store_name = path.split(b"/")[1].lower()
        # print("store:", store_name)
        key_name = path.split(b"/")[2]
        # print("key:", key_name)
        if method == b"GET":
            if store_name == b"key":
                res = key_get(key_name)
            elif store_name == b"counter":
                res = counter_get(key_name)
            counter += len(header) + 2
        elif method == b"DELETE":
            if store_name == b"key":
                res = key_delete(key_name)
            elif store_name == b"counter":
                res = counter_delete(key_name)
            counter += len(header) + 2
        elif method == b"POST":
            content_len = 0
            for i in range(2, len(header_space_split)):
                if header_space_split[i].lower() == b"content-length":
                    try:
                        content_len = int(header_space_split[i+1])
                    except:
                        continue
                    # print("content len:", content_len)
            content = content_and_rest[0 : content_len]
            # print("content:", content)
            if len(content) < content_len: # Len of content is smaller than described content len
                break
            if store_name == b"key":
                res = key_insert_update(key_name, content)
            elif store_name == b'counter':
                res = counter_insert_update(key_name, int(content))
            counter += len(header) + 2 + content_len
        # print("Request:", byte_arr[0: counter])
        del byte_arr[0: counter]
        # print("byte_arr after: ", byte_arr)
        yield res
    


### Network
byte_arr = bytearray()
serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))


while True:
    serverSocket.listen()
    #print("Server listening")
    connectionSocket, clientAddr = serverSocket.accept()
    while True:
        request = connectionSocket.recv(2048)
        if not request:
            break
        byte_arr.extend(request)
        response_generator = parse_request(byte_arr)
        while True:
            try:
                response = next(response_generator)
                # print("Response:", response)
                connectionSocket.sendall(response)
            except StopIteration:
                break
    connectionSocket.close()
    #print("Client connection closed")
