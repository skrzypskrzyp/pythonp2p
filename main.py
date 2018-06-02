import argparse

from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
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

    def sendDummy(self):
        print("sending dummy message")

        self.transport.write("DUMMY\n")

    def dataReceived(self, data):
        for line in data.splitlines():
            line = line.strip()
            print("RECEIVED " + line)
    
    def connectionMade(self):
        print("Connection from", self.transport.getPeer())

    def connectionLost(self, reason):
        if self.remote_nodeid in self.factory.peers:
            self.factory.peers.pop(self.remote_nodeid)
        print (self.nodeid +  " disconnected")

class P2PProtocolFactory(Factory):
    def __init__(self):
        self.peers = {}
        self.nodeid = generate_nodeid()
        print("initializing factory")

    def buildProtocol(self, addr):
        print("Building protocol")
        return P2PProtocol(self)
        

def gotProtocol(protocol):
    procotol.send_dummy()

factory = P2PProtocolFactory()

#listener
try:
    serverEndpoint = TCP4ServerEndpoint(reactor, args.port_listen, interface="localhost")
    serverEndpoint.listen(factory)
except CannotListenError:
    print("[!] Address in use")
    raise SystemExit

#sender
clientEndpoint = TCP4ClientEndpoint(reactor, "localhost", args.port_send)
d = connectProtocol(clientEndpoint, P2PProtocol(factory))
d.addCallback(gotProtocol)

reactor.run()
