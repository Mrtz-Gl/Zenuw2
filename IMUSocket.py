# Import necessary packages
# 1. Import the ICM20948.py file and make sure this file can be found
import time
import csv
import sys
import math
import socket
import time
import numpy as np
sys.path.insert(0, '/opt/')
from ICM20948 import *

UDP_IP = "172.19.12.67"  # Replace with your laptop's IP
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

fields = ["Time", "roll", "pitch", "yaw", "AccelX", "AccelY", "AccelZ", "GyroX", "GyroY", "GyroZ", "MagX", "MagY", "MagZ"]

# csvfile = open('data.csv', 'w', newline='')
# csvwriter= csv.writer(csvfile)
# csvwriter.writerow(fields)

def get_imu_data():
    icm20948.icm20948_Gyro_Accel_Read()
    icm20948.icm20948MagRead()
    icm20948.icm20948CalAvgValue()
    
    q0, q1, q2, q3 = icm20948.imuAHRSupdate(MotionVal[0] * 0.0175, MotionVal[1] * 0.0175,MotionVal[2] * 0.0175,
                MotionVal[3],MotionVal[4],MotionVal[5], 
                MotionVal[6], MotionVal[7], MotionVal[8])      
    pitch = math.asin(-2 * q1 * q3 + 2 * q0* q2)* 57.3
    roll  = math.atan2(2 * q2 * q3 + 2 * q0 * q1, -2 * q1 * q1 - 2 * q2* q2 + 1)* 57.3
    yaw   = math.atan2(-2 * q1 * q2 - 2 * q0 * q3, 2 * q2 * q2 + 2 * q3 * q3 - 1) * 57.3
    return {'roll': roll,
            'pitch': pitch,
            'yaw': yaw,
            'Accel': [Accel[0],Accel[1],Accel[2]],
            'Gyro':[Gyro[0],Gyro[1],Gyro[2]],
            'Mag': [Mag[0],Mag[1],Mag[2]]}

print("\nSense HAT Test Program ...\n")
icm20948=ICM20948()

def get_program_time():
    starttime = time.time()
    programtime = starttime - time.time()
    return programtime

def send_over_socket(programtime, imu):
    
    row = f"p{programtime}"
    for key, value in imu.items():
        row += f", {value}"
    print(row)
    UDPMessage = sock.sendto(row.encode(), (UDP_IP, UDP_PORT))
    
    

    
def main():
    while(True):
        try:
            imu = get_imu_data()
            programtime = get_program_time()
            send_over_socket(programtime, imu)
            time.sleep(0.01)

        except(KeyboardInterrupt):
            print("\n === INTERRUPTED ===")
            break
        
main()