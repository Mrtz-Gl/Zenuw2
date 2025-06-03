import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

# --- Constants ---
ACC_SENSITIVITY_LSB_PER_G = 16384
GYRO_SENSITIVITY_LSB_PER_DPS = 250
G_TO_MS2 = 9.80665

# --- Load CSV ---
df = pd.read_csv("csv/p27/p27yes/2025-05-28_16-28-59/imu_105_0.csv")

# --- Fix time direction: only reverse 'programtime' if decreasing ---
if df['programtime'].is_monotonic_decreasing:
    df['programtime'] = df['programtime'].iloc[::-1].values

# --- Normalize time to start at 0 ---
df['programtime'] = df['programtime'] - df['programtime'].min()

# --- Convert acceleration to m/s² ---
df['ax_mps2'] = df['ax'] / ACC_SENSITIVITY_LSB_PER_G * G_TO_MS2
df['ay_mps2'] = df['ay'] / ACC_SENSITIVITY_LSB_PER_G * G_TO_MS2
df['az_mps2'] = df['az'] / ACC_SENSITIVITY_LSB_PER_G * G_TO_MS2

# --- Convert gyroscope to deg/s ---
df['gx_dps'] = df['gx'] / GYRO_SENSITIVITY_LSB_PER_DPS
df['gy_dps'] = df['gy'] / GYRO_SENSITIVITY_LSB_PER_DPS
df['gz_dps'] = df['gz'] / GYRO_SENSITIVITY_LSB_PER_DPS

# --- Convert quaternions to Euler angles ---
quaternions = df[['q0', 'q1', 'q2', 'q3']].values
rotations = R.from_quat(quaternions[:, [1, 2, 3, 0]])  # Reorder to [x, y, z, w]
euler = rotations.as_euler('xyz', degrees=True)
df['roll'], df['pitch'], df['yaw'] = euler[:, 0], euler[:, 1], euler[:, 2]

# --- Plot Acceleration ---
plt.figure(figsize=(12, 5))
plt.plot(df['programtime'], df['ax_mps2'], label='Ax (m/s²)', color='r')
plt.plot(df['programtime'], df['ay_mps2'], label='Ay (m/s²)', color='g')
plt.plot(df['programtime'], df['az_mps2'], label='Az (m/s²)', color='b')
plt.title("3-Axis Acceleration")
plt.xlabel("Time (s)")
plt.ylabel("Acceleration (m/s²)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Plot Gyroscope ---
plt.figure(figsize=(12, 5))
plt.plot(df['programtime'], df['gx_dps'], label='Gx (°/s)', color='r')
plt.plot(df['programtime'], df['gy_dps'], label='Gy (°/s)', color='g')
plt.plot(df['programtime'], df['gz_dps'], label='Gz (°/s)', color='b')
plt.title("3-Axis Gyroscope")
plt.xlabel("Time (s)")
plt.ylabel("Angular Velocity (°/s)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Plot Orientation (Euler Angles) ---
plt.figure(figsize=(12, 5))
plt.plot(df['programtime'], df['roll'], label='Roll (°)', color='c')
plt.plot(df['programtime'], df['pitch'], label='Pitch (°)', color='m')
plt.plot(df['programtime'], df['yaw'], label='Yaw (°)', color='y')
plt.title("Orientation (Euler Angles)")
plt.xlabel("Time (s)")
plt.ylabel("Angle (°)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()