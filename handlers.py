import os
import socket
from config import DISCOVERY_PORT


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
    server.sendto("PROBE|"+ip,('<broadcast>',DISCOVERY_PORT))
    server.close()

def send_disconnect_message(ip):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(1)
    server.bind(("", DISCOVERY_PORT))
    server.sendto("DISCONNECTED|" + ip, ('<broadcast>', DISCOVERY_PORT))
    server.close()

