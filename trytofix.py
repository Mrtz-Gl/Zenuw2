from smbus2 import SMBus
from ahrs.filters import Madgwick
import numpy as np
import time
import socket

UDP_IP = "192.168.18.223"  # Replace with your laptop's IP
UDP_PORT = 5005
starttime = time.time()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# MPU6050 Register Addresses
MPU_ADDRS = [0x68, 0x69]
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# I2C Bus Configuration
i2c_buses = [0, 1]  # /dev/i2c-0 and /dev/i2c-1
mpus = []

# Initialize each MPU
for bus_num in i2c_buses:
    bus = SMBus(bus_num)
    for addr in MPU_ADDRS:
        try:
            bus.write_byte_data(addr, PWR_MGMT_1, 0)
            mpus.append((bus_num, addr))
            print(f"Initialized MPU at address 0x{addr:02X} on bus {bus_num}")
        except Exception as e:
            print(f"Failed to init MPU at 0x{addr:02X} on bus {bus_num}: {e}")

# Functions
def read_word(bus, addr, reg):
    high = bus.read_byte_data(addr, reg)
    low = bus.read_byte_data(addr, reg + 1)
    val = (high << 8) + low
    if val >= 0x8000:
        val -= 0x10000
    return val

def get_program_time():
    return time.time() - starttime

def send_over_socket(programtime, imu):
    row = f"{programtime}"
    for key, value in imu.items():
        row += f", {value}"
    print(row)
    sock.sendto(row.encode(), (UDP_IP, UDP_PORT))

def quaternion_to_euler(q):
    q0, q1, q2, q3 = q
    roll = np.arctan2(2 * (q0*q1 + q2*q3), 1 - 2 * (q1**2 + q2**2)) * 57.3
    pitch = np.arcsin(2 * (q0*q2 - q3*q1)) * 57.3
    yaw = np.arctan2(2 * (q0*q3 + q1*q2), 1 - 2 * (q2**2 + q3**2)) * 57.3
    return roll, pitch, yaw

def dict_writer(addr, bus_num, programtime, q, accel, gyro):
    roll, pitch, yaw = quaternion_to_euler(q)
    return {
        'addr': addr,
        'bus_num': bus_num,
        'programtime': programtime,
        'roll': roll,
        'pitch': pitch,
        'yaw': yaw,
        'Accel': accel.tolist(),
        'Gyro': gyro.tolist()
    }

# Set up reusable SMBus handles
buses = {bus_num: SMBus(bus_num) for bus_num, _ in mpus}

# Set up one Madgwick filter and quaternion per sensor
filters = {}
quaternions = {}
for bus_num, addr in mpus:
    key = (bus_num, addr)
    filters[key] = Madgwick()
    quaternions[key] = np.array([1.0, 0.0, 0.0, 0.0])  # initial quaternion

# Main loop
try:
    while True:
        for bus_num, addr in mpus:
            bus = buses[bus_num]
            ax = read_word(bus, addr, ACCEL_XOUT_H)
            ay = read_word(bus, addr, ACCEL_XOUT_H + 2)
            az = read_word(bus, addr, ACCEL_XOUT_H + 4)
            gx = read_word(bus, addr, GYRO_XOUT_H)
            gy = read_word(bus, addr, GYRO_XOUT_H + 2)
            gz = read_word(bus, addr, GYRO_XOUT_H + 4)

            accel = np.array([ax, ay, az], dtype=float)
            gyro = np.radians(np.array([gx, gy, gz], dtype=float))

            if np.linalg.norm(accel) != 0:
                accel_norm = accel / np.linalg.norm(accel)
            else:
                accel_norm = accel

            key = (bus_num, addr)
            q = quaternions[key]
            madgwick_filter = filters[key]

            q = madgwick_filter.updateIMU(q, gyro, accel_norm)
            quaternions[key] = q  # update the stored quaternion

            if q is not None:
                programtime = get_program_time()
                data_dict = dict_writer(addr, bus_num, programtime, q, accel, gyro)
                sock.sendto(str(data_dict).encode(), (UDP_IP, UDP_PORT))
            else:
                print(f"No quaternion output from filter for device {addr} on bus {bus_num}")

except KeyboardInterrupt:
    print("Stopping...")
finally:
    for bus in buses.values():
        bus.close()