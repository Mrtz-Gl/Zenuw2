import socket
import csv
import os
from datetime import datetime

# Create output directory based on program start time
starttime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_folder = os.path.join("csv", starttime)
os.makedirs(csv_folder, exist_ok=True)

imu_data = {
    (104, 0): [],
    (104, 1): [],
    (105, 0): [],
    (105, 1): []
}

def get_csv_filename(addr, bus_num):
    return os.path.join(csv_folder, f"imu_{addr}_{bus_num}.csv")

def write_to_csv(addr, bus_num, data_row):
    filename = get_csv_filename(addr, bus_num)
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as csvfile:
        fieldnames = ['programtime', 'ax', 'ay', 'az', 'gx', 'gy', 'gz']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(data_row)

def process_udp_data(datasend):
    try:
        parts = datasend.strip().split(',')
        if len(parts) != 9:
            print("Invalid data format")
            return

        addr = int(parts[0].strip())
        bus_num = int(parts[1].strip())
        programtime = float(parts[2].strip())
        ax = float(parts[3].strip())
        ay = float(parts[4].strip())
        az = float(parts[5].strip())
        gx = float(parts[6].strip())
        gy = float(parts[7].strip())
        gz = float(parts[8].strip())

        key = (addr, bus_num)

        if key not in imu_data:
            print(f"Unknown IMU address/bus: {key}")
            return

        data_row = {
            'programtime': programtime,
            'ax': ax,
            'ay': ay,
            'az': az,
            'gx': gx,
            'gy': gy,
            'gz': gz
        }

        imu_data[key].append(data_row)
        write_to_csv(addr, bus_num, data_row)
        print(f"Data written for IMU {key}")

    except ValueError as e:
        print(f"Error parsing data: {e}")

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP messages on port {UDP_PORT}...")

while True:
    try:
        data, addr = sock.recvfrom(1024)
        print(f"{data.decode()}")
        process_udp_data(data.decode())
    except KeyboardInterrupt:
        print("Stopping")
        break