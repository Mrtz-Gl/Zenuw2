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
        
        x_len = 200         # Number of points to display
        y_range = [10, 40]  # Range of possible Y values to display
        
        fig = plt.figure()
        ax = fig.add_subplot(3, 1, 1)
        ax2 = fig.add_subplot(3, 1, 2)  # rij 2 van 3
        ax3 = fig.add_subplot(3, 1, 3)  # rij 3 van 3
        line, = ax.plot(xs, ys)
        # Subplot 1
        ax.plot([1, 2, 3], [4, 5, 6], label='Lijn A')
        ax.plot([1, 2, 3], [1, 2, 3], label='Lijn B')
        ax.plot([1, 2, 3], [6, 4, 2], label='Lijn C')
        ax.set_title('Subplot 1')
        ax.legend()

        # Subplot 2
        ax2.plot([1, 2, 3], [2, 4, 1], label='Lijn D')
        ax2.plot([1, 2, 3], [5, 3, 2], label='Lijn E')
        ax2.plot([1, 2, 3], [3, 3, 3], label='Lijn F')
        ax2.set_title('Subplot 2')
        ax2.legend()

        # Subplot 3
        ax3.plot([1, 2, 3], [1, 4, 2], label='Lijn G')
        ax3.plot([1, 2, 3], [2, 1, 3], label='Lijn H')
        ax3.plot([1, 2, 3], [3, 2, 1], label='Lijn I')
        ax3.set_title('Subplot 3')
        ax3.legend()

        xs = list(range(0, 200))
        ys = [0] * x_len
        ax.set_ylim(y_range)
        ax2.set_ylim(y_range)
        ax3.set_ylim(y_range)
        def animate(i, ys):

          # Read temperature (Celsius) from TMP102
            temp_c = round(tmp102.read_temp(), 2)

         # Add y to list
            ys.append(temp_c)

          # Limit y list to set number of items
            ys = ys[-x_len:]

          # Update line with new Y values
            line.set_ydata(ys)

            return line,

# Set up plot to call animate() function periodically
        ani = animation.FuncAnimation(fig,
            animate,
            fargs=(ys,),
            interval=50,
            blit=True)
        plt.show()

        
    
    # Stop the script with Ctrl+C
    except(KeyboardInterrupt):
        print("\n === INTERRUPTED ===")
        break
