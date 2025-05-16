#!/usr/bin/env python3
"""
IMU_animation.py

Copy of IMU_test.py with added real-time GUI to visualize
accelerometer, gyroscope, magnetometer, and orientation data.
"""
import sys
import math
import time
from collections import deque

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
from mpl_toolkits.mplot3d import Axes3D

# Ensure the ICM20948 module can be found
sys.path.insert(0, '/opt/')
from ICM20948 import ICM20948, Accel, Gyro, Mag, MotionVal

# Constants
MAX_POINTS = 100
UPDATE_INTERVAL_MS = 100

# Data buffers for time-series plots
data_buffer = {
    'Accel[0]': deque(maxlen=MAX_POINTS),
    'Accel[1]': deque(maxlen=MAX_POINTS),
    'Accel[2]': deque(maxlen=MAX_POINTS),
    'Gyro[0]':  deque(maxlen=MAX_POINTS),
    'Gyro[1]':  deque(maxlen=MAX_POINTS),
    'Gyro[2]':  deque(maxlen=MAX_POINTS),
    'Mag[0]':   deque(maxlen=MAX_POINTS),
    'Mag[1]':   deque(maxlen=MAX_POINTS),
    'Mag[2]':   deque(maxlen=MAX_POINTS),
}

# Set up figure and subplots
fig = plt.figure(figsize=(12, 10))
gs = fig.add_gridspec(2, 2)
ax_accel = fig.add_subplot(gs[0, 0])
ax_gyro  = fig.add_subplot(gs[0, 1])
ax_mag   = fig.add_subplot(gs[1, 0])
ax_orientation = fig.add_subplot(gs[1, 1], projection='3d')

# Time-series lines setup
lines = {}
for ax, title, keys in [
    (ax_accel, 'Acceleration (m/s²)', ['Accel[0]', 'Accel[1]', 'Accel[2]']),
    (ax_gyro,  'Gyroscope (°/s)',      ['Gyro[0]',  'Gyro[1]',  'Gyro[2]']),
    (ax_mag,   'Magnetometer (µT)',    ['Mag[0]',   'Mag[1]',   'Mag[2]']),
]:
    ax.set_title(title)
    ax.set_xlim(0, MAX_POINTS)
    ax.set_ylim(-3000, 3000)
    ax.grid(True)
    for key in keys:
        line, = ax.plot([], [], label=key)
        lines[key] = line
    ax.legend()

# Orientation axes limits and aspect
# Define yaw/pitch/roll limits
x_min, x_max = -180, 180
y_min, y_max = -180, 180
z_min, z_max = -180, 180
ax_orientation.set_xlim(x_min, x_max)
ax_orientation.set_ylim(y_min, y_max)
ax_orientation.set_zlim(z_min, z_max)
ax_orientation.set_title("Orientation (Yaw, Pitch, Roll)")
# Compute spans
dx = x_max - x_min
dy = y_max - y_min
dz = z_max - z_min
# Ensure equal physical scaling for each axis
ax_orientation.set_box_aspect((dx, dy, dz))
# Determine arrow length as 30% of the largest half-span
arrow_length = 0.3 * max(dx, dy, dz) / 2

# Initial reference quivers (will be overwritten in update)
orientation_lines = {
    'x': ax_orientation.quiver(0, 0, 0, 1, 0, 0,
                                length=arrow_length, normalize=True, color='r', label='X'),
    'y': ax_orientation.quiver(0, 0, 0, 0, 1, 0,
                                length=arrow_length, normalize=True, color='g', label='Y'),
    'z': ax_orientation.quiver(0, 0, 0, 0, 0, 1,
                                length=arrow_length, normalize=True, color='b', label='Z')
}
ax_orientation.legend()

# Insert IMU path again
sys.path.insert(0, '/opt/')

def get_imu_data():
    """Read sensors, update AHRS, return dict with roll, pitch, yaw, accel, gyro, mag."""
    icm.icm20948_Gyro_Accel_Read()
    icm.icm20948MagRead()
    icm.icm20948CalAvgValue()

    # AHRS quaternion update
    q0, q1, q2, q3 = icm.imuAHRSupdate(
        MotionVal[0] * 0.0175, MotionVal[1] * 0.0175, MotionVal[2] * 0.0175,
        MotionVal[3], MotionVal[4], MotionVal[5],
        MotionVal[6], MotionVal[7], MotionVal[8]
    )
    # Euler angles conversion
    pitch = math.asin(-2 * q1 * q3 + 2 * q0 * q2) * 57.3
    roll  = math.atan2(2 * q2 * q3 + 2 * q0 * q1,
                       -2 * q1 * q1 - 2 * q2 * q2 + 1) * 57.3
    yaw   = math.atan2(-2 * q1 * q2 - 2 * q0 * q3,
                       2 * q2 * q2 + 2 * q3 * q3 - 1) * 57.3

    return {
        'roll': roll, 'pitch': pitch, 'yaw': yaw,
        'Accel': [Accel[0], Accel[1], Accel[2]],
        'Gyro':  [Gyro[0],  Gyro[1],  Gyro[2]],
        'Mag':   [Mag[0],   Mag[1],   Mag[2]],
    }

# Initialize IMU sensor
print("\nSense HAT Test Program ...\n")
icm = ICM20948()

def update_plot(frame):
    global orientation_lines
    imu = get_imu_data()

    # Update time-series buffers
    for i in range(3):
        data_buffer[f'Accel[{i}]'].append(imu['Accel'][i])
        data_buffer[f'Gyro[{i}]'].append(imu['Gyro'][i])
        data_buffer[f'Mag[{i}]'].append(imu['Mag'][i])

    # Update time-series lines
    for key, line in lines.items():
        line.set_data(range(len(data_buffer[key])), data_buffer[key])

    # Remove old orientation arrows
    for art in orientation_lines.values():
        art.remove()

    # Compute rotation matrix
    roll, pitch, yaw = imu['roll'], imu['pitch'], imu['yaw']
    R_x = np.array([[1, 0, 0],
                    [0, np.cos(roll), -np.sin(roll)],
                    [0, np.sin(roll),  np.cos(roll)]])
    R_y = np.array([[ np.cos(pitch), 0, np.sin(pitch)],
                    [0, 1, 0],
                    [-np.sin(pitch), 0, np.cos(pitch)]])
    R_z = np.array([[ np.cos(yaw), -np.sin(yaw), 0],
                    [ np.sin(yaw),  np.cos(yaw), 0],
                    [0, 0, 1]])
    R = R_z @ R_y @ R_x

    # Plot new orientation quivers
    origin = np.zeros(3)
    axes_vecs = {
        'x': R @ np.array([1, 0, 0]),
        'y': R @ np.array([0, 1, 0]),
        'z': R @ np.array([0, 0, 1])
    }
    for key, vec in axes_vecs.items():
        orientation_lines[key] = ax_orientation.quiver(
            *origin, *vec,
            length=arrow_length,
            normalize=True
        )

    # Return all artists for animation
    return list(lines.values()) + list(orientation_lines.values())

# Start animation
ani = animation.FuncAnimation(
    fig, update_plot,
    interval=UPDATE_INTERVAL_MS,
    blit=False
)
plt.tight_layout()
plt.show()
