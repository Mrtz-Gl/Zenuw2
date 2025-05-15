from smbus2 import SMBus
import time
import socket

UDP_IP = "192.168.178.63"  # Replace with your laptop's IP
UDP_PORT = 5005
starttime = time.time()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
starttime = time.time()
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
    high = bus.read_byte_data(addr, reg)
    low = bus.read_byte_data(addr, reg + 1)
    val = (high << 8) + low
    if val >= 0x8000:
        val -= 0x10000
    return val

def get_program_time():
    programtime = starttime - time.time()
    return programtime

def send_over_socket(programtime, imu):
    row = f"{programtime}"
    for key, value in imu.items():
        row += f", {value}"
    print(row)
    UDPMessage = sock.sendto(row.encode(), (UDP_IP, UDP_PORT))

# Main loop
try:
    while True:
        for bus_num, addr in mpus:
            bus = SMBus(bus_num)
            ax = read_word(bus, addr, ACCEL_XOUT_H)
            ay = read_word(bus, addr, ACCEL_XOUT_H + 2)
            az = read_word(bus, addr, ACCEL_XOUT_H + 4)
            gx = read_word(bus, addr, GYRO_XOUT_H)
            gy = read_word(bus, addr, GYRO_XOUT_H + 2)
            gz = read_word(bus, addr, GYRO_XOUT_H + 4)
            print(f"Bus {bus_num}, Addr 0x{addr:02X} | Accel: ({ax}, {ay}, {az}) | Gyro: ({gx}, {gy}, {gz})")
            programtime = get_program_time()
            datasend = f"{addr}, {bus_num}, {programtime}, {ax}, {ay}, {az}, {gx}, {gy}, {gz}"

            UDPMessage = sock.sendto(datasend.encode(), (UDP_IP, UDP_PORT))
            
            
        print("---")
except KeyboardInterrupt:
    print("Stopping...")