from smbus2 import SMBus
import time
import socket

UDP_IP = "192.168.18.223"  # Replace with your laptop's IP
UDP_PORT = 5005
starttime = time.time()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# MPU Registers
MPU_ADDRS = [0x68, 0x69]
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# I2C Buses
i2c_buses = [0, 1]  # /dev/i2c-0 and /dev/i2c-1
mpus = []

def scan_i2c(bus_num):
    print(f"\nScanning I2C bus {bus_num}...")
    found = []
    try:
        with SMBus(bus_num) as bus:
            for addr in range(0x03, 0x77):
                try:
                    bus.read_byte(addr)
                    print(f"  Found device at 0x{addr:02X}")
                    found.append(addr)
                except:
                    continue
    except Exception as e:
        print(f"  Failed to scan I2C bus {bus_num}: {e}")
    return found

# Perform scan before initialization
for bus_num in i2c_buses:
    scan_i2c(bus_num)

# Wake up MPUs
for bus_num in i2c_buses:
    try:
        bus = SMBus(bus_num)
        for addr in MPU_ADDRS:
            try:
                bus.write_byte_data(addr, PWR_MGMT_1, 0)  # Wake up
                mpus.append((bus_num, addr))
                print(f"Initialized MPU at address 0x{addr:02X} on bus {bus_num}")
            except Exception as e:
                print(f"Failed to init MPU at 0x{addr:02X} on bus {bus_num}: {e}")
        bus.close()
    except Exception as e:
        print(f"Failed to open bus {bus_num}: {e}")

def read_word(bus, addr, reg):
    high = bus.read_byte_data(addr, reg)
    low = bus.read_byte_data(addr, reg + 1)
    val = (high << 8) + low
    if val >= 0x8000:
        val -= 0x10000
    return val

def get_program_time():
    return time.time() - starttime

buses = {bus_num: SMBus(bus_num) for bus_num, _ in mpus}

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
            programtime = get_program_time()

            datasend = f"{addr}, {bus_num}, {programtime:.3f}, {ax}, {ay}, {az}, {gx}, {gy}, {gz}"
            print(datasend)  # Add this to observe sensor data in terminal
            UDPMessage = sock.sendto(datasend.encode(), (UDP_IP, UDP_PORT))

except KeyboardInterrupt:
    print("Stopping...")

finally:
    for bus in buses.values():
        bus.close()