# Import necessary packages
# 1. Import the ICM20948.py file and make sure this file can be found
import time
import csv
import sys
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import time
from collections import deque
import numpy as np
sys.path.insert(0, '/opt/')
from ICM20948 import *

# Constants
MAX_POINTS = 100
UPDATE_INTERVAL_MS = 100

# Buffers for time series plots. #x:0, y:1, z:2
data_buffer = {
    'Accel[0]': deque(maxlen=MAX_POINTS),
    'Accel[1]': deque(maxlen=MAX_POINTS),
    'Accel[2]': deque(maxlen=MAX_POINTS),
    'Gyro[0]': deque(maxlen=MAX_POINTS),
    'Gyro[1]': deque(maxlen=MAX_POINTS),
    'Gyro[2]': deque(maxlen=MAX_POINTS),
    'Mag[0]': deque(maxlen=MAX_POINTS),
    'Mag[1]': deque(maxlen=MAX_POINTS),
    'Mag[2]': deque(maxlen=MAX_POINTS),
}
# Set up figure and axes
fig = plt.figure(figsize=(12, 10))
gs = fig.add_gridspec(2, 2)

ax_accel = fig.add_subplot(gs[0, 0])
ax_gyro = fig.add_subplot(gs[0, 1])
ax_mag = fig.add_subplot(gs[1, 0])
ax_orientation = fig.add_subplot(gs[1, 1], projection='3d')
# Orientation reference axes

# Lines for time-series plots
lines = {}
for ax, label, keys in [
    (ax_accel, 'Acceleration (m/s²)', ['Accel[0]', 'Accel[1]', 'Accel[2]']),
    (ax_gyro, 'Gyroscope (°/s)', ['Gyro[0]', 'Gyro[1]', 'Gyro[2]']),
    (ax_mag, 'Magnetometer (µT)', ['Mag[0]', 'Mag[1]', 'Mag[2]']),
]:
    ax.set_title(label)
    ax.set_ylim(-100, 100)
    ax.set_xlim(0, MAX_POINTS)
    ax.grid(True)
    for key in keys:
        (line,) = ax.plot([], [], label=key)
        lines[key] = line
    ax.legend()
    


orientation_lines = {
    'x': ax_orientation.quiver(0, 0, 0, 1, 0, 0, color='r', label='X'),
    'y': ax_orientation.quiver(0, 0, 0, 0, 1, 0, color='g', label='Y'),
    'z': ax_orientation.quiver(0, 0, 0, 0, 0, 1, color='b', label='Z')
}
ax_orientation.set_xlim([-1, 1])
ax_orientation.set_ylim([-1, 1])
ax_orientation.set_zlim([-1, 1])
ax_orientation.set_title("Orientation (Yaw, Pitch, Roll)")
ax_orientation.set_box_aspect([1, 1, 1])
ax_orientation.legend()

sys.path.insert(0, '/opt/')

fields = ["Time", "roll", "pitch", "yaw", "AccelX", "AccelY", "AccelZ", "GyroX", "GyroY", "GyroZ", "MagX", "MagY", "MagZ"]

csvfile = open('data.csv', 'w', newline='')
csvwriter= csv.writer('data.csv')
csvwriter.writerow(fields)

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

def write_csv(programtime, imu):
    row = [programtime]
    for key, value in imu.items:
        row.append(value)
    csv.writerow(row)
    

        

def update_plot(frame):
    imu = get_imu_data()
    programtime = get_program_time()
    write_csv(programtime, imu)
    # Get the values from icm20948
    
    for i in range(3):
        data_buffer[f'Accel[{i}]'].append(imu['Accel'][i])
        data_buffer[f'Gyro[{i}]'].append(imu['Gyro'][i])
        data_buffer[f'Mag[{i}]'].append(imu['Mag'][i])

    for key, line in lines.items():
        line.set_data(range(len(data_buffer[key])), data_buffer[key])

    # Orientation update
    for artist in orientation_lines.values():
        artist.remove()
        
    roll = imu['roll']
    pitch = imu['pitch']
    yaw = imu['yaw']

    # Rotation matrices
    R_x = np.array([[1, 0, 0],
                    [0, np.cos(roll), -np.sin(roll)],
                    [0, np.sin(roll), np.cos(roll)]])

    R_y = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                    [0, 1, 0],
                    [-np.sin(pitch), 0, np.cos(pitch)]])

    R_z = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                    [np.sin(yaw), np.cos(yaw), 0],
                    [0, 0, 1]])

    R = R_z @ R_y @ R_x

    origin = np.array([[0, 0, 0]]).T
    x_axis = R @ np.array([[1, 0, 0]]).T
    y_axis = R @ np.array([[0, 1, 0]]).T
    z_axis = R @ np.array([[0, 0, 1]]).T

    orientation_lines['x'] = ax_orientation.quiver(*origin.flatten(), *x_axis.flatten(), color='r')
    orientation_lines['y'] = ax_orientation.quiver(*origin.flatten(), *y_axis.flatten(), color='g')
    orientation_lines['z'] = ax_orientation.quiver(*origin.flatten(), *z_axis.flatten(), color='b')

    return list(lines.values()) + list(orientation_lines.values())
try:
    ani = animation.FuncAnimation(fig, update_plot, interval=UPDATE_INTERVAL_MS, blit=False)
    plt.tight_layout()
    plt.show()
except(KeyboardInterrupt):
    print("\n === INTERRUPTED ===")
    csvfile.close()