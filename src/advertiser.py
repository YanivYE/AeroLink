from http.client import HTTP_PORT
import socket
from zeroconf import ServiceInfo, Zeroconf
from src.constants import GOOGLE_DNS_IP, SERVICE_TYPE, SERVICE_NAME, DEFAULT_PORT, DEVICE_NAME

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((GOOGLE_DNS_IP, HTTP_PORT))  # Use a public DNS server to determine the local IP
        return s.getsockname()[0]
    finally:
        s.close()

def get_device_name():
    try:
        # Try to get the hostname, fallback to DEVICE_NAME constant if empty or fails
        pc_name = socket.gethostname()
        if pc_name and pc_name.strip():
            return pc_name
    except Exception:
        pass
    return DEVICE_NAME

def start_advertising(port=DEFAULT_PORT):
    device_name = get_device_name()
    desc = {'device': device_name}
    
    info = ServiceInfo(
        SERVICE_TYPE,
        SERVICE_NAME,
        addresses=[socket.inet_aton(get_ip())],
        port=port,
        properties=desc,
        server="{}.local.".format(device_name.lower())  # use device_name as server name
    )

    zeroconf = Zeroconf()
    zeroconf.register_service(info)
    print(f"[+] Advertising as {device_name} on {get_ip()}:{port}")
    return zeroconf
