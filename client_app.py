import socket
import sys

buffsize = 32

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print('connecting to %s port %s' % server_address)
sock.connect(server_address)

# Send data
with open ("/home/katsanis/Desktop/tst2", "r") as myfile:
    for message in myfile:
        print('sending ', message)
        sock.send(message.encode())

print('closing socket')
sock.close()
