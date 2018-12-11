import asyncio
import socket
from string import ascii_letters
import random
import threading
import hashlib
import select
from config import DISCOVERY_PORT,DELIVERY_PORT, SELF_IP, SUBNET, OFFER_TIMEOUT, OFFER_PORT
import math

class OfferMaker:
    def __init__(self,ip,quant):
        self.ip = ip
        self.quant = quant
        self.limit = None
        self.offset = None
        self.response = None

class Offer:
    def __init__(self, filename, required_quant, num_operations):
        self.filename = filename
        self.required_quant = required_quant
        self.num_operations = num_operations
        self.md5 = self.get_md5()
        self.content = self.get_script_content()
        self.offer_takers = []


    def set_distributions(self):
        quants = [taker.quant for taker in self.offer_takers]
        assigned_ops = [math.ceil((self.num_operations/ sum(quants)) * quant) for quant in quants]
        curr_offset = 0
        for i in range(len(self.offer_takers)):
            taker = self.offer_takers[i]
            taker.offset= curr_offset
            taker.limit = assigned_ops[i]
            curr_offset += taker.limit
        excess = sum(assigned_ops) - self.num_operations
        self.offer_takers[-1].limit -= excess

    def is_satisfied(self):
        available_quant = sum([maker.quant for maker in self.offer_takers])
        if available_quant >= self.required_quant:
            return True
        else:
            return False

    def get_script_content(self):
        script = open(self.filename, 'rb')
        try:
            content = script.read()
            return content
        except Exception as ex:
            print("Exception occured while reading script file. Info: " + str(ex))
            #TODO print in UI
            return None
        finally:
            script.close()

    def get_md5(self):
        script = open(self.filename, 'rb')
        try:
            content = script.read()
            return hashlib.md5(content).hexdigest()
        except Exception as ex:
            print("Exception occured while reading script file. Info: " + str(ex))
            # TODO print in UI
            return None
        finally:
            script.close()

class Client:
    def __init__(self):
        self.loop = asyncio.get_running_loop()
        self.available_servers = {}
        self.loop = None
        self.offer = None

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

    def broadcast_script_offer(self, filename, required_quant, num_operations):
        asyncio.run(self.start_offer_broadcast(filename, required_quant, num_operations))

    async def start_offer_broadcast(self, filename, required_quant, num_operations):
        self.loop = asyncio.get_event_loop()
        self.offer = Offer(filename, required_quant)
        promises = []
        for ip, offer_maker in self.available_servers:
            server = OfferClientProtocol(self.loop, self.offer)
            _ , _ = await self.loop.create_connection(
            lambda: server, ip, OFFER_PORT)
            promises.append(server.conn_lost)
            self.loop.call_later(OFFER_TIMEOUT, server.connection_lost)
        await asyncio.gather(*[promises]) # "Wait for all of the connections to return"
        if self.offer.is_satisfied():
            #TODO Display Success on UI Start sending offer
            self.send_script()
        else:
            #TODO Display error in UI
            self.offer = None
            return

    def send_script(self):
        asyncio.run(self.start_script_protocol())

    async def start_script_protocol(self):
        #Burada connectionları aç
        await asyncio.sleep(1)

class OfferClientProtocol(asyncio.Protocol):

    def __init__(self, loop, offer):
        self.loop = loop
        self.offer= offer
        self.transport = None
        self.conn_lost = loop.create_future()

    def connection_made(self, transport):
        bcast_message =  ("PROBE|" + self.offer.md5 ).encode('utf_8')
        transport.write(bcast_message)

    def connection_lost(self, exc):
        self.conn_lost.set_result(True)

    def data_received(self, data, addr):
        if addr[0]==SELF_IP:
            return
        status, ip, time_quant = data.split("|")
        if status == "BUSY":
            return
        elif status == "OK":
            self.offer.offer_takers.append(OfferMaker(ip,time_quant))
        self.conn_lost.set_result(True)

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

class OfferScriptProtocol(asyncio.Protocol):
    #TODO use this class with timeout quant + tolerance and gather all the responses to print to UI
    def __init__(self, loop, offer, index):
        self.loop = loop
        self.offer= offer
        self.index = index
        self.transport = None
        self.conn_lost = loop.create_future()
        self.offer_taker = self.offer.offer_takers[index]

    def connection_made(self, transport):
        message =  [self.offer.md5, self.offer.content, str(self.offer_taker.offset), str(self.offer_taker.limit)]
        message = "|".join(message)
        message = message.encode('utf_8')
        transport.write(message)

    def connection_lost(self, exc):
        self.conn_lost.set_result(True)

    def data_received(self, data, addr):
        if addr[0]==SELF_IP:
            return
        status, ip, time_quant = data.split("|")
        if status == "BUSY":
            return
        elif status == "OK":
            self.offer.offer_takers.append(OfferMaker(ip,time_quant))
