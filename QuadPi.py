from smbus2 import SMBus
from ahrs.filters import Madgwick
import numpy as np
import time
import socket

UDP_IP = "192.168.18.223"  # Replace with your laptop's IP
UDP_PORT = 5005
starttime = time.time()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
starttime = time.time()
# Initialise Madgwick filter (quarternion to euler)
madgwick_filter = Madgwick()
# MPU Registers
MPU_ADDRS = [0x68, 0x69]
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# Setup: Initialize each MPU on each bus
i2c_buses = [0, 1]  # /dev/i2c-0 and /dev/i2c-1
mpus = []

# Wake up MPUs
for bus_num in i2c_buses:
    bus = SMBus(bus_num)
    for addr in MPU_ADDRS:
        try:
            bus.write_byte_data(addr, PWR_MGMT_1, 0)  # Wake up
            mpus.append((bus_num, addr))
            print(f"Initialized MPU at address 0x{addr:02X} on bus {bus_num}")
        except Exception as e:
            print(f"Failed to init MPU at 0x{addr:02X} on bus {bus_num}: {e}")

def read_word(bus, addr, reg):
    """
    Reads a 16-bit signed value from two consecutive 8-bit registers 
    (accelerometer or gyroscope axes)
    """
    high = bus.read_byte_data(addr, reg)
    low = bus.read_byte_data(addr, reg + 1)
    val = (high << 8) + low
    if val >= 0x8000:
        val -= 0x10000
    return val

def get_program_time():
    """
     Computes the time elapsed since the program started
    """
    programtime = starttime - time.time() # moet dit nit anders om!
    return programtime

def send_over_socket(programtime, imu):
    # defined but not used
    """
    Converts IMU data into a comma-separated string and 
    sends it over the UDP socket
    """
    row = f"{programtime}"
    for key, value in imu.items():
        row += f", {value}"
    print(row)
    UDPMessage = sock.sendto(row.encode(), (UDP_IP, UDP_PORT))

def quaternion_to_euler(q):
    """
    Changes quarternion angles to euler angles
    """
    q0, q1, q2, q3 = q
    roll = np.arctan2(2 * (q0*q1 + q2*q3), 1 - 2 * (q1**2 + q2**2)) * 57.3
    pitch = np.arcsin(2 * (q0*q2 - q3*q1)) * 57.3
    yaw = np.arctan2(2 * (q0*q3 + q1*q2), 1 - 2 * (q2**2 + q3**2)) * 57.3
    return roll, pitch, yaw

def dict_writer(addr, bus_num, programtime, q):
    """
    creates a dictionary to be send to socket
    """
    roll, pitch, yaw = quaternion_to_euler(q)

    data_dict = {
        'addr': addr,
        'bus_num': bus_num,
        'programtime': programtime,
        'roll': roll,
        'pitch': pitch,
        'yaw': yaw,
        'Accel': [ax, ay, az],
        'Gyro': [gx, gy, gz]
    } 
    return data_dict

buses = {bus_num: SMBus(bus_num) for bus_num, _ in mpus}

# Loops through each MPU device, reads: Accelerometer and Gyroscope
# Sends the data via UDP as csv formatted string
try:
    while True:
        for bus_num, addr in mpus:
            bus = buses[bus_num]  # reuse opened bus
            ax = read_word(bus, addr, ACCEL_XOUT_H)
            ay = read_word(bus, addr, ACCEL_XOUT_H + 2)
            az = read_word(bus, addr, ACCEL_XOUT_H + 4)
            gx = read_word(bus, addr, GYRO_XOUT_H)
            gy = read_word(bus, addr, GYRO_XOUT_H + 2)
            gz = read_word(bus, addr, GYRO_XOUT_H + 4)
            programtime = get_program_time()

            ### ! ###
            ### Is normalizatie wel nodig? Wij willen toch de juiste accelratie data ####
            ### wordt atm ook niet gebruikt ###

            # Normalize accelerometer data
            accel = np.array([ax, ay, az])  # adjust scale as needed
            # accel_norm = np.linalg.norm(accel)
            gyro = np.radians(np.array([gx, gy, gz]))  # convert to rad/s
            # gyro_norm = np.linalg.norm(gyro)

            # Update AHRS filter
            q = madgwick_filter.updateIMU(gyro=gyro, acc=accel)

            if q is not None:
                data_dict = dict_writer(addr, bus_num, programtime, q)

                # Format and send
                datasend = str(data_dict)
                UDPMessage = sock.sendto(datasend.encode(), (UDP_IP, UDP_PORT))
            else: 
                print('q is none')

except KeyboardInterrupt:
    print("Stopping...")
finally:
# Always close the buses when done
    for bus in buses.values():
        bus.close()
