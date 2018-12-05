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
with open ("/home/katsanis/Desktop/input3", "r") as myfile:
    for message in myfile:
        print('sending ', message)
        sock.send(message.encode())

        """# Look for the response
        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            data = sock.recv(buffsize)
            amount_received += len(data)
            print('received "%s"' % data)"""

print('closing socket')
sock.close()
