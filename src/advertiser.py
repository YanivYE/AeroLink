from zeroconf import ServiceInfo, Zeroconf
import socket
from constants import SERVICE_TYPE, SERVICE_NAME, DEFAULT_PORT, DEVICE_NAME

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

def start_advertising(port=DEFAULT_PORT):
    desc = {'device': DEVICE_NAME}
    info = ServiceInfo(
        SERVICE_TYPE,
        SERVICE_NAME,
        addresses=[socket.inet_aton(get_ip())],
        port=port,
        properties=desc,
        server="aerolink.local."
    )

    zeroconf = Zeroconf()
    zeroconf.register_service(info)
    print(f"[+] Advertising as {SERVICE_NAME} on {get_ip()}:{port}")
    return zeroconf
