import socket
import time

UDP_IP = "172.19.12.67"  # Replace with your laptop's IP
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for i in range(100):
    message = f"Hello #{i} from Pi Zero"
    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
    print("Sent:", message)
    time.sleep(5)