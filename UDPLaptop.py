import socket

UDP_IP = "0.0.0.0"     # Listen on all interfaces
UDP_PORT = 5005        # Must match Pico's send port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP messages on port {UDP_PORT}...")

try:
    while True:
        data, addr = sock.recvfrom(1024)
        i2caddr, bus_num, programtime, ax, ay, az, gx, gy, gz = data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]
        print(f"Received from {addr}: {data.decode()}")
except KeyboardInterrupt:
        print("Stopping")
    