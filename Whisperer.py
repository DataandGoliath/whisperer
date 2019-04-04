import socket
from threading import *
import sys

global c2psock
global p2ssock

class c2s(Thread):
    def __init__(self,csocket, ssocket):
        Thread.__init__(self)

        self.clientsock = csocket
        self.serversock = ssocket
        c2psock = csocket

        self.start()

    def run(self):
        while True:
            clientbuf = self.clientsock.recv(4096)
            if str(clientbuf).strip("b''").strip(" ") != "":
                print("[C->S] {} | {}".format(str(clientbuf[:100]).encode("utf-8").hex(),str(clientbuf[:100])))
                self.serversock.send(clientbuf)
            clientbuf = ""

class s2c(Thread):
    def __init__(self,csocket, ssocket):
        Thread.__init__(self)

        self.clientsock = csocket
        self.serversock = ssocket

        p2ssock = self.serversock

        self.start()

    def run(self):
        while True:
            serverbuf = self.serversock.recv(4096)
            if str(serverbuf).strip("b''").strip(" ") != "":
                print("[S->C] {} | {}".format(str(serverbuf[:100]).encode("utf-8").hex(),str(serverbuf[:100])))
                self.clientsock.send(serverbuf)
            serverbuf = ""
try:
    proxyaddr = sys.argv[1]
    proxyport = int(sys.argv[2])
    serveraddr = sys.argv[3]
    serverport = int(sys.argv[4])
except:
    print("Usage:\nwhisperer.py [proxy-addr] [proxy-port] [server-addr] [server-port]")
    print("Example:\nwhisperer.py 0.0.0.0 80 website.com 80")
    exit()

print("Listening for input")

s = socket.socket()
c = socket.socket()

c.bind((proxyaddr,proxyport))
c.listen(5)
p,a = c.accept()
print("Got client")

s.connect((serveraddr,serverport))

print("Spawning threads")
c2s(p,s)
s2c(p,s)

