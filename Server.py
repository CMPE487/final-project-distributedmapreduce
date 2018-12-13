import asyncio
import socket
import threading
from config import DISCOVERY_PORT, DELIVERY_PORT, SELF_IP, OFFER_TIMEOUT, SERVER_WAIT_FOR_SCRIPT_TOLERANCE, MESSAGE_TIMEOUT
from handlers import execute_script, send_probe_response
import select

class Task:
    def __init__(self, hash):
        self.hash = hash
        self.script = None
        self.limit = None
        self.offset = None

    def execute(self):
        results = execute_script(self.script, self.offset, self.limit)
        return results

class Server:
    def __init__(self):
        self.busy = False
        self.loop = asyncio.get_running_loop()
        self.task = None
        self.quant= None
        self.lock = threading.Lock()
        self.task = None

    def set_busy(self):
        self.busy = True

    def set_available(self):
        if self.task is not None:
            if self.task.script is not None:
                return
        self.busy = False

    def start_discovery_handler(self):
        disc_thread = DiscoveryHandler(self.send_probe_response)
        disc_thread.setDaemon(True)
        disc_thread.start()

    def send_probe_response(self, receiver_ip):
        msg = "HERE|"
        msg += SELF_IP + "|" + str(self.quant)
        msg = msg.encode('utf_8')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
            try:
                server.settimeout(MESSAGE_TIMEOUT)
                server.connect((receiver_ip, DISCOVERY_PORT))
                server.sendall(msg)
            except Exception as ex:
                print("Error occured while sending the discovery response", ex)
                return
            finally:
                server.close()

class OfferTakerProtocol(asyncio.Protocol):
    def __init__(self, server,loop):
        self.server = server
        self.loop = loop

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):

        self.server.lock.acquire()
        if len(data.decode('|')) == 2:
            try:
                msg = ""
                if self.server.busy:
                    msg += "BUSY"
                else:
                    msg += "OK"
                    self.server.set_busy()
                    self.loop.call_later(SERVER_WAIT_FOR_SCRIPT_TOLERANCE,self.server.set_available)
                    #TODO Create empty task with the hast get from data decode
                self.transport.write("OK|" + SELF_IP +"|" + str(self.server.quant))
                self.transport.close()
            except Exception as ex:
                print("Error occured while sending offer response client: " + str(ex))
            finally:
                self.server.lock.release()
        else:
            self.server.lock()
            #TODO execution logic


class DiscoveryHandler(threading.Thread):
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
            probe,received_from = msg.split('|')
            self.discovery_cb(received_from)