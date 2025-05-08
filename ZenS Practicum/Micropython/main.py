import network
import time
import socket
import time

# Replace with your network details
ssid = 'TUD-facility'
password = '0b62dc191344e'

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connection
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    print('Waiting for connection...')
    time.sleep(1)
    max_wait -= 1

if wlan.status() != 3:
    raise RuntimeError('Wi-Fi connection failed')
else:
    print('Connected. IP:', wlan.ifconfig()[0])

# Set up UDP socket
UDP_IP = '172.19.12.67'
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send UDP packets
for i in range(1000):  # send 10 packets
    message = f"UDP hello #{i} from Pico W!"
    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
    print("Sent:", message)
    time.sleep(5)