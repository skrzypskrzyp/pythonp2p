import argparse
import random

from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from uuid import uuid4

parser = argparse.ArgumentParser(description="ncpoc")
parser.add_argument('--port_listen', type=int, default=5008)
parser.add_argument('--port_send', type=int, default=5009)

generate_nodeid = lambda: str(uuid4())
args = parser.parse_args()

print(args.port_listen)
print(args.port_send)


class P2PProtocol(Protocol):
    def __init__(self, factory):
        print("initializing protocol")
        self.factory = factory
        self.nodeid = self.factory.nodeid
        self.loopCall = LoopingCall(self.sendDummy)

    def sendDummy(self):
        print("sending dummy message")
        self.transport.write(b'DUMMY\r\n')

    def dataReceived(self, data):
        for line in data.splitlines():
            line = line.strip()
            print("received  " + str(line, 'utf-8'))
    
    def connectionMade(self):
        interval = random.randint(1, 10)
        print("connection from", self.transport.getPeer())
        print("will send dummy message every " + str(interval) + " seconds")
        self.loopCall.start(interval)

    def connectionLost(self, reason):
        print (self.nodeid +  " disconnected")

class P2PProtocolFactory(Factory):
    def __init__(self):
        self.peers = {}
        self.nodeid = generate_nodeid()
        print("initializing factory")

    def buildProtocol(self, addr):
        print("building protocol")
        return P2PProtocol(self)
        

def gotProtocol(protocol):
    procotol.send_dummy()

factory = P2PProtocolFactory()

#listener
try:
    serverEndpoint = TCP4ServerEndpoint(reactor, args.port_listen, interface="localhost")
    serverEndpoint.listen(factory)
except CannotListenError:
    print("Could not connect")
    raise SystemExit

#sender
clientEndpoint = TCP4ClientEndpoint(reactor, "localhost", int(args.port_send))
d = connectProtocol(clientEndpoint, P2PProtocol(factory))
d.addCallback(gotProtocol)

reactor.run()
