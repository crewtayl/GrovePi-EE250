# LED Server
# 
# This program runs on the Raspberry Pi and accepts requests to turn on and off
# the LED via TCP packets.

import sys
# By appending the folder of all the GrovePi libraries to the system path here,
# we are successfully `import grovepi`
sys.path.append('../../Software/Python/')


# use TCP
"""Example python3 server side socket program using UDP adopted from the 
video tutorial below.
https://www.youtube.com/watch?v=bTThyxVy7Sk&index=6&list=PL1A2CSdiySGIPxpSlgzsZiWDavYTAx61d
"""
import groovepi
import socket

def Main():
    host = '192.168.1.210'
    port = 9000

    s = socket.socket()
    s.bind((host,port))
    s.listen(1)
    c, addr = s.accept()
    print("Connection from: " + str(addr))
    while True:
        data = c.recv(1024).decode('utf-8')
        print("From connected user: " + data)
        data = data.upper()
        print("Sending: " + data)
        if data == "LED_ON":
            digitalWrite(3,1)
            print("LED_ON")
        if data == "LED_OFF":
            digitalWrite(3,0)
            print("LED_OFF")
        c.send(data.encode('utf-8'))
    c.close()

if __name__ == '__main__':
    Main()