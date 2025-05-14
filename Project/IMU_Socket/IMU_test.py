# Import necessary packages
# 1. Import the ICM20948.py file and make sure this file can be found

import sys
sys.path.insert(0, '/opt/')
from ICM20948 import *
from matplotlib import pyplot
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
        ax = fig.add_subplot(4, 1, 1)
        ax2 = fig.add_subplot(4, 1, 2)  # rij 2 van 3
        ax3 = fig.add_subplot(4, 1, 3)  # rij 3 van 3
        ax4 = fig.add_subplot(4, 1, 4)

        xs = list(range(0, 200))
        ys1 = [0] * x_len
        ys2 = [0] * x_len
        ys3 = [0] * x_len
        ys4 = [0] * x_len
        ys5 = [0] * x_len
        ys6 = [0] * x_len
        ys7 = [0] * x_len
        ys8 = [0] * x_len
        ys9 = [0] * x_len
        ys10 = [0] * x_len
        ys11 = [0] * x_len
        ys12 = [0] * x_len

        line_acc_x, = ax.plot(xs, ys1, label='acc_x')
        line_acc_y, = ax.plot(xs, ys2, label='acc_y')
        line_acc_z, = ax.plot(xs, ys3, label='acc_z')

        line_pitch, = ax2.plot(xs, ys4, label='pitch')
        line_roll, = ax2.plot(xs, ys5, label='roll')
        line_yaw, = ax2.plot(xs, ys6, label='yaw')

        line_mag_x, = ax3.plot(xs, ys7, label='mag_x')
        line_mag_y, = ax3.plot(xs, ys8, label='mag_y')
        line_mag_z, = ax3.plot(xs, ys9, label='mag_z')

        line_gyro_x, = ax4.plot(xs, ys10, label='gyro_x')
        line_gyro_y, = ax4.plot(xs, ys11, label='gyro_y')
        line_gyro_z, = ax4.plot(xs, ys12, label='gyro_z')
        ax.set_ylim(y_range)
        ax2.set_ylim(y_range)
        ax3.set_ylim(y_range)
        ax4.set_ylim(y_range)
        def animate(i):
            # Add y to list
            ys1.append(Accel[0])
            ys1[:] = ys1[-x_len:]
            line_acc_x.set_ydata(ys1)

            ys2.append(Accel[1])
            ys2[:] = ys2[-x_len:]
            line_acc_y.set_ydata(ys2)

            ys3.append(Accel[2])
            ys3[:] = ys3[-x_len:]
            line_acc_z.set_ydata(ys3)

            ys4.append(pitch)
            ys4[:] = ys4[-x_len:]
            line_pitch.set_ydata(ys4)

            ys5.append(roll)
            ys5[:] = ys5[-x_len:]
            line_roll.set_ydata(ys5)

            ys6.append(yaw)
            ys6[:] = ys6[-x_len:]
            line_yaw.set_ydata(ys6)

            ys7.append(Mag[0])
            ys7[:] = ys7[-x_len:]
            line_mag_x.set_ydata(ys7)

            ys8.append(Mag[1])
            ys8[:] = ys8[-x_len:]
            line_mag_y.set_ydata(ys8)

            ys9.append(Mag[2])
            ys9[:] = ys9[-x_len:]
            line_mag_z.set_ydata(ys9)

            ys10.append(Gyro[0])
            ys10[:] = ys10[-x_len:]
            line_gyro_x.set_ydata(ys10)

            ys11.append(Gyro[1])
            ys11[:] = ys11[-x_len:]
            line_gyro_y.set_ydata(ys11)

            ys12.append(Gyro[2])
            ys12[:] = ys12[-x_len:]
            line_gyro_z.set_ydata(ys12)

            return line_acc_x, line_acc_y, line_acc_z, line_pitch, line_roll, line_yaw, line_mag_x, line_mag_y, line_mag_z, line_gyro_x, line_gyro_y, line_gyro_z,

            # Set up plot to call animate() function periodically
        ani = animation.FuncAnimation(fig,
            animate,
            interval=50,
            blit=True)
        plt.show()

        
    
    # Stop the script with Ctrl+C
    except(KeyboardInterrupt):
        print("\n === INTERRUPTED ===")
        break
