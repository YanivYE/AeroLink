from zeroconf import Zeroconf, ServiceBrowser
import socket
import time

SERVICE_TYPE = "_aerolink._tcp.local."
discovered_devices = {}

class Listener:
    def __init__(self, on_device_discovered=None):
        self.on_device_discovered = on_device_discovered

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            ip = ".".join(map(str, info.addresses[0]))
            port = info.port
            device = info.properties.get(b'device', b'').decode()

            local_ip = socket.gethostbyname(socket.gethostname())
            if ip == local_ip:
                return  # Skip self

            discovered_devices[device] = (ip, port)
            if self.on_device_discovered:
                self.on_device_discovered(device, ip, port)

    def remove_service(self, zeroconf, type, name):
        pass  # Optional cleanup

    def update_service(self, zeroconf, type, name):
        pass  # Not used

def start_discovery(timeout=5, on_device_discovered=None):
    zeroconf = Zeroconf()
    listener = Listener(on_device_discovered=on_device_discovered)
    browser = ServiceBrowser(zeroconf, SERVICE_TYPE, listener)

    time.sleep(timeout)
    zeroconf.close()
