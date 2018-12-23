import os
import socket
from string import Template
from config import DISCOVERY_PORT, MESSAGE_TIMEOUT, SERVER_WAIT_FOR_SCRIPT_TOLERANCE
from utils import PLATFORM


def execute_script(task, quant):
    file = open("register.py",'w')
    file.truncate(0)
    file.write(task.script)
    file.close()
    print("Executing the script with Offset: "+str(task.offset)+" Limit: "+str(task.limit))
    if PLATFORM == "mac":
        command = Template("gtimeout $quant python3 register.py $offset $limit").substitute(quant=str(quant),
                                                                                           offset=str(task.offset),
                                                                                           limit=str(task.limit))
    else:
        command = Template("timeout $quant python3 register.py $offset $limit").substitute(quant=str(quant),
                                                                                           offset=str(task.offset),
                                                                                           limit=str(task.limit))
    results = os.popen(command).read()
    return results

def probe_for_resources(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 0))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(("PROBE|"+ip).encode('utf_8'),('<broadcast>',DISCOVERY_PORT))
    sock.close()

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


