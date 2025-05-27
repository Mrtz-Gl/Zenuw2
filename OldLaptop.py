import socket
import csv
import os
from datetime import datetime
from ahrs.filters import Madgwick
import numpy as np

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
imu_filters = {
    (104, 0): Madgwick(),
    (104, 1): Madgwick(),
    (105, 0): Madgwick(),
    (105, 1): Madgwick()
}
# Store last quaternion per IMU
imu_quaternions = {
    (104, 0): np.array([1.0, 0.0, 0.0, 0.0]),
    (104, 1): np.array([1.0, 0.0, 0.0, 0.0]),
    (105, 0): np.array([1.0, 0.0, 0.0, 0.0]),
    (105, 1): np.array([1.0, 0.0, 0.0, 0.0])
}


def get_csv_filename(addr, bus_num):
    return os.path.join(csv_folder, f"imu_{addr}_{bus_num}.csv")

def write_to_csv(addr, bus_num, data_row):
    filename = get_csv_filename(addr, bus_num)
    file_exists = os.path.isfile(filename)

    fieldnames = ['programtime', 'ax', 'ay', 'az', 'gx', 'gy', 'gz', 'q0', 'q1', 'q2', 'q3']
    with open(filename, mode='a', newline='') as csvfile:
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

        # Convert gyroscope to rad/s
        gyr = np.radians([gx, gy, gz])
        acc = np.array([ax, ay, az])

        # Use previous quaternion as input
        q_prev = imu_quaternions[key]
        filter = imu_filters[key]

        q_new = filter.updateIMU(q_prev, gyr=gyr, acc=acc)
        imu_quaternions[key] = q_new  # update stored quaternion

        data_row = {
            'programtime': programtime,
            'ax': ax,
            'ay': ay,
            'az': az,
            'gx': gx,
            'gy': gy,
            'gz': gz,
            'q0': q_new[0],
            'q1': q_new[1],
            'q2': q_new[2],
            'q3': q_new[3]
        }

        imu_data[key].append(data_row)
        write_to_csv(addr, bus_num, data_row)
        print(f"Data written for IMU {key} with quaternion")

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