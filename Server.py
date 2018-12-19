import asyncio
import socket
import threading
from config import DISCOVERY_PORT, DELIVERY_PORT, SELF_IP, OFFER_TIMEOUT, SERVER_WAIT_FOR_SCRIPT_TOLERANCE, MESSAGE_TIMEOUT, OFFER_PORT
from handlers import execute_script, send_probe_response
import select
from utils import change_style

class Task:
    def __init__(self, hash):
        self.hash = hash
        self.script = None
        self.limit = None
        self.offset = None
        self.result = None

    def get_result_message(self):
        message = "|".join([self.hash, self.result, self.offset, self.limit])
        return message.encode('utf_8')


class Server:
    def __init__(self,quant):
        self.busy = False
        self.loop = None
        self.task = None
        self.quant= quant
        self.lock = threading.Lock()
        self.task = None

    def set_busy(self):
        self.busy = True

    def timeout_after_offer(self, hash):
        if self.task is not None:
            if self.task.script is not None:
                return
            if self.task.hash == hash:
                self.busy = False
                self.task = None

    def timeout_after_execution(self, hash):
        if self.task is None:
            return
        if self.task.hash == hash:
            self.busy = False
            self.task = None

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

    def serve(self):
        #t = threading.Thread(target = self.start_server)
        #t.setDaemon(True)
        #t.start()
        asyncio.run(self.start_server())

    async def start_server(self):
        self.loop = asyncio.get_running_loop()
        server = await self.loop.create_server(
            lambda: OfferTakerProtocol(self),
            SELF_IP, OFFER_PORT)
        print("Started Offer Server")
        async with server:
            await server.serve_forever()

class OfferTakerProtocol(asyncio.Protocol):
    def __init__(self, server):
        self.server = server
        self.loop = server.loop

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.server.lock.acquire()
        try:
            if len(data.decode('utf_8').split("|")) == 2:
                msg = ""
                if self.server.busy:
                    msg += "BUSY|"
                else:
                    msg += "OK|"
                    self.server.set_busy()
                    self.loop.call_later(SERVER_WAIT_FOR_SCRIPT_TOLERANCE, self.server.timeout_after_offer,(hash,))
                    self.server.task = Task(data.decode('utf_8').split("|")[1])
                msg = msg + SELF_IP + "|" + str(self.server.quant)
                print("Received Script Offer")
                self.transport.write(msg.encode('utf_8'))
                self.transport.close()
            else:
                if self.server.task is None:
                    return
                print("Received Script Content")
                self.loop.call_later(self.server.quant + SERVER_WAIT_FOR_SCRIPT_TOLERANCE, self.server.timeout_after_execution,(self.server.task.hash,))
                self.server.task.hash, self.server.task.script, self.server.task.offset, self.server.task.limit = data.decode('utf_8').split("|")
                self.server.task.result = execute_script(self.server.task, self.server.quant)
                message = self.server.task.get_result_message()
                self.transport.write(message)
                self.server.task = None
                self.server.busy = False
                self.transport.close()

        except Exception as ex:
            print("Exception occured during data receive on Server: " + str(ex))
        finally:
            self.server.lock.release()


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
            if len(msg.split('|')) > 2:
                continue
            probe,received_from = msg.split('|')
            print("Received discovery request from:" + received_from)
            self.discovery_cb(received_from)


capacity = input("\n" + change_style("Enter the number of seconds that this server should spend for each execution", 'underline') + ": ")
s = Server(int(capacity))
s.start_discovery_handler()
s.serve()