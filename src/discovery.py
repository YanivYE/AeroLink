from zeroconf import Zeroconf, ServiceBrowser
import socket
import time

from src.constants import SERVICE_TYPE

IPV4_ADDRESS_LENGTH = 4

discovered_devices = {}

def get_ipv4_address(info):
    for addr in info.addresses:
        if len(addr) == IPV4_ADDRESS_LENGTH:
            return socket.inet_ntoa(addr)
    return None

class Listener:
    def __init__(self, on_device_discovered=None):
        self.on_device_discovered = on_device_discovered

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            ip = get_ipv4_address(info)
            if not ip:
                return

            port = info.port
            device = info.properties.get(b'device', b'').decode()
            if not device:
                device = name  # fallback to service name

            local_ip = socket.gethostbyname(socket.gethostname())
            if ip == local_ip:
                return  # Skip self

            discovered_devices[device] = (ip, port)
            if self.on_device_discovered:
                self.on_device_discovered(device, ip, port)

    def remove_service(self, zeroconf, type, name):
        # Optional cleanup logic
        pass

    def update_service(self, zeroconf, type, name):
        # Not used currently
        pass

def start_discovery(timeout, on_device_discovered=None):
    discovered_devices.clear()

    zeroconf = Zeroconf()
    listener = Listener(on_device_discovered=on_device_discovered)
    ServiceBrowser(zeroconf, SERVICE_TYPE, listener)

    try:
        if timeout is None:
            while True:
                time.sleep(1)
        else:
            time.sleep(timeout)
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()
