from socket import *

serverName = 'localhost'
serverPort = 2106

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
is_continue = True

while is_continue:
    message = input('Enter Request: ')
    clientSocket.send(message.encode())
    receivedMsg = clientSocket.recv(2048)
    print('Response: ', receivedMsg.decode())
    is_continue_str = input('Continue?')
    if is_continue_str == 'y':
        is_continue = True
    else:
        is_continue = False
clientSocket.close()