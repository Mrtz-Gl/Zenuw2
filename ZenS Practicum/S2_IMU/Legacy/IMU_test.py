# Import necessary packages
# 1. Import the ICM20948.py file and make sure this file can be found
import sys
sys.path.insert(0, '/opt/')
from ICM20948 import *

#2. Import 'time' for time.sleep
import time

print("\nSense HAT Test Program ...\n")
icm20948=ICM20948()

while True:
    try:
        # Get the values from icm20948
        icm20948.icm20948_Gyro_Accel_Read()
        icm20948.icm20948MagRead()
        icm20948.icm20948CalAvgValue()
        time.sleep(0.1)
        q0, q1, q2, q3 = icm20948.imuAHRSupdate(MotionVal[0] * 0.0175, MotionVal[1] * 0.0175,MotionVal[2] * 0.0175,
                 MotionVal[3],MotionVal[4],MotionVal[5], 
                 MotionVal[6], MotionVal[7], MotionVal[8])      
        pitch = math.asin(-2 * q1 * q3 + 2 * q0* q2)* 57.3
        roll  = math.atan2(2 * q2 * q3 + 2 * q0 * q1, -2 * q1 * q1 - 2 * q2* q2 + 1)* 57.3
        yaw   = math.atan2(-2 * q1 * q2 - 2 * q0 * q3, 2 * q2 * q2 + 2 * q3 * q3 - 1) * 57.3

        # Print the values
        print("\r\n /-------------------------------------------------------------/ \r\n")
        print('\r\n Roll = %.2f , Pitch = %.2f , Yaw = %.2f\r\n'%(roll,pitch,yaw))
        print('\r\nAcceleration:  X = %d , Y = %d , Z = %d\r\n'%(Accel[0],Accel[1],Accel[2]))  
        print('\r\nGyroscope:     X = %d , Y = %d , Z = %d\r\n'%(Gyro[0],Gyro[1],Gyro[2]))
        print('\r\nMagnetic:      X = %d , Y = %d , Z = %d'%((Mag[0]),Mag[1],Mag[2]))
    
    # Stop the script with Ctrl+C
    except(KeyboardInterrupt):
        print("\n === INTERRUPTED ===")
        break
