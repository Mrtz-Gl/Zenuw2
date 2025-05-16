"""Modules for retrieving the IMU-data and writing this to a CSV-file"""
import time
import csv
import sys
import math
import socket
import time
import numpy as np

#### Dit stond niet aan. Wel nodig??
sys.path.insert(0, '/opt/')
from ICM20948 import ICM20948 # 1. Import the ICM20948.py file and make sure this file can be found
####

# create a connection with raspberry chip
hostname = '172.19.12.38' # insert IP-adress of PC
UDP_PORT = 5005 # port of raspberry chip
starttime = time.time()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create new socket object for network communication

# write data to a CSV-file
# define row of data labels 
fields = ["Time", "roll", "pitch", "yaw", "AccelX", "AccelY", "AccelZ",
           "GyroX", "GyroY", "GyroZ", "MagX", "MagY", "MagZ"]
###
# csvfile = open('data.csv', 'w', newline='')
# csvwriter= csv.writer(csvfil
# csvwriter.writerow(fields)
###

def get_imu_data():
    """retrieves data from the IMU"""

    #retrieves Gyroscopic, Magnetic data. Calculates the average values
    print(f"{get_program_time()} start")
    icm20948.icm20948_Gyro_Accel_Read()
    print(get_program_time())
    icm20948.icm20948MagRead()
    print(get_program_time())
    icm20948.icm20948CalAvgValue()
    print(get_program_time())
    
    #### gedeelte van de code die nog niet werkt...
    q0, q1, q2, q3 = icm20948.imuAHRSupdate(MotionVal[0] * 0.0175, MotionVal[1] * 0.0175,MotionVal[2] * 0.0175,
                MotionVal[3],MotionVal[4],MotionVal[5], 
                MotionVal[6], MotionVal[7], MotionVal[8]) ©ñ
    pitch = math.asin(-2 * q1 * q3 + 2 * q0* q2)* 57.3
    roll  = math.atan2(2 * q2 * q3 + 2 * q0 * q1, -2 * q1 * q1 - 2 * q2* q2 + 1)* 57.3
    yaw   = math.atan2(-2 * q1 * q2 - 2 * q0 * q3, 2 * q2 * q2 + 2 * q3 * q3 - 1) * 57.3
    return {'roll': roll,
            'pitch': pitch,
            'yaw': yaw,
            'Accel': [Accel[0],Accel[1],Accel[2]],
            'Gyro':[Gyro[0],Gyro[1],Gyro[2]]
    }
    ####

print("\nSense HAT Test Program ...\n")
icm20948 = ICM20948()

def get_program_time():
    """retrieves current duration of the program running"""
    programtime = time.time() - starttime 
    print(programtime)
    return int(programtime*1000)

def send_over_socket(programtime, imu):
    """Sends data over to the socket"""
    row = f"{programtime}"
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
            time.sleep(1)

        except(KeyboardInterrupt):
            print("\n === INTERRUPTED ===")
            break
        
main()