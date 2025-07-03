import socket
from zeroconf import Zeroconf, ServiceBrowser
from src.constants import SERVICE_TYPE

discovered_devices = {}

class DeviceDiscoveryListener:
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            ip = ".".join(map(str, info.addresses[0]))
            port = info.port
            device_name = info.properties.get(b'device', b'').decode()

            local_ip = socket.gethostbyname(socket.gethostname())
            if ip == local_ip:
                return  # Skip self

            print(f"[>] Found: {device_name} at {ip}:{port}")
            discovered_devices[name] = (device_name, ip, port)

    def remove_service(self, zeroconf, type, name):
        if name in discovered_devices:
            print(f"[x] Device went offline: {name}")
            discovered_devices.pop(name)

    def update_service(self, zeroconf, type, name):
        pass  # Required by Zeroconf

def start_discovery(timeout=10):
    zeroconf = Zeroconf()
    listener = DeviceDiscoveryListener()
    browser = ServiceBrowser(zeroconf, SERVICE_TYPE, listener)

    print(f"[~] Browsing for {timeout} seconds...")
    try:
        import time
        time.sleep(timeout)
    finally:
        zeroconf.close()

    return discovered_devices
