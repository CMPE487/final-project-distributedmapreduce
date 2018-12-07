import asyncio
import socket
from string import ascii_letters
import random
import threading
import select
from config import DISCOVERY_PORT,DELIVERY_PORT, SELF_IP, SUBNET, OFFER_TIMEOUT

class OfferMaker:
    def __init__(self,ip,quant):
        self.ip = ip
        self.quant = quant

class Client:
    def __init__(self):
        self.loop = asyncio.get_running_loop()
        self.available_servers = {}
        self.loop = None

    def start_probe_listener(self):
        disc_thread = DiscoveryListener(self.probe_returned)
        disc_thread.setDaemon(True)
        disc_thread.start()

    def probe_returned(self,status, ip, quant):
        if status == "OK":
            self.available_servers[ip] = OfferMaker(ip,quant)
        else:
            self.available_servers.pop(ip, None)
        #TODO update UI

    def broadcast_script_offer(self):
        asyncio.run(self.start_offer_broadcast())

    async def start_offer_broadcast(self, filename, required_quant):
        self.loop = asyncio.get_event_loop()
        server = BroadcastProtocol(self.loop)
        coro = await self.loop.create_datagram_endpoint(
            lambda: server, local_addr=('0.0.0.0', 9000))
        await server.conn_lost
        available_quant = sum([server.offer_acceptors[item].quant for item in server.offer_acceptors])
        if available_quant < required_quant:
            #TODO Pop Error in UI Thread
            return
        self.send_script(filename, server.offer_acceptors)

    def send_script(self, filename, available_servers):
        pass
    #TODO send the file to the adams
    #TCP ile gönder hepsine ayrı ayrı sonra bi tcp serverda dinle

class BroadcastProtocol:

    def __init__(self, loop, required_quant):
        self.loop = loop
        self.transport = None
        self.required_quant = required_quant
        self.offer_acceptors = {}
        self.conn_lost = loop.create_future()

    def connection_made(self, transport):
        print('started')
        self.transport = transport
        sock = transport.get_extra_info("socket")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def datagram_received(self, data, addr):
        if addr[0]==SELF_IP:
            return
        print(self.transport)
        status, time_quant = data.split("|")
        if status == "BUSY":
            return
        elif status == "OK":
            self.offer_acceptors[addr[0]] = OfferMaker(addr[0],int(time_quant))

    def broadcast(self):
        string = ''.join([random.choice(ascii_letters) for _ in range(5)])
        print('sending:', string)
        self.transport.sendto(string.encode(), (SUBNET+'.255', DELIVERY_PORT))
        self.loop.call_later(OFFER_TIMEOUT, self.conn_lost.set_result, (True,))


class DiscoveryListener(threading.Thread):
    def __init__(self, discovery_cb):
        threading.Thread.__init__(self)
        self.discovery_cb = discovery_cb
        self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('initializing discovery thread')

    def run(self):
        self.discovery_socket.bind(('', DISCOVERY_PORT))
        self.discovery_socket.setblocking(0)
        while True:
            result = select.select([self.discovery_socket], [], [])
            msg = result[0][0].recv(1024)
            msg = msg.decode('utf_8')
            status,received_from, quant = msg.split('|')
            quant = int(quant)
            self.discovery_cb(status,received_from, quant)
