import socket
import grovepi

def Main():
    # Change the host and port as needed. For ports, use a number in the 9000 
    # range. 
    host = '192.168.1.210'
    port = 5000

    server_addr = '192.168.1.161'

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    s.bind((host,port))

    # UDP is connectionless, so a client does not formally connect to a server
    # before sending a message.
    dst_port = input("destination port-> ")
    while 1:
        #tuples are immutable so we need to overwrite the last tuple
        server = (server_addr, int(dst_port))
        message = grovepi.ultrasonicRead(8)
        # for UDP, sendto() and recvfrom() are used instead
        s.sendto(str(message).encode('utf-8'), server)
    s.close()

if __name__ == '__main__':
    Main()