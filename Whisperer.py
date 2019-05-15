import socket
from threading import *
import sys
from queue import Queue

logqueue = Queue()

class c2s(Thread):
    def __init__(self,csocket, ssocket,logqueue,logging):
        Thread.__init__(self)

        self.clientsock = csocket
        self.serversock = ssocket
        c2psock = csocket
        self.logqueue = logqueue
        self.logging = logging

        self.start()

    def hexify(self,string):
        hexstring = ""
        if str(string)[:2]=="b'":
            string=string[2:]

        for char in string:
            hexstring+=hex(ord(str(chr(char)))).replace("0x","")
            hexstring+=" "
        
        hexstring=str(hexstring)
        return hexstring[:-3]

    def run(self):
        while True:
            clientbuf = self.clientsock.recv(4096)
            presentbuf = clientbuf#.strip("\r").strip("\n")
            #presentbuf = presentbuf.decode('ascii')
            
            if str(clientbuf).strip("b''").strip(" ") != "":
                
                hexbuf = self.hexify(clientbuf)

                print("[C->S] {} | {}".format(str(hexbuf),str(presentbuf)[2:-1]))#str(clientbuf[:100]).encode("utf-8").hex(),str(clientbuf[:100])))
                #if you want to modify clientbuf, do it here
                self.serversock.send(clientbuf)
                
                if self.logging:
                    combined = "[C->S] " + str(hexbuf) + " | " + str(presentbuf)[2:-1]
                    self.logqueue.put(combined)

            clientbuf = ""

class s2c(Thread):
    def __init__(self,csocket, ssocket,logqueue,logging):
        Thread.__init__(self)

        self.clientsock = csocket
        self.serversock = ssocket
        self.logqueue = logqueue
        self.logging = logging
        p2ssock = self.serversock

        self.start()

    def hexify(self,string):
        hexstring = ""
        if str(string[:2])=="b'":
            string=string[2:]
        
        for char in string:
            hexstring+=hex(ord(str(chr(char)))).replace("0x","")
            hexstring+=" "
        hexstring=str(hexstring)
        return hexstring[:-3]

    def run(self):
        while True:
            serverbuf = self.serversock.recv(4096)
            presentbuf = serverbuf
            
            if str(serverbuf).strip("b''").strip(" ") != "":
                
                hexbuf = self.hexify(serverbuf)

                print("[S->C] {} | {}".format(str(hexbuf),str(presentbuf)[2:-1]))
                #If you want to mod serverbuf, do it here
                self.clientsock.send(serverbuf)
                
                if self.logging:
                    combined = "[S->C] " + str(hexbuf) + " | " + str(presentbuf)[2:-1]
                    self.logqueue.put(combined)
            serverbuf = ""
try:
    proxyaddr = sys.argv[1]
    proxyport = int(sys.argv[2])
    serveraddr = sys.argv[3]
    serverport = int(sys.argv[4])
except:
    print("Usage:\nwhisperer.py [proxy-addr] [proxy-port] [server-addr] [server-port] (logfile)")
    print("Example:\nwhisperer.py 0.0.0.0 80 website.com 80")
    print("whisperer.py 0.0.0.0 80 loggedexample.com 80 proxylog.txt")
    exit()

logging = True
try:
    logfile = sys.argv[5]
except:
    logfile = None
    logging = False

print("Listening for input")

s = socket.socket()
c = socket.socket()

c.bind((proxyaddr,proxyport))
c.listen(5)
p,a = c.accept()
print("Got client")

s.connect((serveraddr,serverport))

if logging:
    print("Logging entries to {}! Remember to press CTRL+C before exiting!".format(logfile))
print("Spawning threads")

c2s(p,s,logqueue,logging)
s2c(p,s,logqueue,logging)

if logfile:
    f = open(logfile,"a")
    try:
        while True:
            if not logqueue.empty():
                f.write(logqueue.get())
                f.write("\n")
                logqueue.task_done()
    except KeyboardInterrupt:
        f.close()
        print("Logging complete. Safe to close.")

