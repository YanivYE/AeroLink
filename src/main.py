import time
from discovery import start_discovery, discovered_devices
from communication import send_message
from advertiser import start_advertising
from server import start_tcp_server

def choose_device():
    print("\nSelect a device to connect:")
    items = list(discovered_devices.items())
    for idx, (name, (ip, port)) in enumerate(items):
        print(f"{idx + 1}. {name} at {ip}:{port}")
    
    try:
        sel = int(input("> ")) - 1
        ip, port = items[sel][1]
        msg = input("Enter message to send: ")
        send_message(ip, port, msg)
    except:
        print("[!] Invalid selection.")

def main():
    print("🚀 AeroLink")
    print("\nChoose mode:")
    print("1. Discover other devices and send message")
    print("2. Passive mode - wait for others to find you")
    choice = input("> ")

    if choice == "1":
        devices = start_discovery(timeout=10)
        if not devices:
            print("[!] No devices found.")
        else:
            choose_device()
    else:
        start_tcp_server()
        print("[~] Passive mode active. Waiting for incoming connections...")
        zeroconf = start_advertising()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[~] Shutting down...")
            zeroconf.close()

if __name__ == "__main__":
    main()
