import socket


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


SELF_IP = get_ip()
DISCOVERY_PORT = 5000  #UDP
OFFER_PORT = 5001 #TCP
DELIVERY_PORT = 5002  #TCP
OFFER_TIMEOUT= 5  #Seconds
MESSAGE_TIMEOUT = 2  #Seconds
SUBNET = ".".join(SELF_IP.split('.')[:3])

