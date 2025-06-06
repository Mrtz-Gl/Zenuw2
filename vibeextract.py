import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

# --- Constants ---
ACC_SENSITIVITY_LSB_PER_G = 16384
GYRO_SENSITIVITY_LSB_PER_DPS = 131
G_TO_MS2 = 9.80665
CUTOFF_FREQ = 3  # Hz

root_dir = "csv"

for patient_num in range(1, 35):
    patient_id = f"p{patient_num}"

    for intervention_type in ["no", "yes"]:
        intervention_path = os.path.join(root_dir, patient_id, f"{patient_id}{intervention_type}")

        if not os.path.exists(intervention_path):
            print(f"{intervention_path} not found, skipping...")
            continue

        subfolders = [f.path for f in os.scandir(intervention_path) if f.is_dir()]
        if not subfolders:
            print(f"No session folders in {intervention_path}, skipping...")
            continue

        for session_folder in subfolders:
            session_name = os.path.basename(session_folder)
            csv_files = glob.glob(os.path.join(session_folder, "*.csv"))
            if not csv_files:
                print(f"No CSVs found in {session_folder}, skipping...")
                continue

            for csv_path in csv_files:
                csv_filename = os.path.basename(csv_path)
                try:
                    print(f"\nProcessing: {csv_path}")
                    df = pd.read_csv(csv_path)

                    if df['programtime'].is_monotonic_decreasing:
                        df['programtime'] = df['programtime'].iloc[::-1].values
                    df['programtime'] = df['programtime'] - df['programtime'].min()

                    time_diffs = np.diff(df['programtime'])
                    fs = 1 / np.median(time_diffs)

                    b, a = butter(N=2, Wn=CUTOFF_FREQ / (0.5 * fs), btype='low')

                    df['ax_mps2'] = df['ax'] / ACC_SENSITIVITY_LSB_PER_G * G_TO_MS2
                    df['ay_mps2'] = df['ay'] / ACC_SENSITIVITY_LSB_PER_G * G_TO_MS2
                    df['az_mps2'] = df['az'] / ACC_SENSITIVITY_LSB_PER_G * G_TO_MS2

                    df['gx_dps'] = df['gx'] / GYRO_SENSITIVITY_LSB_PER_DPS
                    df['gy_dps'] = df['gy'] / GYRO_SENSITIVITY_LSB_PER_DPS
                    df['gz_dps'] = df['gz'] / GYRO_SENSITIVITY_LSB_PER_DPS

                    for axis in ['ax_mps2', 'ay_mps2', 'az_mps2', 'gx_dps', 'gy_dps', 'gz_dps']:
                        df[f'{axis}_filtered'] = filtfilt(b, a, df[axis])

                    df['acc_mag'] = np.sqrt(df['ax_mps2_filtered']**2 + df['ay_mps2_filtered']**2 + df['az_mps2_filtered']**2)

                    top_peaks_by_axis = {}
                    for axis in ['ax_mps2_filtered', 'ay_mps2_filtered', 'az_mps2_filtered']:
                        peaks, _ = find_peaks(df[axis], distance=int(fs))
                        top_4_peaks = sorted(peaks, key=lambda idx: abs(df[axis].iloc[idx]), reverse=True)[:4]
                        top_peaks_by_axis[axis] = top_4_peaks

                    last_peak_candidates = [max(peaks, key=lambda idx: df['programtime'].iloc[idx]) for peaks in top_peaks_by_axis.values() if peaks]
                    if not last_peak_candidates:
                        print("No peaks found, skipping...")
                        continue

                    last_peak_index = max(last_peak_candidates, key=lambda idx: df['programtime'].iloc[idx])
                    baseline_window_size = 200
                    baseline_start_idx = max(0, last_peak_index - baseline_window_size)
                    baseline_end_idx = last_peak_index
                    baseline_window_filtered = df.iloc[baseline_start_idx:baseline_end_idx]

                    gravity_vector = baseline_window_filtered[['ax_mps2_filtered', 'ay_mps2_filtered', 'az_mps2_filtered']].mean().values
                    gravity_vector /= np.linalg.norm(gravity_vector)

                    target_vector = np.array([0, 0, 1])
                    v = np.cross(gravity_vector, target_vector)
                    s = np.linalg.norm(v)
                    c = np.dot(gravity_vector, target_vector)
                    if s == 0:
                        rotation_matrix = np.eye(3)
                    else:
                        vx = np.array([
                            [0, -v[2], v[1]],
                            [v[2], 0, -v[0]],
                            [-v[1], v[0], 0]
                        ])
                        rotation_matrix = np.eye(3) + vx + vx @ vx * ((1 - c) / s**2)

                    acc_data = df[['ax_mps2_filtered', 'ay_mps2_filtered', 'az_mps2_filtered']].values
                    rotated_acc = acc_data @ rotation_matrix.T
                    df['ax_upright'], df['ay_upright'], df['az_upright'] = rotated_acc.T

                    gyro_data = df[['gx_dps_filtered', 'gy_dps_filtered', 'gz_dps_filtered']].values
                    rotated_gyro = gyro_data @ rotation_matrix.T
                    df['gx_upright'], df['gy_upright'], df['gz_upright'] = rotated_gyro.T

                    baseline_window = df.iloc[baseline_start_idx:baseline_end_idx]
                    baseline_time = df['programtime'].iloc[baseline_start_idx]
                    baseline_means = {axis: baseline_window[axis].mean() for axis in ['ax_upright', 'ay_upright', 'az_upright']}
                    deviation_threshold = 0.4

                    top_peaks_by_axis = {}
                    for axis in ['ax_upright', 'ay_upright', 'az_upright']:
                        peaks, _ = find_peaks(df[axis], distance=20)
                        top_4_peaks = sorted(peaks, key=lambda idx: abs(df[axis].iloc[idx]), reverse=True)[:4]
                        if top_4_peaks:
                            last_peak_idx = max(top_4_peaks, key=lambda idx: df['programtime'].iloc[idx])
                            top_peaks_by_axis[axis] = [{
                                'index': last_peak_idx,
                                'axis': axis,
                                'value': df[axis].iloc[last_peak_idx],
                                'time': df['programtime'].iloc[last_peak_idx],
                                'time_from_baseline': df['programtime'].iloc[last_peak_idx] - baseline_time
                            }]
                        else:
                            top_peaks_by_axis[axis] = []

                    last_peak_index = max([peak['index'] for peaks in top_peaks_by_axis.values() for peak in peaks])

                    stable_duration = 1.0
                    stable_window_size = int(fs * stable_duration)
                    movement_start_idx = None
                    for i in range(last_peak_index, baseline_start_idx, -1):
                        recent_window = df.iloc[i - stable_window_size + 1:i + 1] if i - stable_window_size + 1 >= 0 else None
                        if recent_window is not None and all(
                            all(abs(recent_window[axis] - baseline_means[axis]) < deviation_threshold)
                            for axis in ['ax_upright', 'ay_upright', 'az_upright']
                        ):
                            for j in range(i + 1, last_peak_index):
                                if any(abs(df.loc[j, axis] - baseline_means[axis]) > deviation_threshold for axis in ['ax_upright', 'ay_upright', 'az_upright']):
                                    movement_start_idx = j
                                    break
                            if movement_start_idx is not None:
                                break
                    if movement_start_idx is None:
                        movement_start_idx = baseline_start_idx
                    movement_start_time = df.loc[movement_start_idx, 'programtime']

                    movement_end_idx = None
                    for i in range(last_peak_index, len(df)):
                        if all(abs(df.loc[i, axis] - baseline_means[axis]) < deviation_threshold for axis in ['ax_upright', 'ay_upright', 'az_upright']):
                            movement_end_idx = i
                            break
                    if movement_end_idx is None:
                        movement_end_idx = len(df) - 1
                    movement_end_time = df.loc[movement_end_idx, 'programtime']

                    step_interval_df = df[(df['programtime'] >= movement_start_time) & (df['programtime'] <= movement_end_time)]
                    avg_acc = step_interval_df[['ax_upright', 'ay_upright', 'az_upright']].mean().to_dict()

                    refined_peaks_by_axis = {}
                    for axis in ['ax_upright', 'ay_upright', 'az_upright']:
                        baseline = baseline_means[axis]
                        deviation_series = step_interval_df[axis] - baseline
                        peaks, _ = find_peaks(np.abs(deviation_series), distance=int(fs / 2))

                        if len(peaks) > 0:
                            max_peak_idx = peaks[np.argmax(np.abs(deviation_series.iloc[peaks]))]
                            global_idx = step_interval_df.index[max_peak_idx]
                            refined_peaks_by_axis[axis] = {
                                'index': global_idx,
                                'axis': axis,
                                'value': df.loc[global_idx, axis],
                                'baseline': baseline,
                                'deviation': df.loc[global_idx, axis] - baseline,
                                'time': df.loc[global_idx, 'programtime'],
                                'time_from_baseline': df.loc[global_idx, 'programtime'] - baseline_time
                            }
                        else:
                            refined_peaks_by_axis[axis] = None

                    step_gyro_df = step_interval_df.copy()
                    gyro_max_per_axis = {}
                    for axis in ['gx_upright', 'gy_upright', 'gz_upright']:
                        max_idx = step_gyro_df[axis].abs().idxmax()
                        max_val = df.loc[max_idx, axis]
                        max_time = df.loc[max_idx, 'programtime']
                        delta_t = max_time - movement_start_time
                        gyro_max_per_axis[axis] = {
                            'value': max_val,
                            'time': max_time,
                            'time_from_step_start': delta_t
                        }

                    step_gyro_df['gyro_mag'] = np.sqrt(
                        step_gyro_df['gx_upright']**2 +
                        step_gyro_df['gy_upright']**2 +
                        step_gyro_df['gz_upright']**2
                    )
                    max_gyro_idx = step_gyro_df['gyro_mag'].idxmax()
                    max_gyro_time = df.loc[max_gyro_idx, 'programtime']
                    max_gyro_magnitude = step_gyro_df.loc[max_gyro_idx, 'gyro_mag']
                    time_from_step_start_to_max_gyro = max_gyro_time - movement_start_time

                    # === METRICS LOGGING ===
                    metrics_data = {
                        "patient_id": patient_id,
                        "intervention_type": intervention_type,
                        "session": session_name,
                        "csv_filename": csv_filename,
                        "step_duration_s": movement_end_time - movement_start_time,
                        "avg_acc_ax_upright": avg_acc.get('ax_upright', np.nan),
                        "avg_acc_ay_upright": avg_acc.get('ay_upright', np.nan),
                        "avg_acc_az_upright": avg_acc.get('az_upright', np.nan)
                    }

                    for axis in ['ax_upright', 'ay_upright', 'az_upright']:
                        peak = refined_peaks_by_axis.get(axis)
                        metrics_data[f"max_acc_{axis}"] = peak['value'] if peak else np.nan
                        metrics_data[f"time_to_max_acc_{axis}"] = peak['time_from_baseline'] if peak else np.nan

                    for axis in ['gx_upright', 'gy_upright', 'gz_upright']:
                        gyro = gyro_max_per_axis.get(axis)
                        metrics_data[f"max_ang_vel_{axis}"] = gyro['value'] if gyro else np.nan
                        metrics_data[f"time_to_max_ang_vel_{axis}"] = gyro['time_from_step_start'] if gyro else np.nan

                    metrics_df = pd.DataFrame([metrics_data])

                    # Only write if not all key metrics are zero or NaN
                    if not metrics_df.replace(0, np.nan).dropna(how='all', axis=1).empty:
                        metrics_file = "metrics_summary2.csv"
                        if not os.path.isfile(metrics_file):
                            metrics_df.to_csv(metrics_file, index=False)
                        else:
                            metrics_df.to_csv(metrics_file, mode='a', header=False, index=False)

                except Exception as e:
                    print(f"Error processing {csv_path}: {e}")
