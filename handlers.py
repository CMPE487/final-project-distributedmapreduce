import os
import socket
from config import DISCOVERY_PORT, MESSAGE_TIMEOUT


def execute_script(script, offset, limit):
    file = open("register.py",'wb')
    file.truncate(0)
    file.write(script)
    file.close()
    results = os.popen("python3 register.py " + offset + " " + limit).read().split("\n")
    return results

def probe_for_resources(ip):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(1)
    server.bind(("",DISCOVERY_PORT))
    server.sendto(("PROBE|"+ip).encode('utf_8'),('<broadcast>',DISCOVERY_PORT))
    server.close()

def send_disconnect_message(ip):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(1)
    server.bind(("", DISCOVERY_PORT))
    server.sendto(("PROBE|"+ip).encode('utf_8'), ('<broadcast>', DISCOVERY_PORT))
    server.close()

def send_probe_response(self_ip, receiver_ip, quant):
    msg = "HERE|"
    msg += self_ip + "|" + str(quant)
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


