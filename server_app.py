import socket
import sys

buffsize = 32

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()

    print('connection from', client_address)

    # Receive the data in small chunks and save it
    f = open("/home/katsanis/Desktop/tst22","a")
    while True:
        data = connection.recv(buffsize)
        f.write(data.decode())
        if not data:
            print('no more data from', client_address)
            break


    # Clean up the connection
    connection.close()
